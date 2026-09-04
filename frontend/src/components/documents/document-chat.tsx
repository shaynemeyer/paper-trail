import { useMutation } from '@tanstack/react-query'
import { useEffect, useRef, useState, type FormEvent } from 'react'
import { toast } from 'sonner'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { chatApi, type Document } from '@/lib/api'

const chatMessageSchema = z.object({
  message: z.string().trim().min(1, 'Enter a question.'),
})

type ChatMessage = {
  id: number
  role: 'user' | 'assistant'
  content: string
}

type DocumentChatProps = {
  document: Document
}

export function DocumentChat({ document }: DocumentChatProps) {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const nextMessageId = useRef(0)
  const messageEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages])

  const appendMessage = (role: ChatMessage['role'], content: string) => {
    const nextMessage = { id: nextMessageId.current, role, content }
    nextMessageId.current += 1
    setMessages((current) => [...current, nextMessage])
  }

  const chatMutation = useMutation({
    mutationFn: (question: string) => chatApi.ask(document.id, question),
    onSuccess: (response) => appendMessage('assistant', response.answer),
    onError: (err: Error) => toast.error(err.message),
  })

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const result = chatMessageSchema.safeParse({ message })
    if (!result.success) {
      toast.error(result.error.issues[0].message)
      return
    }

    appendMessage('user', result.data.message)
    chatMutation.mutate(result.data.message)
    setMessage('')
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div
        className="min-h-0 flex-1 space-y-3 overflow-y-auto p-4"
        aria-live="polite"
        role="log"
      >
        {messages.length === 0 ? (
          <p className="text-muted-foreground">
            Ask a question about {document.name} to start the conversation.
          </p>
        ) : (
          messages.map((chatMessage) => (
            <div
              key={chatMessage.id}
              className={
                chatMessage.role === 'user'
                  ? 'ml-8 rounded-lg bg-primary px-3 py-2 text-primary-foreground'
                  : 'mr-8 rounded-lg bg-muted px-3 py-2 text-foreground'
              }
            >
              <p className="mb-1 text-xs font-medium">
                {chatMessage.role === 'user' ? 'You' : 'Paper Trail'}
              </p>
              <p className="whitespace-pre-wrap">{chatMessage.content}</p>
            </div>
          ))
        )}
        <div ref={messageEndRef} aria-hidden="true" />
      </div>

      <form className="space-y-2 border-t p-4" onSubmit={handleSubmit}>
        <Textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder={`Ask about ${document.name}`}
          aria-label={`Question about ${document.name}`}
          disabled={chatMutation.isPending}
        />
        <Button type="submit" className="w-full" disabled={chatMutation.isPending}>
          {chatMutation.isPending ? 'Asking…' : 'Ask question'}
        </Button>
      </form>
    </div>
  )
}
