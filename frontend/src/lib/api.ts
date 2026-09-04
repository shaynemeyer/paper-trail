// Relative default: works out of the box in the combined Docker image, where
// the backend serves the built frontend from the same origin under /api.
const API_URL = import.meta.env.VITE_API_URL ?? "/api"
const TOKEN_KEY = "pt_token"

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export interface CurrentUser {
  sub: string
  role: string
}

// Decodes the JWT payload for display only (name/role) -- not a signature check.
export function getCurrentUser(): CurrentUser | null {
  const token = getToken()
  if (!token) return null
  try {
    const payload = token.split(".")[1]
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"))
    const { sub, role } = JSON.parse(json)
    return sub && role ? { sub, role } : null
  } catch {
    return null
  }
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new ApiError(response.status, body?.detail ?? response.statusText)
  }

  if (response.status === 204) return undefined as T
  return response.json()
}

async function requestForm<T>(path: string, formData: FormData): Promise<T> {
  const token = getToken()
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  })
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new ApiError(response.status, body?.detail ?? response.statusText)
  }
  return response.json()
}

export type DocumentStatus = "draft" | "pending" | "approved"

export interface Document {
  id: number
  name: string
  description: string
  doctype: string
  document_source: string | null
  status: DocumentStatus
  created_at: string
  updated_at: string
}

export interface DocumentInput {
  name: string
  description: string
  doctype: string
  document_source?: string | null
  status: DocumentStatus
}

export interface UploadDocumentInput {
  file: File
  name: string
  description: string
  document_source?: string
  tags: string[]
}

export const documentsApi = {
  list: () => request<Document[]>("/documents"),
  create: (data: DocumentInput) =>
    request<Document>("/documents", { method: "POST", body: JSON.stringify(data) }),
  update: (id: number, data: DocumentInput) =>
    request<Document>(`/documents/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  remove: (id: number) => request<void>(`/documents/${id}`, { method: "DELETE" }),
  embed: (id: number) => request<Document>(`/documents/${id}/embed`, { method: "POST" }),
  search: (q: string) =>
    request<Document[]>(`/documents/search?q=${encodeURIComponent(q)}`),
  upload: (data: UploadDocumentInput) => {
    const formData = new FormData()
    formData.append("file", data.file)
    formData.append("name", data.name)
    formData.append("description", data.description)
    if (data.document_source) formData.append("document_source", data.document_source)
    formData.append("tags", data.tags.join(","))
    return requestForm<Document>("/documents/upload", formData)
  },
}

export type UserRole = "user" | "admin"

export interface User {
  id: number
  email: string
  name: string
  role: UserRole
  created_at: string
  updated_at: string
}

export interface UserInput {
  email: string
  name: string
  role: UserRole
}

export const usersApi = {
  list: () => request<User[]>("/users"),
  create: (data: UserInput) =>
    request<User>("/users", { method: "POST", body: JSON.stringify(data) }),
  update: (id: number, data: Partial<UserInput>) =>
    request<User>(`/users/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: number) => request<void>(`/users/${id}`, { method: "DELETE" }),
}
