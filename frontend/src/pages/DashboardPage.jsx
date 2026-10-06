
// ----------------------------------------------------FUNCTIONS----------------------------------------------------

import { useNavigate } from "react-router-dom"
import { clearToken } from "../api/client"
import { useEffect, useState } from "react"
import { getAvailability } from "../api/spaces"
import DatePicker from "react-datepicker"
import "react-datepicker/dist/react-datepicker.css"




// 8 -> 08 
const pad = (n) => String(n).padStart(2,"0")

// date object to YYYY-MM-DD-THH:mm for html datetime input
const toLocalInput = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`


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
    }, [start, end, invalid]) //rerun whenever start, end or validity changes

    


    return(
        <div className="min-h-screen bg-surface">
            <header className="bg-white items-center flex justify-between border-b border-line px-6 py-4">
                <span className="text-3xl text-navy font-semibold">DeskIn Sync</span>
                <button onClick={logout} className="text-2xl rounded-md bg-gray-100 text-gray-900 border border-gray-300 hover:bg-navy hover:text-white transition-colors duration-200 ease-in-out">Log out</button>
            </header>

            <main className="max-w-6xl p-6">
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
                    <div className="border border-bad text-bad rounded-md text-sm px-3 py-2">Start time must be earlier that end time!</div>
                )}

                {error && invalid && (
                    <div className="border border-bad text-bad rounded-md text-sm px-3 py-2">{error}</div>
                )}


                {!invalid && !error && spaces == null && <p className="text-ink/60">Loading...</p>}
                {!invalid && spaces?.length === 0 && <p className="text-ink/60">No spaces found...</p>}


                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {spaces?.map((s) => (
                        <div key={s.id} className="bg-white  border-2 rounded-xl p-5">
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
                        </div>
                    ))}
                </div>
            </main>
        </div>
    )
}