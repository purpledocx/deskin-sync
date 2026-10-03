import { Link } from "react-router-dom";

export default function Navbar() {
    return (
        <header className="border-b border-line bg-white" >
            <div className="mx-auto flex h-18 max-w-6xl  items-center justify-between px-6">

                <Link to="/" className="text-xl font-semibold text-navy">DeskIn Sync</Link>

                <nav className="hidden gap-8 text-ink md:flex">
                    <a href="#functions">Functions</a>
                    <a href="#how-it-work">How does it work?</a>
                    <a href="#pricing">Pricing</a>
                </nav>

                <div className="flex gap-5 items-center">
                    <Link to="/register?method=login" className="text-ink">Login</Link>
                    <Link to="/register" className="rounded-md text-white bg-navy px-5 py-2.5 hover:bg-steel transition-colors duration-200 ease-in-out">Dive in Demo-mode</Link>
                </div>

            </div>

        </header>
    )
}