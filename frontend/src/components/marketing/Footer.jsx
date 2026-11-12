const cols = [
  { title: "Product", links: ["Features", "Pricing", "Demo"] },
  { title: "Company", links: ["About us", "Contact"] },
  { title: "Legal", links: ["Privacy", "Terms & Conditions"] },
];

export default function Footer() {
    return(
        <footer className="bg-gray-900 text-gray-300 text-sm">
            
            <div className="max-w-7xl px-8 py-10 flex flex-wrap justify-between gap-8">
                
                <div>
                    <div className="text-white font-semibold mb-2">DeskIn Sync</div>
                    Book spaces smarter.
                </div>
                
                {cols.map((c) => (
                    <div key={c.title} className="flex flex-col gap-2">
                        <div className="text-white font-semibold">{c.title}</div>
                        {c.links.map((l) => <a key={l} href="#">{l}</a>)}
                    </div>
                ))}
                
            </div>
            
            <div className="text-center text-xs text-gray-400 bg-black/30 py-3">2026 DeskIn Sync - <a href="https://github.com/purpledocx" className="hover:underline">github.com/purpledocx</a></div>
        </footer>
    )
}