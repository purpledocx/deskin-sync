const features = [
    {title: "Real-time availability", text: "Select time slot and instantly see which spaces are free, filtered by capacity and equipment."},
    {title: "No double booking", text: "Say goodbye to scheduling conflicts. Overlapping reservations are blocked automatically"},
    {title: "Smart roles & rules", text: "Tailored access for Students, Teahcers and Admins. Booking changes locked 30 minutes before kickoff"}
]

export default function Features() {
    return (
        <section id="features" className="max-w-6xl px-6 py-20 mx-auto">
            
            <h2 className="text-3xl text-navy font-semibold">Everything you need to manage spaces</h2>
            
            <p className="text-ink/70 mt-2m mb-10">Three reasons why DeskIn Sync is your perfect choice.</p>
            
            <div className="gtid gap-6 md:grid-cols-3">

                {features.map((f) => (
                    <div key={f.title} className="bg-white shadow-sm p-7 border border-line rounded-lg flex flex-col gap-3">
                        
                        {/* interesing feature i added from react tutorial | works even WITHOUT internet o_0 */}
                        <div className="bg-green-600 size-11 rounded-lg flex items-center justify-center text-white">
                            <svg xmlns="http://w3.org" fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor" className="size-5">
                                <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                            </svg>
                        </div>
                            <h3 className="text-lg font-semibold">{f.title}</h3>
                            <p className="text-ink/70 text-sm ">{f.text}</p>
                    </div>
                ))}

            </div>
        </section>
    )
}