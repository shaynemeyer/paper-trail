import { KeyRound } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { clearToken, getToken, setToken } from '@/lib/api'

// Stand-in for a real login flow: paste a JWT from generate_token.py
export function DevSessionMenu() {
  const [open, setOpen] = useState(false)
  const [token, setTokenValue] = useState(getToken() ?? '')

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={
          <Button variant="ghost" size="icon" title="Dev session">
            <KeyRound className="size-4" />
            <span className="sr-only">Dev session</span>
          </Button>
        }
      />
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Dev session</DialogTitle>
          <DialogDescription>
            Paste a JWT from <code>uv run scripts/generate_token.py admin</code> to test
            the API as that user.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-2">
          <Label htmlFor="dev-token">Token</Label>
          <Input
            id="dev-token"
            value={token}
            onChange={(e) => setTokenValue(e.target.value)}
            placeholder="eyJhbGciOi..."
          />
        </div>
        <DialogFooter>
          <Button
            variant="ghost"
            onClick={() => {
              clearToken()
              setTokenValue('')
              window.location.reload()
            }}
          >
            Clear
          </Button>
          <Button
            onClick={() => {
              setToken(token)
              window.location.reload()
            }}
          >
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
