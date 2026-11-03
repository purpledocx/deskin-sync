import { useEffect, useState } from "react"
import { getSpaceBookings } from "../../api/spaces"
import { parseApiDate } from "../../api/dates"

const pad = (n) => String(n).padStart(2, "0")

const hhmm = (iso) => {
  const d = parseApiDate(iso)
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`
}

export default function SpaceDetailsModal({ space, day, onClose }) {

  const [slots, setSlots] = useState(null)
  const [error, setError] = useState("")

  const parsedDay = day ? parseApiDate(day) : new Date()
  const validDate = !isNaN(parsedDay?.getTime()) ? parsedDay : new Date()

  const dayLabel = `${pad(validDate.getDate())}.${pad(validDate.getMonth() + 1)}.${validDate.getFullYear()}`
  const facilities = Array.isArray(space?.facilities) ? space.facilities : []

  useEffect(() => {
    if (!space || !day) return;
    
    let ignore = false

    const baseDate = parseApiDate(day)
    const from = new Date(baseDate)
    from.setHours(0, 0, 0, 0)

    const till = new Date(from)
    till.setDate(till.getDate() + 1)


    getSpaceBookings(space.id, from, till)
      .then((data) => {
        if (!ignore) setSlots(Array.isArray(data) ? data : [])
      })
      .catch((err) => {
        if (!ignore) setError(err.message || "Could not load bookings")
      })

    return () => {
      ignore = true
    }
  }, [space, day])

  if (!space) return null;

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-10 flex items-center justify-center bg-black/40 p-4"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="flex w-full max-w-md flex-col gap-4 rounded-form bg-white p-6 shadow-hover"
      >
        <div className="flex items-start justify-between gap-2">
          <h2 className="text-2xl font-semibold text-navy">{space.name}</h2>
          <span className="chip">{space.category}</span>
        </div>

        <p className="text-sm text-muted">
          {space.capacity} {space.capacity === 1 ? "seat" : "seats"}
        </p>

        {facilities.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {facilities.map((f) => (
              <span key={f} className="chip">{f}</span>
            ))}
          </div>
        )}

        <div>
          <h3 className="mb-2 font-semibold text-navy">
            Availability on {dayLabel}
          </h3>

          {error && (
            <div className="rounded-form border border-bad bg-bad-soft px-3 py-2 text-sm text-bad-ink">
              {error}
            </div>
          )}

          {!error && slots === null && (
            <p className="text-sm text-muted">Loading...</p>
          )}

          {!error && slots?.length === 0 && (
            <div className="rounded-form border border-ok bg-ok-soft px-3 py-2 text-sm text-ok-ink">
              Available all day
            </div>
          )}

          {!error && slots?.length > 0 && (
            <>
              <p className="mb-2 text-sm text-muted">Booked time slots:</p>

              <ul className="flex flex-col gap-1">
                {slots.map((s, i) => (
                  <li
                    key={i}
                    className="rounded-form bg-bad-soft px-3 py-2 text-sm text-bad-ink"
                  >
                    {hhmm(s.start_at)} – {hhmm(s.end_at)}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>

        <button
          type="button"
          onClick={onClose}
          className="btn btn-secondary"
        >
          Close
        </button>
      </div>
    </div>
  )
}