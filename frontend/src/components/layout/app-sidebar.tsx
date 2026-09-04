import { Link } from '@tanstack/react-router'
import { FileStack, ScrollText, Users } from 'lucide-react'
import { NavUser } from '@/components/layout/nav-user'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar'
import { getCurrentUser } from '@/lib/api'

const navItems = [
  { label: 'My Documents', icon: FileStack, to: '/', adminOnly: false },
  { label: 'Documents', icon: FileStack, to: '/admin/documents', adminOnly: true },
  { label: 'Users', icon: Users, to: '/admin/users', adminOnly: true },
]

export function AppSidebar() {
  const isAdmin = getCurrentUser()?.role === 'admin'
  const visibleItems = navItems.filter((item) => !item.adminOnly || isAdmin)

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="py-4">
        <div className="flex items-center gap-2">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
            <ScrollText className="size-4" />
          </div>
          <span className="text-sm font-semibold text-sidebar-foreground group-data-[collapsible=icon]:hidden">
            Paper Trail
          </span>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {visibleItems.map((item) => (
                <SidebarMenuItem key={item.label}>
                  <SidebarMenuButton
                    tooltip={item.label}
                    render={<Link to={item.to} activeOptions={{ exact: true }} />}
                    className="[&.active]:bg-sidebar-accent [&.active]:text-sidebar-accent-foreground"
                  >
                    <item.icon />
                    <span>{item.label}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <NavUser />
      </SidebarFooter>
    </Sidebar>
  )
}
