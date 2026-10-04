const steps = [
  { title: "Pick your time", text: "Define exact start and end time of your booking" },
  { title: "Check availability", text: "Review real-time occupancy status directly in interactive schedule" },
  { title: "Book & Manage", text: "Finalize your reservation and modify details anytime via your personal dashboard" }
];

export default function HowItWorks() {
  return (
    <section id="how-it-work" className="bg-white py-20 scroll-mt-20">
      
      <div className="mx-auto px-6 max-w-6xl">
        
        <h2 className="text-3xl text-navy font-semibold">How it works</h2>
        
        <p className="text-ink/70 mt-2 mb-10">From search to confirmed booking in three easy steps.</p>
        
        <div className="grid gap-8 md:grid-cols-3">
          
          
          {steps.map((s, i) => (
            <div key={s.title} className="flex flex-col gap-3">
              
              <div className="size-11 bg-navy text-white rounded-full flex font-semibold justify-center items-center">
                {i + 1}
              </div>
              
              <div>
                <h3 className="font-semibold text-lg">{s.title}</h3>
                <p className="text-ink/70 text-sm mt-1">{s.text}</p>
              </div>
            
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
