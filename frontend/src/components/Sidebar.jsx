import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard", num: "01" },
  { to: "/logs", label: "Logs", num: "02" },
  { to: "/clusters", label: "Clusters", num: "03" },
  { to: "/review", label: "Review Queue", num: "04" },
  { to: "/export", label: "Export", num: "05" },
];

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {/* backdrop, mobile only */}
      {open && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-ink/30 z-30 lg:hidden"
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed lg:sticky top-0 left-0 h-screen w-64 sm:w-56 shrink-0 border-r border-line
        bg-paper px-4 py-6 z-40 transition-transform duration-200 ease-out overflow-y-auto
        ${open ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0`}
      >
        <div className="flex items-start justify-between mb-8">
          <div>
            <div className="text-xs mono uppercase tracking-widest text-accent">flywheel</div>
            <div className="text-sm font-semibold leading-tight mt-1">
              Log → Eval Dataset
              <br />
              Builder
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close menu"
            className="lg:hidden text-ink/50 hover:text-ink text-lg leading-none p-1 -mr-1"
          >
            ✕
          </button>
        </div>

        <nav className="flex flex-col gap-1">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.to === "/"}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded px-2 py-2 lg:py-1.5 text-sm transition-colors ${
                  isActive ? "bg-ink text-paper" : "text-ink/70 hover:bg-ink/5"
                }`
              }
            >
              <span className="mono text-[10px] opacity-60">{l.num}</span>
              {l.label}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
}
