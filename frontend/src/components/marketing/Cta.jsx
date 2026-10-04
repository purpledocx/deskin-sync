import { Link } from "react-router-dom"

export default function Cta() {
    return(
        
        <section className="bg-navy text-white text-center py-16">
            <h2 className="text-5xl font-semibold mb-6">Try DeskIn Sync now!</h2>
            
            <Link to="/register" className="text-navy bg-white text-2xl sm:text-4xl md:text-7xl font-medium inline-block px-3 py-3 rounded-md border border-line hover:bg-navy hover:text-white transition-colors duration-200 ease-in-out">
            Dive in demo-mode
            </Link>
        </section>
    )
}