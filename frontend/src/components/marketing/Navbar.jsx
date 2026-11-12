import { useState } from "react";
import { Link } from "react-router-dom";
import { getUser } from "../../api/session";


const links = [
    ["Features", "#features"],
    ["How it works?", "#how-it-work"],
    ["Pricing", "#pricing"]
]

export default function Navbar() {

    const [open, setOpen] = useState(false);
    const close = () => setOpen(false);
    const user = getUser();


    return (
        <header className="sticky bg-white top-0 border-b border-line z-50">
            <div className="flex max-w-7xl items-center justify-between px-4 sm:px-6 md:h-18 mx-auto">
                
                <Link to="/" className="text-navy font-semibold text-xl">DeskIn Sync</Link>

                <nav className="hidden text-ink gap-8 md:flex">
                    {links.map(([label, href]) => <a key={href} href={href} className="transition-colors duration-200 hover:text-navy">{label}</a>)}
                </nav>

                <div className="flex items-center gap-3 sm:gap-5">
                    {!user && <Link to="/register?mode=login" className="  text-ink sm:inline">Log in</Link>}
                    <Link to={user ? "/app" : "/register"} className="text-white bg-navy rounded-md text-sm font-medium px-4 py-2 hover:bg-steel sm:px-5 sm:py-2.5 sm:text-base transition-colors duration-200 ease-in-out">{user ? "Open app" : "See demo"}</Link>

                    <button className="text-2xl md:hidden" aria-label="Menu" aria-expanded={open} onClick={() => setOpen(!open)}>{open ? "✕" : "☰"}</button>
                </div>
            </div>

                  <nav className={` flex flex-col gap-4 overflow-hidden border-t border-line px-4 transition-[max-height,opacity,padding] duration-300 ease-in-out
                                    md:hidden ${open ? "max-h-60 py-4 opacity-100" : "max-h-0 py-0 opacity-0"}`}>

                    {links.map(([label, href]) => (
                        <a href={href} key={href} onClick={close}>{label}</a>
                    ))}
                    
                    {!user && <Link to="/register?mode=login" onClick={close}>Log in</Link>}
                    
                    </nav>
        </header>
    )
}