import { createFileRoute } from '@tanstack/react-router'
import type { ColumnDef } from '@tanstack/react-table'
import { DataTable } from '@/components/data-table'
import { Badge } from '@/components/ui/badge'

export const Route = createFileRoute('/')({
  component: Index,
})

interface Document {
  id: string
  name: string
  status: 'draft' | 'pending' | 'approved'
  updatedAt: string
}

const data: Document[] = [
  { id: '1', name: 'Invoice #1024', status: 'approved', updatedAt: '2026-08-12' },
  { id: '2', name: 'Contract - Acme Co', status: 'pending', updatedAt: '2026-08-30' },
  { id: '3', name: 'Receipt #552', status: 'draft', updatedAt: '2026-09-01' },
]

const statusVariant: Record<Document['status'], 'default' | 'secondary' | 'outline'> = {
  approved: 'default',
  pending: 'secondary',
  draft: 'outline',
}

const columns: ColumnDef<Document>[] = [
  { accessorKey: 'name', header: 'Name' },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => (
      <Badge variant={statusVariant[row.original.status]}>
        {row.original.status}
      </Badge>
    ),
  },
  { accessorKey: 'updatedAt', header: 'Updated' },
]

function Index() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Documents</h1>
      <DataTable columns={columns} data={data} />
    </div>
  )
}
