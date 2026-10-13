import { useState } from "react"
import DatePicker from "react-datepicker"

import { createBooking } from "../../api/bookings"
import { toLocalInput } from "../../api/dates"

import "react-datepicker/dist/react-datepicker.css"

export default function BookingModal({ space, start: s0, end: e0, onClose, onBooked }) {
    const [start, setStart] = useState(s0)
    const [end, setEnd] = useState(e0)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")

    const changeStart = (date) => {
        if (!date) return

        setStart(toLocalInput(date))

        if (date >= new Date(end)) {
            setEnd(toLocalInput(new Date(date.getTime() + 60 * 60 * 1000)))
        }
    }

    const changeEnd = (date) => {
        if (date) setEnd(toLocalInput(date))
    }

    const submit = async (e) => {
        e.preventDefault()
        setError("")

        if (start >= end) {
            setError("Start time must be earlier than end time!")
            return
        }

        if (new Date(start) < new Date()) {
            setError("Start time cannot be in the past.")
            return
        }

        setLoading(true)

        try {
            await createBooking({ spaceId: space.id, start, end })
            onBooked(space.name)
        } catch (err) {
            setError(
                [400, 404, 409, 422].includes(err.status)
                    ? err.message
                    : err.status === 0
                        ? "Server-side is unreachable"
                        : "Something went wrong :( Please try again"
            )
        } finally {
            setLoading(false)
        }
    }

    return (
        <div onClick={onClose} className="fixed inset-0 z-10 flex items-center justify-center bg-black/40 p-4">
            <form
                onSubmit={submit}
                onClick={(e) => e.stopPropagation()}
                className="flex w-full max-w-md flex-col gap-4 rounded-form bg-white p-6 shadow-lg"
            >
                <h2 className="text-navy text-2xl font-semibold">Book {space.name}</h2>
                <p className="text-muted">
                    {space.category} | {space.capacity} {space.capacity === 1 ? "seat" : "seats"}
                </p>

                <label className="flex flex-col gap-1 font-medium">
                    From
                    <DatePicker
                        selected={start ? new Date(start) : null}
                        onChange={changeStart}
                        minDate={new Date()}
                        showTimeSelect
                        timeIntervals={30}
                        dateFormat="dd.MM.yyyy HH:mm"
                        className="field"
                        wrapperClassName="w-full"
                        popperPlacement="bottom-start"
                        required
                    />
                </label>

                <label className="flex flex-col gap-1 font-medium">
                    Till
                    <DatePicker
                        selected={end ? new Date(end) : null}
                        onChange={changeEnd}
                        minDate={start ? new Date(start) : new Date()}
                        showTimeSelect
                        timeIntervals={30}
                        dateFormat="dd.MM.yyyy HH:mm"
                        className="field"
                        wrapperClassName="w-full"
                        popperPlacement="bottom-start"
                        required
                    />
                </label>

                {error && (
                    <div className="rounded-form border border-bad bg-bad-soft px-3 py-2 text-sm text-bad-ink">
                        {error}
                    </div>
                )}

                <div className="flex gap-3">
                    <button
                        type="button"
                        onClick={onClose}
                        className="h-11 flex-1 rounded-md border border-line font-medium transition-colors duration-200 ease-in-out hover:bg-surface"
                    >
                        Cancel
                    </button>
                    <button
                        disabled={loading}
                        className="h-11 flex-1 rounded-md bg-navy font-medium text-white transition-colors duration-200 ease-in-out hover:bg-steel disabled:opacity-60"
                    >
                        {loading ? "Booking..." : "Confirm booking"}
                    </button>
                </div>
            </form>
        </div>
    )
}