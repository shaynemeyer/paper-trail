import { useQuery } from '@tanstack/react-query'
import { createFileRoute } from '@tanstack/react-router'
import type { ColumnDef } from '@tanstack/react-table'
import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { DataTable } from '@/components/data-table'
import { type Document, type DocumentStatus, documentsApi } from '@/lib/api'

export const Route = createFileRoute('/_app/')({
  component: Index,
})

const statusVariant: Record<DocumentStatus, 'default' | 'secondary' | 'outline'> = {
  approved: 'default',
  pending: 'secondary',
  draft: 'outline',
}

function Index() {
  const { data: documents = [], isLoading, error } = useQuery({
    queryKey: ['documents'],
    queryFn: documentsApi.list,
  })

  const [activeDocument, setActiveDocument] = useState<Document | null>(null)

  const columns: ColumnDef<Document>[] = [
    { accessorKey: 'name', header: 'Name' },
    { accessorKey: 'doctype', header: 'Type' },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => (
        <Badge variant={statusVariant[row.original.status]}>
          {row.original.status}
        </Badge>
      ),
    },
    {
      accessorKey: 'updated_at',
      header: 'Updated',
      cell: ({ row }) => new Date(row.original.updated_at).toLocaleString(),
    },
    {
      id: 'actions',
      header: '',
      cell: ({ row }) => (
        <Button
          variant={activeDocument?.id === row.original.id ? 'default' : 'outline'}
          size="sm"
          onClick={() => setActiveDocument(row.original)}
        >
          {activeDocument?.id === row.original.id ? 'Selected' : 'Chat'}
        </Button>
      ),
    },
  ]

  if (error) {
    return <p className="text-destructive">{error.message}</p>
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Your Documents</h1>
      {isLoading ? (
        <p className="text-muted-foreground">Loading…</p>
      ) : documents.length === 0 ? (
        <p className="text-muted-foreground">No documents yet.</p>
      ) : (
        <DataTable columns={columns} data={documents} />
      )}
    </div>
  )
}
