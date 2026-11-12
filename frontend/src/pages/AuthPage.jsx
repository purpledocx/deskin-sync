import { useState } from "react";
import { Link, Navigate, useSearchParams, useNavigate } from "react-router-dom";
import { register, login } from "../api/auth";
import { getUser } from "../api/session";

export default function AuthPage() {
  const [params, setParams] = useSearchParams();
  const mode = params.get("mode") === "login" ? "login" : "register";
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError("");

    if (mode === "register") {
      const name = form.name.trim();
      if (name.length < 2 || name.length > 100)
        return setError("Name must be between 2 and 100 characters.");
      if (!/^\S+@\S+\.\S+$/.test(form.email)) // regex validation
        return setError("Enter a valid email address.");
      if (form.password.length < 8)
        return setError("Password must be at least 8 characters.");
      if (form.password.length > 72)
        return setError("Password must be at most 72 characters.");
    }

    setLoading(true);
    try {
      if (mode === "register") await register(form);
      await login(form.email, form.password);
      navigate("/app");
    } catch (err) {
      setError(
        err.status === 409
          ? "This email is already in use."
          : err.status === 401
          ? "Email or password is incorrect. Please try again."
          : err.status === 422
          ? err.message
          : err.status === 0
          ? "Server-side is unreachable. Try again later."
          : "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  // already signed in ---> straight to the app
  if (getUser()) return <Navigate to="/app" replace />;

  const tab = (m, label) => (
    <button
      type="button"
      onClick={() => {
        setError("");
        setParams(m === "login" ? { mode: "login" } : {});
      }}
      className={`flex-1 border-b-2 py-3 text-lg ${
        mode === m ? "border-navy font-semibold text-navy" : "border-transparent text-muted"
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="grid min-h-screen md:grid-cols-2">
      <div className="hidden flex-col items-center justify-center gap-6 bg-surface md:flex">
        <Link to="/" className="text-3xl font-semibold text-navy">DeskIn Sync</Link>
        <div className="flex items-center justify-center">
          <img 
              src={"../../Workspace.jpg"} 
              alt="DeskIn Sync Workspace Screenshot" 
              className="w-full h-auto rounded-xl shadow-xl border border-line/50 object-cover"
          />
        </div>
      </div>

      <div className="flex flex-col items-center justify-center gap-4 p-6">
        <Link
          to="/"
          className="w-full max-w-lg text-xl text-muted transition-colors hover:text-navy"
        >
          ← Back to home
        </Link>
        <form
          onSubmit={submit}
          noValidate
          className="flex w-full max-w-lg flex-col gap-6 rounded-form border border-line bg-white p-8 shadow-soft sm:p-10"
        >
          <div className="flex border-b border-line">
            {tab("login", "Log in")}
            {tab("register", "Sign up")}
          </div>

          <h1 className="text-3xl font-semibold text-navy">
            {mode === "login" ? "Welcome back to DeskIn Sync" : "Create your account"}
          </h1>

          {mode === "register" && (
            <label className="flex flex-col gap-1.5 text-base font-medium">
              Name
              <input className="field h-12 text-base" value={form.name} onChange={set("name")} required />
            </label>
          )}
          <label className="flex flex-col gap-1.5 text-base font-medium">
            Email address
            <input type="email" className="field h-12 text-base" placeholder="richard@piedpiper.com" value={form.email} onChange={set("email")} required />
          </label>
          <label className="flex flex-col gap-1.5 text-base font-medium">
            Password
            <input type="password" className="field h-12 text-base" value={form.password} onChange={set("password")} required />
          </label>

          {mode === "register" && <p className="text-base text-muted">Your role will be set to Student automatically.</p>}
          {error && <div className="rounded-form border border-bad bg-bad-soft px-3 py-2 text-sm text-bad-ink">{error}</div>}

          <button disabled={loading} className="h-12 rounded-md bg-navy text-lg font-medium text-white hover:bg-steel disabled:opacity-60">
            {loading ? "Authenticating…" : mode === "login" ? "Log in" : "Sign up"}
          </button>
        </form>
      </div>
    </div>
  );
}