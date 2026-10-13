import { useState } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import { register, login } from "../api/auth";

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

  const tab = (m, label) => (
    <button
      type="button"
      onClick={() => {
        setError("");
        setParams(m === "login" ? { mode: "login" } : {});
      }}
      className={`flex-1 border-b-2 py-3 ${
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
              src={"../../dist/Workspace.png"} 
              alt="DeskIn Sync Workspace Screenshot" 
              className="w-full h-auto rounded-xl shadow-xl border border-line/50 object-cover"
          />
        </div>
      </div>

      <div className="flex items-center justify-center p-6">
        <form
          onSubmit={submit}
          noValidate
          className="flex w-full max-w-md flex-col gap-5 rounded-form border border-line bg-white p-8 shadow-soft"
        >
          <div className="flex border-b border-line">
            {tab("login", "Log in")}
            {tab("register", "Sign up")}
          </div>

          <h1 className="text-2xl font-semibold text-navy">
            {mode === "login" ? "Welcome back to DeskIn Sync" : "Create your account"}
          </h1>

          {mode === "register" && (
            <label className="flex flex-col gap-1 text-sm font-medium">
              Name
              <input className="field" value={form.name} onChange={set("name")} required />
            </label>
          )}
          <label className="flex flex-col gap-1 text-sm font-medium">
            Email address
            <input type="email" className="field" placeholder="richard@piedpiper.com" value={form.email} onChange={set("email")} required />
          </label>
          <label className="flex flex-col gap-1 text-sm font-medium">
            Password
            <input type="password" className="field" value={form.password} onChange={set("password")} required />
          </label>

          {mode === "register" && <p className="text-sm text-muted">Your role will be set to Student automatically.</p>}
          {error && <div className="rounded-form border border-bad bg-bad-soft px-3 py-2 text-sm text-bad-ink">{error}</div>}

          <button disabled={loading} className="h-11 rounded-md bg-navy font-medium text-white hover:bg-steel disabled:opacity-60">
            {loading ? "Authenticating…" : mode === "login" ? "Log in" : "Sign up"}
          </button>
        </form>
      </div>
    </div>
  );
}