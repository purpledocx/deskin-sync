import { useState, useEffect } from "react";
import { getBookings, cancelBooking } from "../api/bookings";
import { getUser, canViewAll } from "../api/session";
import { parseApiDate, formatDateTime } from "../api/dates";
import { getAvailability } from "../api/spaces";
import ConfirmCancelModal from "../components/modals/ConfirmCancelModal";
import EditBookingModal from "../components/modals/EditBookingModal";
import SpaceDetailsModal from "../components/modals/SpaceDetailsModal";

const MIN_BEFORE_CHANGE = 30 * 60 * 1000; // same rule as backend
const LOCK_HINT = "Changes and cancellations are not possible within 30 minutes of the start.";

// cancelled | finished | locked (<30 min to start) | open
const bookingState = (b) => {
  if (b.status === "cancelled") return "cancelled";
  const now = Date.now();
  if (parseApiDate(b.end_at) < now) return "finished";
  if (parseApiDate(b.start_at) - now < MIN_BEFORE_CHANGE) return "locked";
  return "open";
};

const STATUS_LABEL = { open: "Active", locked: "Active", finished: "Finished", cancelled: "Cancelled" };

export default function MyBookingsPage() {
  const user = getUser();
  const showToggle = canViewAll(user);

  const [bookings, setBookings] = useState(null); // null -> loading
  const [viewAll, setViewAll] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [refresh, setRefresh] = useState(0);

  // cancel modal state
  const [toCancel, setToCancel] = useState(null);
  const [busy, setBusy] = useState(false);
  const [cancelError, setCancelError] = useState("");

  // edit modal state
  const [toEdit, setToEdit] = useState(null);

  const [details, setDetails] = useState(null);

  useEffect(() => {
    let ignore = false;
    getBookings()
      .then((data) => {
        if (ignore) return;
        setBookings(data);
        setError("");
      })
      .catch((err) => {
        if (!ignore) setError(err.message);
      });
    return () => {
      ignore = true;
    };
  }, [refresh]);

  const showAll = showToggle && viewAll;
  const rows = showAll ? bookings : bookings?.filter((b) => b.user_id === user.id);

  const openCancel = (b) => {
    setNotice("");
    setCancelError("");
    setToCancel(b);
  };

  const confirmCancel = async () => {
    setBusy(true);
    setCancelError("");
    try {
      const updated = await cancelBooking(toCancel.id);
      setBookings((list) => list.map((b) => (b.id === updated.id ? updated : b)));
      setNotice(`Booking for ${updated.space_name} was cancelled.`);
      setToCancel(null);
    } catch (err) {
      setCancelError(err.message);
      if (err.status === 409) setRefresh((n) => n + 1); // data is stale -> reload
    } finally {
      setBusy(false);
    }
  };

  const handleSaved = (updated) => {
    setBookings((list) =>
      list
        .map((b) => (b.id === updated.id ? updated : b))
        .sort((a, b) => parseApiDate(a.start_at) - parseApiDate(b.start_at))
    );
    setNotice(`Booking for ${updated.space_name} was updated.`);
    setToEdit(null);
  };

  const seg = (active) =>
    `px-4 py-2 text-[13px] transition-colors ${
      active ? "bg-navy font-semibold text-white" : "bg-white text-chip hover:bg-surface"
    }`;

  return (
    <main className="mx-auto max-w-5xl p-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-semibold leading-[1.15] text-navy">
            {showAll ? "All bookings" : "My bookings"}
          </h1>
          <div className="mb-6 mt-3 h-0.75 w-36 bg-gold" />
        </div>

        {showToggle && (
          <div className="mb-6 flex overflow-hidden rounded-form border border-line">
            <button onClick={() => setViewAll(false)} className={seg(!viewAll)}>My bookings</button>
            <button onClick={() => setViewAll(true)} className={seg(viewAll)}>All bookings</button>
          </div>
        )}
      </div>

      {error && (
        <div className="mb-4 rounded-form border border-bad bg-bad-soft px-3 py-2 text-sm text-bad-ink">{error}</div>
      )}
      {notice && (
        <div className="mb-4 rounded-form border border-ok bg-ok-soft px-3 py-2 text-sm text-ok-ink">{notice}</div>
      )}
      {bookings === null && !error && <p className="text-muted">Loading...</p>}
      {rows?.length === 0 && <p className="text-muted">No bookings yet.</p>}

      {rows?.length > 0 && (
        <div className="overflow-x-auto rounded-form border border-line bg-white shadow-soft">
          <table className="w-full min-w-160 border-collapse text-sm text-center">
            <thead>
              <tr className="border-b border-line text-xs font-semibold uppercase text-muted">
                {showAll && <th className="px-4 py-3">Booking ID</th>}
                <th className="px-4 py-3">Space</th>
                {showAll && <th className="px-4 py-3">User</th>}
                <th className="px-4 py-3">Start</th>
                <th className="px-4 py-3">End</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((b) => {
                const st = bookingState(b);
                return (
                  <tr key={b.id} className="border-b border-line/60 last:border-0 hover:bg-surface">
                    {showAll && <td className="px-4 py-4 text-muted text-center text-xl">{b.id}</td>}
                    
                    <td className="px-4 py-4 font-semibold">
                      <div className="flex flex-col items-center gap-1">
                        <span>{b.space_name}</span>
                        <button
                          type="button"
                          onClick={async () => {
                            try {
                              // request availability to get all info of booking
                              const dayStart = new Date(b.start_at);
                              dayStart.setHours(0, 0, 0, 0);
                              const dayEnd = new Date(dayStart);
                              dayEnd.setDate(dayEnd.getDate() + 1);

                              const spaces = await getAvailability(dayStart, dayEnd);
                              const fullSpace = spaces.find((s) => s.id === b.space_id);

                              setDetails({
                                ...b,
                                // if full space - data from it : fallback on booking
                                category: fullSpace?.category || "",
                                capacity: fullSpace?.capacity ?? 0,
                                facilities: fullSpace?.facilities || [],
                              });
                            } catch {
                              setDetails(b);
                            }
                          }}
                          className="text-xs font-medium text-navy underline cursor-pointer"
                        >
                          Details
                        </button>
                      </div>
                    </td>

                    {showAll && <td className="px-4 py-4">{b.user_name}</td>}
                    <td className="px-4 py-4">{formatDateTime(b.start_at)}</td>
                    <td className="px-4 py-4">{formatDateTime(b.end_at)}</td>
                    <td className="px-4 py-4">
                      <span className={`badge ${st === "open" || st === "locked" ? "badge-ok" : "bg-disabled-bg text-chip"}`}>
                        {STATUS_LABEL[st]}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      {st === "open" && (
                        <div className="flex justify-center gap-2">
                          <button
                            onClick={() => {
                              setNotice("");
                              setToEdit(b);
                            }}
                            className="btn btn-secondary h-9"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => openCancel(b)}
                            className="btn btn-secondary h-9 border-cancel text-cancel hover:bg-bad-soft"
                          >
                            Cancel
                          </button>
                        </div>
                      )}
                      {st === "locked" && (
                        <span className="group relative inline-flex gap-2">
                          <button disabled className="btn btn-secondary h-9">Edit</button>
                          <button disabled className="btn btn-secondary h-9">Cancel</button>
                          <span className="pointer-events-none absolute bottom-full right-0 z-10 mb-2 hidden w-64 rounded bg-ink px-3 py-2 text-xs text-white group-hover:block">
                            {LOCK_HINT}
                          </span>
                        </span>
                      )}
                      {(st === "cancelled" || st === "finished") && <span className="text-disabled">-</span>}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {toCancel && (
        <ConfirmCancelModal
          spaceName={toCancel.space_name}
          when={`${formatDateTime(toCancel.start_at)}\n${formatDateTime(toCancel.end_at)}`}
          loading={busy}
          error={cancelError}
          onClose={() => setToCancel(null)}
          onConfirm={confirmCancel}
        />
      )}

      {toEdit && (
        <EditBookingModal booking={toEdit} onClose={() => setToEdit(null)} onSaved={handleSaved} />
      )}

      {details && (
        <SpaceDetailsModal
          key={details.id}
          space={{
            id: details.space_id || details.space?.id || details.id,
            name: details.space_name || details.space?.name || details.name,
            category: details.space_category || details.category || details.space?.category || "",
            capacity: details.space_capacity ?? details.capacity ?? details.space?.capacity ?? 0,
            facilities: details.space_facilities || details.facilities || details.space?.facilities || []
          }}
          day={details.start_at}
          onClose={() => setDetails(null)}
        />
      )}
    </main>
  );
}