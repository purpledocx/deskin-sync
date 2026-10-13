import { Link } from "react-router-dom"

export default function Hero() {
    return(
        <section className="bg-surface">
            <div className="mx-auto grid max-w-6xl items-center px-6 py-20 md:grid-cols-2">
                <div className="flex flex-col gap-5">
                    <div className="h-0.75 w-18 bg-gold" />
                    <h1 className="text-5xl text-navy font-semibold leading-tight">Book desks and meeting rooms in easiest way ever!</h1>
                    <p className="text-lg text-ink/70">Reserving spaces is now effortless for students, teachers, and admins. DeskIn Sync lets students, teachers and admins reserve spaces just in few clicks! With live availability and clear guidance.</p>
                    <div className="flex gap-3">
                        <Link to="/register?method=login" className="text-white bg-navy rounded-md px-6 py-3 font-medium hover:bg-steel transition-colors duration-200 ease-in-out">Begin with demo</Link>
                        <a href="#how-it-work" className=" text-ink bg-white border border-line rounded px-6 py-3">How does it work?</a>
                    </div>
                </div>
                
                <div className="flex items-center justify-center">
                    <img 
                        src={"/Dashboard.jpg"} 
                        alt="DeskIn Sync Dashboard Screenshot" 
                        className="w-full h-auto rounded-xl shadow-xl border border-line/50 object-cover"
                    />
                </div>
            </div>
        </section>
    )
}