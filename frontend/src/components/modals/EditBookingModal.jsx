import { useState } from "react";
import { updateBooking } from "../../api/bookings";
import { parseApiDate, toLocalInput } from "../../api/dates";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

export default function EditBookingModal({ booking, onClose, onSaved }) {
  const initStart = toLocalInput(parseApiDate(booking.start_at));
  const initEnd = toLocalInput(parseApiDate(booking.end_at));

  const [start, setStart] = useState(initStart);
  const [end, setEnd] = useState(initEnd);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const changed = start !== initStart || end !== initEnd;

  const submit = async (e) => {
    e.preventDefault();
    setError("");

    if (start >= end) {
      return setError("Start time must be earlier than end time!");
    }

    if (new Date(start) < new Date()) {
      return setError("Start time can not be in the past.");
    }

    setLoading(true);
    try {
      const updated = await updateBooking(booking.id, {
        spaceId: booking.space_id,
        start,
        end,
      });
      onSaved(updated);
    } catch (err) {
      setError(
        [400, 404, 409, 422].includes(err.status)
          ? err.message
          : err.status === 0
            ? "Server is unreachable"
            : "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const changeStart = (date) => {
    if (!date) return;

    setStart(toLocalInput(date));
    if (date >= new Date(end)) {
      setEnd(toLocalInput(new Date(date.getTime() + 60 * 60 * 1000)));
    }
  };

  return (
    <div onClick={onClose} className="fixed inset-0 z-10 flex items-center justify-center bg-black/40 p-4">
      <form
        onSubmit={submit}
        onClick={(e) => e.stopPropagation()}
        className="flex w-full max-w-md flex-col gap-4 rounded-form bg-white p-6 shadow-hover"
      >
        <h2 className="text-2xl font-semibold text-navy">
          Edit booking — {booking.space_name}
        </h2>

        <label className="flex flex-col gap-1 font-medium">
          From
          <DatePicker
            selected={new Date(start)}
            onChange={changeStart}
            minDate={new Date()}
            showTimeSelect
            timeIntervals={30}
            dateFormat="dd.MM.yyyy HH:mm"
            className="field"
            wrapperClassName="w-full"
            popperPlacement="bottom-start"
          />
        </label>

        <label className="flex flex-col gap-1 font-medium">
          Till
          <DatePicker
            selected={new Date(end)}
            onChange={(date) => date && setEnd(toLocalInput(date))}
            minDate={new Date(start)}
            showTimeSelect
            timeIntervals={30}
            dateFormat="dd.MM.yyyy HH:mm"
            className="field"
            wrapperClassName="w-full"
            popperPlacement="bottom-start"
          />
        </label>

        {error && (
          <div className="rounded-form border border-bad bg-bad-soft px-3 py-2 text-sm text-bad-ink">
            {error}
          </div>
        )}

        <div className="flex gap-3">
          <button type="button" onClick={onClose} className="btn btn-secondary flex-1">
            Cancel
          </button>
          <button disabled={loading || !changed} className="btn btn-primary flex-1">
            {loading ? "Saving..." : "Save changes"}
          </button>
        </div>
      </form>
    </div>
  );
}