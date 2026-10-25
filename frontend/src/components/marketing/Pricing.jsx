import { Link } from "react-router-dom"


const plans = [
  { 
    name: "Starter", 
    price: "Free", 
    items: ["Up to 5 managed spaces", "Standard scheduling tools", "Email support"], 
    cta: "Get started for free", 
    to: "/register" 
  },
  { 
    name: "Team", 
    price: "€4", 
    unit: "per user / month", 
    items: ["Unlimited spaces & bookings", "Advanced roles & permissions", "Centralized analytics dashboard"], 
    cta: "Start free trial", 
    to: "/register", 
    highlight: true 
  },
  { 
    name: "Enterprise",
    price: "Custom", 
    items: ["Multi-location management", "Tailored automation rules", "Dedicated onboarding & SLA"], 
    cta: "Contact sales", 
    to: "/register" 
  },
];



export default function Pricing() {
    return(
        <section id="pricing" className="max-w-6xl px-6 py-20 mx-auto scroll-mt-20">
            
            <div className="flex flex-wrap items-center gap-3">
                <h2 className="text-3xl text-navy font-semibold">Pricing</h2>
                <span className="rounded-full border border-line bg-surface px-3 py-1 text-xs font-semibold uppercase tracking-wide text-muted">
                    Example plans
                </span>
            </div>

            <p className="text-ink/70 mt-2 mb-10">
                From small team to giant enterprises, we've got you covered! The plans below are
                examples for this demo - DeskIn Sync does not process any payments.
            </p>
            
            <div className="grid gap-6 md:grid-cols-3">

                {plans.map((p) => (
                    <div key={p.name} className={`bg-white p-7 rounded-lg flex flex-col shadow-soft ${p.highlight ? " border-navy border-2" : "border border-line"} `}>

                        <h3 className="font-semibold">{p.name}</h3>
                        
                        <div className="font-semibold text-4xl">
                            {p.price} <span className="text-muted text-sm font-normal">{p.unit}</span>
                        </div>
                        
                        <ul className="text-ink/80 text-sm list-disc flex-1 pl-5 space-y-1">
                            {p.items.map((i) => <li key={i}>{i}</li>)}
                        </ul>

                        <Link to={p.to} className={`font-medium text-center px-5 py-2.5 rounded-md mt-3 ${p.highlight ? "bg-navy text-white hover:bg-steel transition-colors duration-200 ease-in-out" : "border border-line hover:bg-surface transition-colors duration-200 ease-in-out" }`}>
                            {p.cta}
                        </Link>
                    </div>
                ))}

            </div>

        </section>
    )
}