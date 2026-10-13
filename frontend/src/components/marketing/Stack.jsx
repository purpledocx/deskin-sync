const stack = [
  {
    name: "FastAPI",
    logo: "/fastapi-original.svg",
  },
  {
    name: "React",
    logo: "/react-original.svg",
  },
  {
    name: "PostgreSQL",
    logo: "/postgresql-original.svg",
  },
  {
    name: "JWT auth",
    logo: "/jwt-icon.svg",
  },
];

export default function Stack() {
    return(
        <section className="bg-white border-line border-y py-6">
            <div className="flex flex-col mx-auto items-center gap-3 px-6">
                <p className="text-sm text-muted">Built with modern and secure stack</p>
                <div className="flex flex-wrap justify-center gap-3">
                    {stack.map((item) => (
                        <div 
                            key={item.name} 
                            className="flex items-center gap-2 text-sm px-9 py-3 bg-surface rounded border border-line"
                        >
                            <img 
                                src={item.logo} 
                                alt={`${item.name} logo`} 
                                className="w-15 h-15 object-contain" 
                            />
                            <span>{item.name}</span>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}