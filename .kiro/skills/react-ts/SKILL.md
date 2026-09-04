---
name: react-ts
description: Review and improve React + TypeScript code quality in web/src/ (add "fix" to apply changes)
---

Review `web/src/` for React and TypeScript code quality issues.

## Checks

### TypeScript
- `any` types — replace with proper types or `unknown`
- Missing return types on non-trivial functions
- Props not typed (missing interface or inline type)
- Unnecessary type assertions (`as SomeType`) that could be avoided with proper typing
- Non-null assertions (`!`) without a clear reason

### React
- Class components — convert to functional
- State or side effects not using hooks
- Components doing more than one job — flag for extraction
- Reusable logic not extracted into a custom hook
- Missing or incorrect dependency arrays in `useEffect` / `useCallback` / `useMemo`
- `key` prop missing or using array index on dynamic lists

### TanStack Query
- Server state stored in Zustand instead of Query
- Query keys defined as inline literals instead of constants (typo risk)
- Missing `onError` handler on mutations that mutate visible data
- `useQuery` used for mutations (POST/PUT/DELETE)

### TanStack Router
- `useSearchParams` from React used instead of TanStack Router's typed `useSearch`
- Route params accessed without using typed `useParams`
- `routeTree.gen.ts` manually edited

### Zustand
- Server/remote data stored in a Zustand store (belongs in TanStack Query)
- Store too broad — multiple unrelated domains in one store

### Forms
- Form without Zod schema validation
- Zod schema defined but not connected to React Hook Form via `zodResolver`
- Manual `onChange` state management instead of `react-hook-form` `register` / `Controller`

### Styling
- Inline `style={{}}` props (use Tailwind classes)
- `tailwind.config.ts` or `tailwind.config.js` present (v4 uses CSS `@theme` only)
- Custom components placed in `src/components/ui/` (reserved for shadcn only)

### General
- Commented-out code blocks
- Unused imports
- `console.log` statements left in
- `@ts-ignore` or `@ts-expect-error` without explanation

---

## Mode

**Default (no argument / "check"):**
- Scan `web/src/` and report all findings
- Group findings by category
- Do not modify any files

**If asked to "fix":**
- First report all findings grouped by category with numbered items
- Ask: "Which items would you like me to fix? (enter numbers like 1,3,5 or 'all' or 'none')"
- Wait for confirmation before changing anything
- Apply only the approved fixes
- Report what changed
