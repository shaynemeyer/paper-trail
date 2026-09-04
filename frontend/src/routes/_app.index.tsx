import { createFileRoute } from '@tanstack/react-router'
import { ScrollText } from 'lucide-react'

export const Route = createFileRoute('/_app/')({
  component: Index,
})

function Index() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3 text-center">
      <div className="flex size-12 items-center justify-center rounded-lg bg-accent text-accent-foreground">
        <ScrollText className="size-6" />
      </div>
      <h1 className="text-xl font-semibold">Your dashboard is coming soon</h1>
      <p className="max-w-sm text-sm text-muted-foreground">
        A personalized view of your documents will live here.
      </p>
    </div>
  )
}
