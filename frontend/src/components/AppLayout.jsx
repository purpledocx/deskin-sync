import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { clearToken } from "../api/client";
import { getUser } from "../api/session";

const link = ({ isActive }) =>
  `border-b-2 py-5 text-[15px] transition-colors ${
    isActive
      ? "border-navy font-semibold text-navy"
      : "border-transparent text-muted hover:text-navy"
  }`;

export default function AppLayout() {
  const user = getUser();
  const navigate = useNavigate();

  const logout = () => {
    clearToken();
    navigate("/register?mode=login");
  };

  return (
    <div className="flex min-h-screen flex-col bg-surface">
      <header className="border-b border-line bg-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-x-6 px-6">
          <Link to="/" className="py-4 text-xl font-semibold text-navy">DeskIn Sync</Link>

          <nav className="flex gap-8">
            <NavLink to="/app" end className={link}>Spaces</NavLink>
            <NavLink to="/app/bookings" className={link}>My bookings</NavLink>
          </nav>

          <div className="flex items-center gap-3 py-3">
            <span className="hidden text-sm text-muted sm:inline">{user?.email}</span>
            <span className="chip">{user?.role}</span>
            <button onClick={logout} className="btn btn-secondary h-9">Log out</button>
          </div>
        </div>
      </header>

      <div className="flex-1">
        <Outlet />
      </div>

      <footer className="border-t border-line bg-white py-4 text-center text-sm text-muted">
        2026 DeskIn Sync - <a href="github.com/purpledocx">github.com/purpledocx</a>
      </footer>
    </div>
  );
}