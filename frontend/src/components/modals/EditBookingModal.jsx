import { useState, useEffect } from "react";
import { updateBooking } from "../../api/bookings";
import { getAvailability } from "../../api/spaces";
import { parseApiDate, toLocalInput } from "../../api/dates";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

export default function EditBookingModal({ booking, onClose, onSaved }) {

  const initStart = toLocalInput(parseApiDate(booking.start_at));
  const initEnd = toLocalInput(parseApiDate(booking.end_at));

  const [spaces, setSpaces] = useState([]);
  const [spaceId, setSpaceId] = useState(booking.space_id);
  
  const [start, setStart] = useState(initStart);
  const [end, setEnd] = useState(initEnd);
  

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // list of active spaces for selec
  useEffect(() => {
    let ignore = false;
    getAvailability(parseApiDate(booking.start_at), parseApiDate(booking.end_at))
      .then((data) => {
        if (!ignore) setSpaces(data);
      })
      .catch(() => {}); // select still works with current space
    return () => {
      ignore = true;
    };
  }, [booking]);

  // current space must always be an option (it may be inactive now)
  const options = spaces.some((s) => s.id === booking.space_id)
    ? spaces
    : [{ id: booking.space_id, name: booking.space_name }, ...spaces];

  const changed = Number(spaceId) !== booking.space_id || start !== initStart || end !== initEnd;

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (start >= end) return setError("Start time must be earlier than end time!");
    if (new Date(start) < new Date()) return setError("Start time can not be in the past.");

    setLoading(true);
    try {
      const updated = await updateBooking(booking.id, { spaceId: Number(spaceId), start, end });
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

  const changeStart = (d) => {
  if (!d) return;
  setStart(toLocalInput(d));
  // keep the range valid: if the new start is not before the end, move the end 1h after it
  if (d >= new Date(end)) setEnd(toLocalInput(new Date(d.getTime() + 60 * 60 * 1000)));
    };

  const changeEnd = (d) => {
  if (d) setEnd(toLocalInput(d));
  };

  return (
    <div onClick={onClose} className="fixed inset-0 z-10 flex items-center justify-center bg-black/40 p-4">
      <form
        onSubmit={submit}
        onClick={(e) => e.stopPropagation()}
        className="flex w-full max-w-md flex-col gap-4 rounded-form bg-white p-6 shadow-hover"
      >
        <h2 className="text-2xl font-semibold text-navy">Edit booking</h2>

        <label className="flex flex-col gap-1 font-medium">
          Space
          <select className="field" value={spaceId} onChange={(e) => setSpaceId(e.target.value)}>
            {options.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </label>
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
            onChange={changeEnd}
            minDate={new Date(start)}
            showTimeSelect
            timeIntervals={30}
            dateFormat="dd.MM.yyyy HH:mm"
            className="field"
            wrapperClassName="w-full"
            popperPlacement="bottom-start"
        />
        </label>

        <p className="text-sm text-muted">You can change a booking until 30 minutes before it starts.</p>

        {error && (
          <div className="rounded-form border border-bad bg-bad-soft px-3 py-2 text-sm text-bad-ink">{error}</div>
        )}

        <div className="flex gap-3">
          <button type="button" onClick={onClose} className="btn btn-secondary flex-1">Cancel</button>
          <button disabled={loading || !changed} className="btn btn-primary flex-1">
            {loading ? "Saving..." : "Save changes"}
          </button>
        </div>
      </form>
    </div>
  );
}