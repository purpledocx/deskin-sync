import { useEffect, useState } from "react"
import { getAvailability } from "../api/spaces"
import BookingModal from "../components/modals/BookingModal"
import SpaceDetailsModal from "../components/modals/SpaceDetailsModal"
import DatePicker from "react-datepicker"
import "react-datepicker/dist/react-datepicker.css"


// ----------------------------------------------------FUNCTIONS----------------------------------------------------


// 8 -> 08
const pad = (n) => String(n).padStart(2, "0")

// date object to YYYY-MM-DD-THH:mm for html datetime input
const toLocalInput = (d) => {
    if (!d) return ""
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const formatDT = (iso) => {
    const d = new Date(iso)
    return `${pad(d.getDate())}.${pad(d.getMonth() + 1)} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function defaultRange() {

    // default range time to closest half hour + 1hr end time
    const start = new Date()
    start.setMinutes(start.getMinutes() < 30 ? 30 : 60, 0, 0)

    const end = new Date(start.getTime() + 60 * 60 * 1000)

    return [toLocalInput(start), toLocalInput(end)]
}


// ----------------------------------------------------DASHBOARD-PAGE----------------------------------------------------
export default function DashboardPage() {

    const [[start, end], setRange] = useState(defaultRange)
    const invalid = !start || !end || start >= end
    const isPast = !invalid && new Date(start) < new Date() // selected start is already gone -> booking impossible

    const [spaces, setSpaces] = useState(null) // list of spaces from backend | null -> loading
    const [error, setError] = useState("")

    // BookingModal states
    const [booking, setBooking] = useState(null)
    const [details, setDetails] = useState(null)
    const [refresh, setRefresh] = useState(0)
    const [notice, setNotice] = useState("")


    useEffect(() => {
        if (invalid) {
            setSpaces(null)
            return
        }

        let ignore = false // flag to fix race conditions when user clicks fast

        getAvailability(start, end)
            .then((data) => {
                if (ignore) return
                setSpaces(Array.isArray(data) ? data : [])
                setError("")
            })
            .catch((err) => {
                if (!ignore) {
                    setSpaces([])
                    setError(err.message || "Could not load spaces")
                }
            })

        return () => {
            ignore = true
        }
    }, [start, end, invalid, refresh]) //rerun whenever start, end or validity changes


    return (
        <>
            <main className="max-w-6xl mx-auto p-6">
                <h1 className="text-4xl text-navy font-semibold mb-4">Space availability</h1>

                <div className="bg-white flex flex-wrap border border-line rounded-form gap-4 mb-6 p-4">
                    <label className="flex flex-col font-medium">
                        From
                        <DatePicker
                            selected={start ? new Date(start) : null}
                            onChange={(d) => d && setRange([toLocalInput(d), end])}
                            showTimeSelect
                            timeIntervals={30}
                            dateFormat="dd.MM.yyyy HH:mm"
                            className="field"
                        />
                    </label>

                    <label className="flex flex-col font-medium">
                        Till
                        <DatePicker
                            selected={end ? new Date(end) : null}
                            onChange={(d) => d && setRange([start, toLocalInput(d)])}
                            showTimeSelect
                            timeIntervals={30}
                            dateFormat="dd.MM.yyyy HH:mm"
                            className="field"
                        />
                    </label>

                    <div className="flex items-end ml-auto gap-4">
                        <span className="items-center flex gap-2">
                            <i className="size-3 rounded-full bg-ok" />
                            Available
                        </span>
                        <span className="items-center flex gap-2">
                            <i className="size-3 rounded-full bg-bad" />
                            Booked
                        </span>
                    </div>
                </div>

                {invalid && (
                    <div className="rounded-form border border-bad bg-bad-soft px-3 py-2 text-sm text-bad-ink mb-2">
                        Start time must be earlier than end time!
                    </div>
                )}

                {error && !invalid && (
                    <div className="rounded-form border border-bad bg-bad-soft px-3 py-2 text-sm text-bad-ink mb-2">
                        {error}
                    </div>
                )}

                {isPast && (
                    <div className="rounded-form border border-bad bg-bad-soft px-3 py-2 text-sm text-bad-ink mb-2">
                        Booking in the past is NOT POSSIBLE. Choose a future time!
                    </div>
                )}

                {!invalid && !error && spaces === null && (
                    <p className="text-muted">Loading...</p>
                )}

                {!invalid && !error && spaces?.length === 0 && (
                    <p className="text-muted">No spaces found...</p>
                )}

                {notice && (
                    <div className="rounded-form border border-ok bg-ok-soft px-3 py-2 text-sm text-ok-ink mb-4">
                        {notice}
                    </div>
                )}

                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {!invalid && spaces?.map((s) => {
                        const facilities = Array.isArray(s.facilities) ? s.facilities : []

                        return (
                            <div
                                key={s.id}
                                className="flex flex-col rounded-form border border-line bg-white p-5 shadow-soft transition-shadow hover:shadow-hover"
                            >
                                <div className="flex items-start justify-between gap-2">
                                    <h2 className="font-semibold text-navy">{s.name}</h2>
                                    <span className="chip">{s.category}</span>
                                </div>

                                <p className="mt-1 text-sm text-muted">
                                    {s.capacity} {s.capacity === 1 ? "seat" : "seats"}
                                </p>

                                {facilities.length > 0 && (
                                    <div className="mt-3 flex flex-wrap gap-2">
                                        {facilities.map((f) => (
                                            <span key={f} className="chip">{f}</span>
                                        ))}
                                    </div>
                                )}

                                <button
                                    type="button"
                                    onClick={() => setDetails(s)}
                                    className="mt-3 self-start text-sm font-medium text-navy underline cursor-pointer"
                                >
                                    Details
                                </button>

                                <div className="mt-auto flex items-center justify-between gap-2 pt-4">
                                    <span className={`badge ${s.is_available ? "badge-ok" : "badge-bad"}`}>
                                        {s.is_available ? "Available" : "Booked"}
                                    </span>

                                    {isPast ? (
                                        <p className="text-sm text-muted">
                                            Can NOT book: selected time is in the past!
                                        </p>
                                    ) : s.is_available ? (
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setNotice("")
                                                setBooking(s)
                                            }}
                                            className="btn btn-primary"
                                        >
                                            Book
                                        </button>
                                    ) : (
                                        s.available_from && (
                                            <div className="flex items-center justify-between gap-2">
                                                <p className="text-sm text-bad-ink">
                                                    Free from {formatDT(s.available_from)}
                                                </p>

                                                <button
                                                    type="button"
                                                    onClick={() => {
                                                        const from = new Date(s.available_from)

                                                        setRange([
                                                            toLocalInput(from),
                                                            toLocalInput(
                                                                new Date(from.getTime() + 60 * 60 * 1000)
                                                            )
                                                        ])
                                                    }}
                                                    className="text-sm font-medium text-navy underline cursor-pointer"
                                                >
                                                    Show then
                                                </button>
                                            </div>
                                        )
                                    )}
                                </div>
                            </div>
                        )
                    })}
                </div>
            </main>

            {booking && (
                <BookingModal
                    space={booking}
                    start={start}
                    end={end}
                    onClose={() => setBooking(null)}
                    onBooked={(name) => {
                        setBooking(null)
                        setNotice(`${name} booked successfully!`)
                        setRefresh((n) => n + 1)
                    }}
                />
            )}

            {details && (
                <SpaceDetailsModal
                    space={details}
                    day={start}
                    onClose={() => setDetails(null)}
                />
            )}
        </>
    )
}