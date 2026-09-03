import { createRootRoute, Link, Outlet } from '@tanstack/react-router'

export const Route = createRootRoute({
  component: RootComponent,
})

function RootComponent() {
  return (
    <div className="min-h-svh">
      <header className="border-b px-6 py-3">
        <nav className="flex items-center gap-4 text-sm font-medium">
          <Link to="/" className="[&.active]:text-primary">
            Home
          </Link>
        </nav>
      </header>
      <main className="p-6">
        <Outlet />
      </main>
    </div>
  )
}
