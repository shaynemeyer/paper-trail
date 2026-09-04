import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createFileRoute } from '@tanstack/react-router'
import type { ColumnDef } from '@tanstack/react-table'
import { useState } from 'react'
import Markdown from 'react-markdown'
import { toast } from 'sonner'
import { z } from 'zod'
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
  Drawer,
  DrawerContent,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from '@/components/ui/drawer'
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
import { countWords, DESCRIPTION_MAX_WORDS } from '@/lib/validation'

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

// Mirrors backend/app/models/document.py's DocumentCreate/DocumentUpdate: name
// and doctype are unbounded strings, description is capped by word count (not
// character count -- see app/models/document.py's DESCRIPTION_MAX_WORDS).
const descriptionSchema = z
  .string()
  .min(1, 'Description is required')
  .refine((value) => countWords(value) <= DESCRIPTION_MAX_WORDS, {
    message: `Description must be ${DESCRIPTION_MAX_WORDS} words or fewer`,
  })

const documentSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: descriptionSchema,
  doctype: z.string().min(1, 'Doctype is required'),
  document_source: z.string().optional(),
  status: z.enum(['draft', 'pending', 'approved']),
})

const uploadFormSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: descriptionSchema,
  document_source: z.string().optional(),
  tagsInput: z.string().optional(),
})

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

  const [markdownDrawerOpen, setMarkdownDrawerOpen] = useState(false)
  const [markdownDocName, setMarkdownDocName] = useState('')
  const [markdownContent, setMarkdownContent] = useState('')

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['documents'] })

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

  const viewRawMutation = useMutation({
    mutationFn: (document: Document) => documentsApi.getRaw(document.id),
    onSuccess: (blob) => {
      window.open(URL.createObjectURL(blob), '_blank')
    },
    onError: (err: Error) => toast.error(err.message),
  })

  const viewMarkdownMutation = useMutation({
    mutationFn: (document: Document) => documentsApi.getMarkdown(document.id),
    onSuccess: (text, document) => {
      setMarkdownDocName(document.name)
      setMarkdownContent(text)
      setMarkdownDrawerOpen(true)
    },
    onError: (err: Error) => toast.error(err.message),
  })

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
    if (!editing) return
    const result = documentSchema.safeParse(form)
    if (!result.success) {
      toast.error(result.error.issues[0].message)
      return
    }
    updateMutation.mutate({ id: editing.id, data: result.data })
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
    const result = uploadFormSchema.safeParse(uploadForm)
    if (!result.success) {
      toast.error(result.error.issues[0].message)
      return
    }
    const data: UploadDocumentInput = {
      file: uploadFile,
      name: result.data.name,
      description: result.data.description,
      document_source: result.data.document_source || undefined,
      tags: (result.data.tagsInput ?? '')
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
          <Button
            variant="outline"
            size="sm"
            disabled={!row.original.raw_url || viewRawMutation.isPending}
            onClick={() => viewRawMutation.mutate(row.original)}
          >
            View Raw
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={!row.original.markdown_url || viewMarkdownMutation.isPending}
            onClick={() => viewMarkdownMutation.mutate(row.original)}
          >
            View Markdown
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
          <Drawer
            open={uploadDialogOpen}
            onOpenChange={setUploadDialogOpen}
            swipeDirection="right"
          >
            <DrawerTrigger
              render={
                <Button variant="outline" onClick={openUpload}>
                  Upload PDF
                </Button>
              }
            />
            <DrawerContent>
              <form
                onSubmit={handleUploadSubmit}
                className="flex min-h-0 flex-1 flex-col"
              >
                <DrawerHeader>
                  <DrawerTitle>Upload PDF</DrawerTitle>
                </DrawerHeader>
                <div className="flex-1 space-y-4 overflow-y-auto p-4">
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
                      value={uploadForm.description}
                      onChange={(e) =>
                        setUploadForm({ ...uploadForm, description: e.target.value })
                      }
                    />
                    <p className="text-xs text-muted-foreground">
                      {countWords(uploadForm.description)}/{DESCRIPTION_MAX_WORDS} words
                    </p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="upload-source">Source (optional)</Label>
                    <Input
                      id="upload-source"
                      value={uploadForm.document_source}
                      onChange={(e) =>
                        setUploadForm({
                          ...uploadForm,
                          document_source: e.target.value,
                        })
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
                </div>
                <DrawerFooter>
                  <Button type="submit" disabled={uploadMutation.isPending}>
                    {uploadMutation.isPending ? 'Uploading…' : 'Upload'}
                  </Button>
                </DrawerFooter>
              </form>
            </DrawerContent>
          </Drawer>
          <Drawer open={dialogOpen} onOpenChange={setDialogOpen} swipeDirection="right">
            <DrawerContent>
              <form onSubmit={handleSubmit} className="flex min-h-0 flex-1 flex-col">
                <DrawerHeader>
                  <DrawerTitle>Edit Document</DrawerTitle>
                </DrawerHeader>
                <div className="flex-1 space-y-4 overflow-y-auto p-4">
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
                      value={form.description}
                      onChange={(e) => setForm({ ...form, description: e.target.value })}
                    />
                    <p className="text-xs text-muted-foreground">
                      {countWords(form.description)}/{DESCRIPTION_MAX_WORDS} words
                    </p>
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
                </div>
                <DrawerFooter>
                  <Button type="submit" disabled={updateMutation.isPending}>
                    Save
                  </Button>
                </DrawerFooter>
              </form>
            </DrawerContent>
          </Drawer>
        </div>
      </div>
      {isLoading ? (
        <p className="text-muted-foreground">Loading…</p>
      ) : (
        <DataTable columns={columns} data={documents} />
      )}
      <Drawer
        open={markdownDrawerOpen}
        onOpenChange={setMarkdownDrawerOpen}
        swipeDirection="right"
      >
        <DrawerContent>
          <DrawerHeader>
            <DrawerTitle>{markdownDocName}</DrawerTitle>
          </DrawerHeader>
          <div
            className="flex-1 overflow-y-auto p-4 text-sm [&_code]:rounded [&_code]:bg-muted [&_code]:px-1 [&_code]:py-0.5 [&_h1]:mt-4 [&_h1]:text-xl [&_h1]:font-semibold [&_h2]:mt-4 [&_h2]:text-lg [&_h2]:font-semibold [&_h3]:mt-3 [&_h3]:text-base [&_h3]:font-semibold [&_li]:ml-4 [&_ol]:list-decimal [&_p]:my-2 [&_pre]:overflow-x-auto [&_pre]:rounded [&_pre]:bg-muted [&_pre]:p-2 [&_ul]:list-disc"
          >
            <Markdown>{markdownContent}</Markdown>
          </div>
        </DrawerContent>
      </Drawer>
    </div>
  )
}
