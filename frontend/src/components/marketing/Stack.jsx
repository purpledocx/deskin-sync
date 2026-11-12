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
    name: "SQLAlchemy",
    logo: "/sqlalchemy-original.svg",
  },
  {
    name: "Alembic",
    short: "Al",
  },
  {
    name: "Pydantic",
    logo: "/pydantic-original.svg",
  },
  {
    name: "JWT + bcrypt",
    logo: "/jwt-icon.svg",
  },
  {
    name: "Tailwind CSS",
    logo: "/tailwindcss-original.svg",
  },
  {
    name: "Vite",
    logo: "/vitejs-original.svg",
  },
  {
    name: "Pytest",
    logo: "/pytest-original.svg",
  },
  {
    name: "ESLint",
    logo: "/eslint-original.svg",
  },
  {
    name: "GitLab CI",
    logo: "/gitlab-original.svg",
  },
  {
    name: "GitHub Actions",
    logo: "/github-original.svg",
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
                            {item.logo ? (
                                <img 
                                    src={item.logo} 
                                    alt={`${item.name} logo`} 
                                    className="w-15 h-15 object-contain" 
                                />
                            ) : (
                                // no logo file in /public yet -> same-size placeholder with initials
                                <span className="w-15 h-15 flex items-center justify-center rounded border border-line bg-white text-lg font-semibold text-muted">
                                    {item.short}
                                </span>
                            )}
                            <span>{item.name}</span>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}