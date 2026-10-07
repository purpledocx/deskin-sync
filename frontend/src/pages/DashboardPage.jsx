
// ----------------------------------------------------FUNCTIONS----------------------------------------------------

import { useNavigate } from "react-router-dom"
import { clearToken } from "../api/client"
import { useEffect, useState } from "react"
import { getAvailability } from "../api/spaces"
import BookingModal from "../components/modals/BookingModal"
import DatePicker from "react-datepicker"
import "react-datepicker/dist/react-datepicker.css"




// 8 -> 08 
const pad = (n) => String(n).padStart(2,"0")

// date object to YYYY-MM-DD-THH:mm for html datetime input
const toLocalInput = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
const formatDT = (iso) => {
    const d = new Date(iso)
    return `${pad(d.getDate())}.${pad(d.getMonth() + 1)} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}


function defaultRange(){

    // default range time to closest half hour + 1hr end time
    const start = new Date()
    start.setMinutes(start.getMinutes() < 30 ? 30 : 60, 0, 0)

    const end = new Date(start.getTime() + 60 * 60 * 1000)

    return [toLocalInput(start), toLocalInput(end)]
}

const fieldCSS = "h-11 rounded-md border border-line px-3 outline-none focus:border-navy focus:ring-2 focus:ring-navy/20"



// ----------------------------------------------------DASHBOARD-PAGE----------------------------------------------------
export default function DashboardPage() {
    
    const navigate = useNavigate()

    const logout = () => {
        clearToken()
        navigate('/register?mode=login')
    }

    const [[start, end], setRange] = useState(defaultRange)
    const invalid = !start || !end || start >= end

    const [spaces, setSpaces] = useState(null) // list of spaces from backend | null -> loading
    
    const [error, setError] = useState("")

    // BookinModal states
    const [booking, setBooking] = useState(null)
    const [refresh, setRefresh] = useState(0) 
    const [notice, setNotice] = useState("")


    useEffect(() => {
        if (invalid) return;
        let ignore = false; // flag to fix race conditions when user clicks fast
        getAvailability(start, end)
            .then((data) => {
                if (ignore) return;
                setSpaces(data)
                setError("")
            })
            .catch((err) => {
                if (!ignore) setError(err.message)
            })
        return () => {
            ignore = true
        }
    }, [start, end, invalid, refresh]) //rerun whenever start, end or validity changes

    


    return(
        <div className="min-h-screen bg-surface">
            <header className="bg-white items-center flex justify-between border-b border-line px-6 py-4">
                <span className="text-3xl text-navy font-semibold">DeskIn Sync</span>
                <button onClick={logout} className="text-2xl rounded-md bg-gray-100 text-gray-900 border border-gray-300 hover:bg-navy hover:text-white transition-colors duration-200 ease-in-out">Log out</button>
            </header>

            <main className="max-w-6xl mx-auto p-6">
                <h1 className="text-4xl text-navy font-semibold mb-4">Space availability</h1>


                <div className="bg-white flex flex-wrap border border-line rounded-xl gap-4 mb-6 p-4">
                    
                    <label className="flex flex-col font-medium">From
                        <DatePicker
                            selected={start ? new Date(start) : null}
                            onChange={(d) => setRange([toLocalInput(d), end])}
                            showTimeSelect
                            timeIntervals={30}
                            dateFormat="dd.MM.yyyy HH:mm"
                            className={fieldCSS}
                        />
                    </label>

                    <label className="flex flex-col font-medium">Till
                        <DatePicker
                            selected={end ? new Date(end) : null}
                            onChange={(d) => setRange([start, toLocalInput(d)])}
                            showTimeSelect
                            timeIntervals={30}
                            dateFormat="dd.MM.yyyy HH:mm"
                            className={fieldCSS}
                        />
                    </label>

                    <div className="flex items-end ml-auto gap-4">
                        <span className="items-center flex gap-2"><i className="size-3 rounded-full bg-green-600 "/> Available</span>
                        <span className="items-center flex gap-2"><i className="size-3 rounded-full bg-red-600 "/> Booked</span>
                    </div>
                </div>

                {invalid && (
                    <div className="border border-bad text-bad rounded-md px-3 py-2 mb-2 text-xl">Start time must be earlier than end time!</div>
                )}

                {error && !invalid && (
                    <div className="border border-bad text-bad rounded-md px-3 py-2 mb-2 text-xl">{error}</div>
                )}


                {!invalid && !error && spaces == null && <p className="text-ink/60">Loading...</p>}
                {!invalid && spaces?.length === 0 && <p className="text-ink/60">No spaces found...</p>}


                {notice && (
                    <div className=" bg-green-50 border border-green-600 text-green-600 text-sm rounded-md px-3 py-2 mb-4">{notice}</div>
                )}


                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {spaces?.map((s) => (
                        <div key={s.id} className={`bg-white border-2 rounded-xl p-5 ${s.is_available ? "border-green-600" : "border-red-600"}`}>
                            <div className="flex  items-start justify-between gap-2">
                                <h2 className="text-navy font-semibold">{s.name}</h2>
                                <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${s.is_available ? "bg-green-100 text-green-600" : "bg-red-100 text-red-600"}`}>
                                    {s.is_available ? "Available" : "Booked"}
                                </span>
                            </div>
                            <p className="text-ink/60 text-sm mt-1">
                                {s.category} · {s.capacity} {s.capacity === 1 ? "seat" : "seats"}
                            </p>
                            {s.facilities.length > 0 && (
                                <p className="mt-3 text-sm">{s.facilities.join(", ")}</p>
                            )}

                            <div className="mt-auto pt-4">
                            {s.is_available ? (
                                <button
                                    onClick={() => { setNotice(""); setBooking(s) }}
                                    className="text-white bg-navy font-medium rounded-md w-full h-10 border hover:bg-surface hover:text-navy transition-colors duration-200 ease-in-out"
                                >
                                    Book
                                </button>
                            ) : (
                                s.available_from && (
                                    <div className="flex items-center justify-between gap-2">
                                        <p className="text-sm text-red-600">Free from {formatDT(s.available_from)}</p>
                                        <button
                                            onClick={() => {
                                                const from = new Date(s.available_from)
                                                setRange([toLocalInput(from), toLocalInput(new Date(from.getTime() + 60 * 60 * 1000))])
                                            }}
                                            className="text-sm font-medium text-navy underline"
                                        >
                                            Show then
                                        </button>
                                    </div>
                                )
                            )}
                        </div>
                </div>
                    ))}
                </div>
            </main>

            {booking && (
            <BookingModal space={booking} start={start} end={end} onClose={() => setBooking(null)} onBooked={(name) => {
                setBooking(null)
                setNotice(`${name} booked successfully!`)
                setRefresh((n) => n + 1)
            }} />
        )}
    </div>
    )
}