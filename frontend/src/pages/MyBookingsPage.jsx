import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import { cancelBooking, getBookings} from "../api/bookings"
import {getAvailability} from "../api/spaces"


const MIN_BEFORE_CHANGE = 30 * 60 * 1000 // 30 min || backend

const pad = (n) => String(n).padStart(2, "0")

const fmtDate = (iso) => {
    const d = new Date(iso)
    return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${pad(d.getFullYear())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const fmtTime = (iso) => {
    const d = new Date(iso)
    return `${pad(d.getHours())}:${pad(d.getMinutes())}`
}




export default function MyBookingPage() {

    const [bookings, setBookings] = useState(null) // null -> loading
    const [names, setNames] = useState({})
    const [busyId, setBusyId] = useState(null)
    const [notice, setNotice] = useState("")
    const [error, setError] = useState("")


    useEffect(() => {
        const now = new Date()
        const inHour = new Date(now.getTime() + 60 * 60 * 1000)

        Promise.all([
            getBookings(),
            getAvailability(now, inHour).catch(() => []), // только ради имён
        ])
            .then(([list, spaces]) => {
                setBookings(list)
                setNames(Object.fromEntries(spaces.map((s) => [s.id, s.name])))
            })
            .catch((err) => setError(err.message))
    }, [])

    const state = (b) => {
        if (b.status === "cancelled") return "cancelled"
        if (new Date(b.end_at) < new Date()) return "finished"
        if (new Date(b.start_at) - new Date() < MIN_BEFORE_CHANGE) return "locked"
        return "cancellable"
    }

    return(
        <div className="min-h-screen bg-surface">
            <header className=" bg-white flex items-center justify-between border-b border-line px-6 py-4">
                <span className="text-3xl text-navy font-semibold">DeskIn Sync</span>
                <Link to="/app" className="text-2xl rounded-md px-4 py-2 bg-gray-100 text-navy border border-gray-300 hover:bg-navy hover:text-white transition-colors duration-200 ease-in-out">← Dashboard</Link>
            </header>


            <main className=" max-w-3xl p-6 mx-auto">
                <h1 className="text-5xl text-navy font-semibold leading-[1.15] ">My bookings</h1>

                <div className="bg-gold h-0.75 w-36 mt-3 mb-6" />

                {error && (
                    <div className="text-bad-ink border-bad  text-sm mb-4 rounded-form border  bg-bad-soft px-3 py-2">{error}</div>
                )}

                {notice && (
                    <div>{notice}</div>
                )}

                {bookings === 0 && !error && <p>Loading...</p>}
                {bookings?.length === 0 && <p>You have no bookings.</p>}


                <div>
                    {bookings?.map((b) => {
                        const st = state(b)
                        return (
                            <div key={b.id}>
                                <div>
                                    <h2>{names[b.space_id] ?? `Space ${b.space_id}`}</h2>

                                    <p>{fmtDate(b.start_at)} - {fmtTime(b.end_at)}</p>

                                    <span></span>
                                </div>

                                <div></div>
                            </div>
                        )
                    })}
                </div>
            </main>
        </div>
    )
}