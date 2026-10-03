const stack = [
  {
    name: "FastAPI",
    logo: "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg",
  },
  {
    name: "React",
    logo: "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg",
  },
  {
    name: "PostgreSQL",
    logo: "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg",
  },
  {
    name: "JWT auth",
    logo: "https://jwt.io/img/icon.svg",
  },
];

export default function Stack() {
    return(
        <section className="bg-white border-line border-y py-6">
            <div className="flex flex-col mx-auto items-center gap-3 px-6">
                <p className="text-sm text-ink/60">Built with modern and secure stack</p>
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