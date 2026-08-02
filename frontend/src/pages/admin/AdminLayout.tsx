import {
  NavLink,
  Outlet,
} from "react-router-dom"

const links = [
  ["/admin", "Overview"],
  ["/admin/users", "Users"],
  ["/admin/subscriptions", "Subscriptions"],
  ["/admin/system", "System"],
] as const

export default function AdminLayout() {
  return (
    <div>
      <div className="mb-8 flex flex-wrap gap-2">
        {links.map(([to, label]) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/admin"}
            className={({ isActive }) =>
              [
                "rounded-xl px-4 py-2 text-sm transition",
                isActive
                  ? "bg-blue-500 text-white"
                  : "bg-white/[0.04] text-slate-400 hover:text-white",
              ].join(" ")
            }
          >
            {label}
          </NavLink>
        ))}
      </div>

      <Outlet />
    </div>
  )
}
