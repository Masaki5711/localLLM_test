import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'チャット' },
  { to: '/documents', label: 'ドキュメント' },
]

export function Navigation() {
  return (
    <nav className="flex gap-1 bg-gray-800 px-4 py-2">
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            `rounded px-3 py-1 text-sm ${
              isActive
                ? 'bg-gray-700 text-white'
                : 'text-gray-300 hover:bg-gray-700 hover:text-white'
            }`
          }
        >
          {item.label}
        </NavLink>
      ))}
    </nav>
  )
}
