import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createFileRoute } from '@tanstack/react-router'
import type { ColumnDef } from '@tanstack/react-table'
import { useState } from 'react'
import { toast } from 'sonner'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { DataTable } from '@/components/data-table'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import {
  type Document,
  type DocumentInput,
  type DocumentStatus,
  type UploadDocumentInput,
  documentsApi,
} from '@/lib/api'

export const Route = createFileRoute('/_app/admin/documents')({
  component: AdminDocuments,
})

const statusVariant: Record<DocumentStatus, 'default' | 'secondary' | 'outline'> = {
  approved: 'default',
  pending: 'secondary',
  draft: 'outline',
}

const emptyForm: DocumentInput = {
  name: '',
  description: '',
  doctype: 'pdf',
  document_source: '',
  status: 'draft',
}

const emptyUploadForm = {
  name: '',
  description: '',
  document_source: '',
  tagsInput: '',
}

function AdminDocuments() {
  const queryClient = useQueryClient()
  const { data: documents = [], isLoading, error } = useQuery({
    queryKey: ['documents'],
    queryFn: documentsApi.list,
  })

  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<Document | null>(null)
  const [form, setForm] = useState<DocumentInput>(emptyForm)

  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)
  const [uploadForm, setUploadForm] = useState(emptyUploadForm)
  const [uploadFile, setUploadFile] = useState<File | null>(null)

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['documents'] })

  const createMutation = useMutation({
    mutationFn: documentsApi.create,
    onSuccess: () => {
      invalidate()
      toast.success('Document created')
      setDialogOpen(false)
    },
    onError: (err: Error) => toast.error(err.message),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: DocumentInput }) =>
      documentsApi.update(id, data),
    onSuccess: () => {
      invalidate()
      toast.success('Document updated')
      setDialogOpen(false)
    },
    onError: (err: Error) => toast.error(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: documentsApi.remove,
    onSuccess: () => {
      invalidate()
      toast.success('Document deleted')
    },
    onError: (err: Error) => toast.error(err.message),
  })

  const embedMutation = useMutation({
    mutationFn: documentsApi.embed,
    onSuccess: () => {
      invalidate()
      toast.success('Embedding generated')
    },
    onError: (err: Error) => toast.error(err.message),
  })

  const uploadMutation = useMutation({
    mutationFn: documentsApi.upload,
    onSuccess: () => {
      invalidate()
      toast.success('Document uploaded')
      setUploadDialogOpen(false)
      setUploadForm(emptyUploadForm)
      setUploadFile(null)
    },
    onError: (err: Error) => toast.error(err.message),
  })

  function openCreate() {
    setEditing(null)
    setForm(emptyForm)
    setDialogOpen(true)
  }

  function openEdit(document: Document) {
    setEditing(document)
    setForm({
      name: document.name,
      description: document.description,
      doctype: document.doctype,
      document_source: document.document_source ?? '',
      status: document.status,
    })
    setDialogOpen(true)
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (editing) {
      updateMutation.mutate({ id: editing.id, data: form })
    } else {
      createMutation.mutate(form)
    }
  }

  function openUpload() {
    setUploadForm(emptyUploadForm)
    setUploadFile(null)
    setUploadDialogOpen(true)
  }

  function handleUploadSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!uploadFile) {
      toast.error('Select a PDF file')
      return
    }
    if (uploadFile.type !== 'application/pdf') {
      toast.error('Only PDF files are supported')
      return
    }
    const data: UploadDocumentInput = {
      file: uploadFile,
      name: uploadForm.name,
      description: uploadForm.description,
      document_source: uploadForm.document_source || undefined,
      tags: uploadForm.tagsInput
        .split(',')
        .map((tag) => tag.trim())
        .filter(Boolean),
    }
    uploadMutation.mutate(data)
  }

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
      header: 'Actions',
      cell: ({ row }) => (
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => openEdit(row.original)}>
            Edit
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={embedMutation.isPending}
            onClick={() => embedMutation.mutate(row.original.id)}
          >
            Embed
          </Button>
          <AlertDialog>
            <AlertDialogTrigger
              render={
                <Button variant="destructive" size="sm">
                  Delete
                </Button>
              }
            />
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete this document?</AlertDialogTitle>
                <AlertDialogDescription>
                  This permanently deletes "{row.original.name}". This action cannot
                  be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={() => deleteMutation.mutate(row.original.id)}
                >
                  Delete
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      ),
    },
  ]

  if (error) {
    return <p className="text-destructive">{error.message}</p>
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Documents</h1>
        <div className="flex gap-2">
          <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
            <DialogTrigger
              render={
                <Button variant="outline" onClick={openUpload}>
                  Upload PDF
                </Button>
              }
            />
            <DialogContent>
              <form onSubmit={handleUploadSubmit} className="space-y-4">
                <DialogHeader>
                  <DialogTitle>Upload PDF</DialogTitle>
                </DialogHeader>
                <div className="space-y-2">
                  <Label htmlFor="upload-file">PDF file</Label>
                  <Input
                    id="upload-file"
                    type="file"
                    accept="application/pdf"
                    required
                    onChange={(e) => setUploadFile(e.target.files?.[0] ?? null)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="upload-name">Name</Label>
                  <Input
                    id="upload-name"
                    required
                    value={uploadForm.name}
                    onChange={(e) =>
                      setUploadForm({ ...uploadForm, name: e.target.value })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="upload-description">Description</Label>
                  <Textarea
                    id="upload-description"
                    required
                    maxLength={500}
                    value={uploadForm.description}
                    onChange={(e) =>
                      setUploadForm({ ...uploadForm, description: e.target.value })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="upload-source">Source (optional)</Label>
                  <Input
                    id="upload-source"
                    value={uploadForm.document_source}
                    onChange={(e) =>
                      setUploadForm({ ...uploadForm, document_source: e.target.value })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="upload-tags">Tags (comma-separated, optional)</Label>
                  <Input
                    id="upload-tags"
                    value={uploadForm.tagsInput}
                    onChange={(e) =>
                      setUploadForm({ ...uploadForm, tagsInput: e.target.value })
                    }
                  />
                </div>
                <DialogFooter>
                  <Button type="submit" disabled={uploadMutation.isPending}>
                    {uploadMutation.isPending ? 'Uploading…' : 'Upload'}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger render={<Button onClick={openCreate}>New Document</Button>} />
            <DialogContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <DialogHeader>
                  <DialogTitle>{editing ? 'Edit Document' : 'New Document'}</DialogTitle>
                </DialogHeader>
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    required
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    required
                    maxLength={500}
                    value={form.description}
                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="doctype">Doctype</Label>
                    <Input
                      id="doctype"
                      value={form.doctype}
                      onChange={(e) => setForm({ ...form, doctype: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="status">Status</Label>
                    <Select
                      value={form.status}
                      onValueChange={(value) =>
                        setForm({ ...form, status: value as DocumentStatus })
                      }
                    >
                      <SelectTrigger id="status">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="draft">draft</SelectItem>
                        <SelectItem value="pending">pending</SelectItem>
                        <SelectItem value="approved">approved</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="document_source">Source (optional)</Label>
                  <Input
                    id="document_source"
                    value={form.document_source ?? ''}
                    onChange={(e) =>
                      setForm({ ...form, document_source: e.target.value })
                    }
                  />
                </div>
                <DialogFooter>
                  <Button
                    type="submit"
                    disabled={createMutation.isPending || updateMutation.isPending}
                  >
                    {editing ? 'Save' : 'Create'}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>
      {isLoading ? (
        <p className="text-muted-foreground">Loading…</p>
      ) : (
        <DataTable columns={columns} data={documents} />
      )}
    </div>
  )
}
