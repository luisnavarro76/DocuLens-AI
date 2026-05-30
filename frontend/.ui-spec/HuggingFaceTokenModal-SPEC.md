---
phase: HuggingFaceTokenModal
status: draft
design_system: shadcn/ui (base-nova style, @base-ui/react primitives)
icon_library: lucide-react
---

# UI-SPEC: HuggingFaceTokenModal

## 1. Component API

### Export Signature

```tsx
// Default export
export default function HuggingFaceTokenModal(): React.ReactNode
```

### Props Interface

```tsx
interface HuggingFaceTokenModalProps {
  /** Optional: pre-fill token (e.g. from existing hf_token on AuthUser) */
  initialToken?: string;
  /** Trigger element override (default renders a dropdown-menu item) */
  children?: React.ReactNode;
}

export default function HuggingFaceTokenModal({
  initialToken,
  children,
}: HuggingFaceTokenModalProps): React.ReactNode
```

> **Design Decision:** `initialToken` is sourced from `useAuthStore`'s `user.hf_token` — it is **not** passed as a required prop. The store is read inside the component. The prop exists only for testing/edge-case override.

### Internal State (not exposed)

| State | Type | Default | Description |
|-------|------|---------|-------------|
| `inputToken` | `string` | `initialToken ?? ""` | Current input value |
| `saving` | `boolean` | `false` | True while `setHfToken()` API call is in-flight |
| `error` | `string \| null` | `null` | Error message from failed save |
| `success` | `boolean` | `false` | True briefly after successful save |
| `showToken` | `boolean` | `false` | Toggle password/plaintext visibility |

## 2. Visual Design

### Dialog Structure (same as ApiKeyManager.tsx pattern)

```
┌──────────────────────────────────────────────┐
│  [X] (close button, absolute top-right)       │
│                                                │
│  ┌─ DialogHeader ────────────────────────────┐ │
│  │  🤗 HuggingFace Token                     │ │ ← DialogTitle (text-2xl, font-bold, tracking-tight)
│  │  Enter your HuggingFace API token to      │ │ ← Description (text-sm, text-muted-foreground)
│  │  enable inference endpoints and model     │ │
│  │  access.                                  │ │
│  └───────────────────────────────────────────┘ │
│                                                │
│  ┌─ Input Section ───────────────────────────┐ │
│  │  Token                                     │ │ ← Label (text-sm font-medium)
│  │  ┌──────────────────────────────────┐ [👁] │ │ ← Input (type=password / text) + toggle button
│  │  │ hf_...                            │      │ │
│  │  └──────────────────────────────────┘      │ │
│  │                                             │ │
│  │  ┌─ Link ───────────────────────────────┐  │ │
│  │  │ 🔗 Get your token from HF Settings   │  │ │ ← External link, opens new tab
│  │  └──────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────┘ │
│                                                │
│  ┌─ Error Banner (conditional) ──────────────┐ │
│  │  ⚠️ Invalid token or API failure. Retry?  │ │ ← Alert style
│  └─────────────────────────────────────────────┘ │
│                                                │
│  ┌─ DialogFooter ────────────────────────────┐ │
│  │            [Cancel]  [Save Token]          │ │ ← Button variant="outline" + Button variant="default"
│  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

### Styling Tokens (directly from existing patterns)

| Element | Classes | Source |
|---------|---------|--------|
| Dialog wrapper | `Dialog` from `@/components/ui/dialog` | Existing component |
| DialogContent | `max-w-md sm:rounded-2xl border-border/40 p-6 md:p-8 bg-background/95 backdrop-blur-xl shadow-2xl` | Exact copy from ApiKeyManager pattern |
| DialogHeader | `DialogHeader` with `gap-1` (tighter than default `gap-2`) | Custom refinement |
| DialogTitle | `text-2xl font-bold tracking-tight` with emoji prefix | ApiKeyManager pattern |
| Description | `text-sm text-muted-foreground mt-1.5` | ApiKeyManager pattern |
| Label | `text-sm font-medium text-foreground/80` | Inferred from layout |
| Input | `Input` component, `w-full` with `pr-10` (for toggle button) | Input component + padding |
| Toggle button | `Button variant="ghost" size="icon-xs"` positioned absolutely inside input wrapper | Custom |
| External link | `text-xs text-muted-foreground hover:text-primary underline-offset-2 transition-colors inline-flex items-center gap-1` | Custom |
| Error banner | `p-4 border border-destructive/30 bg-destructive/5 rounded-xl text-sm text-destructive flex items-start gap-2` | Inferred from destructive pattern |
| Success banner | `p-4 border border-primary/20 bg-primary/5 rounded-xl text-sm text-primary flex items-start gap-2` | Inferred from ApiKeyManager newKey banner |
| DialogFooter | `DialogFooter` with `showCloseButton={false}` and custom Cancel + Save buttons | DialogFooter component |

### Spacing

| Context | Value | Notes |
|---------|-------|-------|
| Dialog padding | `p-6 md:p-8` | Matches ApiKeyManager |
| Between DialogHeader and Input | `mt-6` (gap-6) | Via DialogContent `gap-4` + manual spacing |
| Input to link | `mt-2` | Tight spacing |
| Link to error/success | `mt-4` | If error/success present |
| Footer buttons gap | `gap-2` | DialogFooter default |
| Icon-to-text gap | `gap-1.5` or `mr-2` | Button/icon pattern |

### Color Contract

| Role | Token | Usage |
|------|-------|-------|
| Surface (60%) | `bg-background/95` | Dialog background (glass) |
| Card (30%) | `border-border/40` | Dialog border |
| Input border | `border-input` | Input default state |
| Input focus | `focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50` | Input focus ring |
| Accent (10%) | `bg-primary text-primary-foreground` | "Save Token" button |
| Destructive | `text-destructive bg-destructive/5 border-destructive/30` | Error banner |
| Success | `text-primary bg-primary/5 border-primary/20` | Success banner (reuse primary) |
| Muted text | `text-muted-foreground` | Description, external link |
| Link hover | `hover:text-primary` | External link hover |

### Typography

| Element | Size | Weight | Line Height | Color |
|---------|------|--------|-------------|-------|
| DialogTitle | `text-2xl` (1.5rem / 24px) | `font-bold` (700) | `tracking-tight` | `text-foreground` |
| Description | `text-sm` (0.875rem / 14px) | `font-normal` (400) | Default | `text-muted-foreground` |
| Label | `text-sm` (0.875rem / 14px) | `font-medium` (500) | Default | `text-foreground/80` |
| Input text | `text-base md:text-sm` | `font-normal` (400) | Default | `text-foreground` |
| Link | `text-xs` (0.75rem / 12px) | `font-normal` (400) | Default | `text-muted-foreground` |
| Error text | `text-sm` (0.875rem / 14px) | `font-medium` (500) | Normal | `text-destructive` |
| Button label | `text-sm` (0.875rem / 14px) | `font-medium` (500) | Default | Per button variant |

## 3. States

### 3.1 Idle (default, modal open)

- Dialog visible with shimmer entrance animation (`.data-open:animate-in data-open:fade-in-0 data-open:zoom-in-95`)
- Input field empty (or pre-filled with `hf_token` from store, masked)
- "Save Token" button enabled if input is non-empty, disabled if empty
- "Cancel" button always enabled
- No error/success banners visible
- Focus automatically moves to the Input field on open

### 3.2 Loading (saving token)

- "Save Token" button shows a spinner and becomes `disabled`
- Button label changes to "Saving..."
- Input field becomes `disabled` (pointer-events-none)
- Cancel button remains enabled (allows dismissal during save)
- Error/success banners hidden (cleared)
- Button uses: `<Loader2 className="w-4 h-4 animate-spin" />` icon from lucide-react

### 3.3 Error (invalid token / API failure)

- Error banner appears above DialogFooter, with fade-in animation
- Banner content shows the error message from the API (via `useAuthStore().setHfToken` rejection)
- "Save Token" button re-enabled (user can retry)
- Input remains editable (user can correct the token)
- Banner auto-dismisses on next successful save or on modal close
- Banner pattern:
  ```tsx
  <div className="p-4 border border-destructive/30 bg-destructive/5 rounded-xl text-sm text-destructive flex items-start gap-2 animate-in fade-in slide-in-from-top-2 duration-200">
    <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
    <span>{error}</span>
  </div>
  ```

### 3.4 Success (token saved)

- Success banner appears briefly: "Token saved successfully"
- Banner auto-dismisses after 2 seconds
- After success, the `AuthUser` in the store is updated (with `hf_token` populated)
- Input retains the token (masked) so user can see it's set
- "Save Token" button re-enabled
- After 1.5s delay, the dialog auto-closes (clean UX — user confirms save then modal dismisses)
- Success banner pattern:
  ```tsx
  <div className="p-4 border border-primary/20 bg-primary/5 rounded-xl text-sm text-primary flex items-start gap-2 animate-in fade-in slide-in-from-top-2 duration-200">
    <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" />
    <span>Token saved successfully</span>
  </div>
  ```

### 3.5 Token Already Set (existing token detected)

- When `user.hf_token` exists in the store, the Input is pre-filled and masked
- The "Save Token" button label changes to "Update Token"
- A small badge or indicator shows: "Token configured" with a check icon
- User can still save a new token (overwrite) or clear and re-enter

### State Machine

```
Idle ──(click Save)──→ Loading ──(API success)──→ Success ──(1.5s timeout)──→ Dialog Close
                           │
                           └──(API error)──→ Error ──(edit input / click Save)──→ Loading (retry)
```

## 4. Behavior

### 4.1 Token Masking

- By default, input uses `type="password"` to mask the token
- A visibility toggle button (eye icon) is positioned absolutely inside the input, right-aligned
  - `Eye` icon from lucide-react when masked
  - `EyeOff` icon from lucide-react when visible
- Button is `variant="ghost" size="icon-xs"` with class `absolute right-2 top-1/2 -translate-y-1/2`
- The input wrapper needs `relative` positioning

### 4.2 Input Wrapper Structure

```tsx
<div className="relative">
  <Input
    type={showToken ? "text" : "password"}
    value={inputToken}
    onChange={(e) => setInputToken(e.target.value)}
    placeholder="hf_..."
    className="pr-10"
    disabled={saving}
    aria-label="HuggingFace API Token"
  />
  <Button
    variant="ghost"
    size="icon-xs"
    className="absolute right-2 top-1/2 -translate-y-1/2"
    onClick={() => setShowToken(!showToken)}
    type="button"
    aria-label={showToken ? "Hide token" : "Show token"}
    disabled={saving}
  >
    {showToken ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
  </Button>
</div>
```

### 4.3 External Link

- Renders as: `🔗 Get your API token from HuggingFace Settings`
- Link target: `https://huggingface.co/settings/tokens`
- Opens in new tab: `target="_blank" rel="noopener noreferrer"`
- Styled as external link (no underlines by default, underline on hover)

### 4.4 Save Action

1. User clicks "Save Token" (or "Update Token")
2. Component sets `saving = true`, `error = null`, `success = false`
3. Calls `useAuthStore.getState().setHfToken(inputToken.trim())`
4. On success:
   - `saving = false`
   - `success = true`
   - Show success banner
   - Auto-close dialog after 1.5s
5. On error:
   - `saving = false`
   - `error = error.message` (from the API exception)
   - Show error banner

### 4.5 Cancel / Close

- X button in dialog header calls `onOpenChange(false)`
- Cancel button in footer calls `onOpenChange(false)`
- Escape key dismisses (native Dialog behavior)
- Click outside (backdrop click) dismisses (native Dialog behavior)
- On close: reset internal state (clear error, success banners)

### 4.6 Existing Token Indicator

When `user.hf_token` is a non-empty string:
- Show label: `"Token"` with a small green dot or check icon next to it
- Pre-fill `inputToken` with the existing token value
- Change button label from "Save Token" to "Update Token"
- The "Update Token" button title text: "Replace existing token with a new one"

## 5. Accessibility

| Requirement | Implementation |
|-------------|---------------|
| Focus on open | `Dialog` handles focus — auto-focuses first focusable element inside content |
| Focus trap | Native to `Dialog` from `@base-ui/react` |
| Escape dismiss | Native to `Dialog` |
| ARIA dialog role | `Dialog` from `@/components/ui/dialog` sets `role="dialog"` + `aria-modal="true"` |
| ARIA label | `DialogTitle` provides `aria-labelledby` automatically |
| ARIA description | `DialogDescription` provides `aria-describedby` automatically |
| Input label | `<label>` element (not just placeholder) — `htmlFor` referencing input `id` |
| Toggle button | `aria-label="Show token"` / `aria-label="Hide token"` |
| Error announcement | `aria-live="polite"` on error banner for screen reader announcement |
| Success announcement | `aria-live="polite"` on success banner |
| Loading state | Button `disabled` + `aria-busy="true"` while saving |
| Keyboard nav | Tab through: X close → Input → Toggle visibility → Link → Cancel → Save |
| Reduced motion | `duration-100` on Dialog + `motion-reduce:transition-none` on animations |

### Focus Management Details

On open:
1. Input field receives focus (via `autoFocus` on Input — the first focusable element)
2. If token is already set, focus still goes to Input (user can type a new token immediately)

On close:
1. Focus returns to the trigger element (native Dialog behavior via @base-ui/react)

### Screen Reader Copy

- Title: "HuggingFace Token"
- Description: "Enter your HuggingFace API token to enable inference endpoints and model access."
- Input label: "HuggingFace API Token"
- Toggle: "Show token" / "Hide token"
- Link: "Get your API token from HuggingFace Settings"
- Cancel button: "Cancel"
- Save button: "Save Token" / "Update Token" / "Saving..."

## 6. Responsive Behavior

| Breakpoint | Behavior |
|------------|----------|
| Mobile (< 640px) | Dialog fills `max-w-[calc(100%-2rem)]` — constrained by Dialog default. Content uses `p-6` |
| Tablet (640px+) | Dialog at `max-w-md` (28rem / 448px). Content uses `md:p-8` |
| Desktop (1024px+) | Same as tablet — modal is fixed-width at `max-w-md` |

- Button layout in footer: `flex-col-reverse` on mobile (Close above Save), `flex-row` on tablet+ (Cancel left, Save right)
- Input width always `w-full` within the dialog container

## 7. Copywriting

| Element | Copy | Context |
|---------|------|---------|
| Dialog title | `🤗 HuggingFace Token` | Modal header |
| Description | `Enter your HuggingFace API token to enable inference endpoints and model access.` | Subtitle beneath title |
| Input label | `Token` | Label above input |
| Input placeholder | `hf_...` | Placeholder inside empty input |
| Toggle show | `Show token` | aria-label when masked |
| Toggle hide | `Hide token` | aria-label when visible |
| External link | `Get your API token from HuggingFace Settings` | Link text |
| Cancel | `Cancel` | Footer cancel button |
| Save (no token) | `Save Token` | Primary CTA when no existing token |
| Save (has token) | `Update Token` | Primary CTA when token exists |
| Saving | `Saving...` | Loading state button text |
| Success | `Token saved successfully` | Success banner |
| Error | Dynamic from API | Error banner (e.g. "Invalid token format") |
| Already set | `Token configured` | Small indicator element |

## 8. Dependencies

### Required shadcn/ui Components

| Component | Import Path | Usage |
|-----------|-------------|-------|
| `Dialog`, `DialogTrigger`, `DialogContent`, `DialogHeader`, `DialogTitle`, `DialogDescription`, `DialogFooter` | `@/components/ui/dialog` | Modal shell |
| `Input` | `@/components/ui/input` | Token text entry |
| `Button` | `@/components/ui/button` | Save, Cancel, visibility toggle |

### Lucide Icons

| Icon | Import | Usage |
|------|--------|-------|
| `Eye` | `lucide-react` | Show token button |
| `EyeOff` | `lucide-react` | Hide token button |
| `AlertCircle` | `lucide-react` | Error banner icon |
| `CheckCircle2` | `lucide-react` | Success banner icon |
| `Loader2` | `lucide-react` | Loading spinner |
| `ExternalLink` | `lucide-react` | External link icon (optional) |

### External Dependencies (already in project)

| Dependency | Version | Usage |
|------------|---------|-------|
| `zustand` | `^5.0.13` | `useAuthStore` for user state and `setHfToken` |
| `@/lib/api` | project-local | API client (used by `setHfToken` inside store) |
| `@/lib/utils` | project-local | `cn()` for class merging |
| `@/store/auth-store` | project-local | `useAuthStore` + `AuthUser` type |

### What NOT to add

- No new npm packages needed (all dependencies already present)
- No new shadcn/ui components to install (Dialog, Input, Button already initialized)

## 9. File Placement

### New File

```
frontend/src/components/auth/HuggingFaceTokenModal.tsx
```

### File Location Rationale

- Co-located with `ApiKeyManager.tsx` and `GoogleSignInButton.tsx` in `components/auth/`
- Follows the established pattern for auth-related UI components

### Trigger Integration (future)

The modal's trigger will be wired into the **Settings dropdown** (or **User menu**), matching how `ApiKeyManager` is triggered via `DialogTrigger` rendered as a dropdown menu item:

```tsx
<DialogTrigger
  render={
    <button className="flex w-full cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground">
      <Key className="mr-2 h-4 w-4" />
      <span>HuggingFace Token</span>
    </button>
  }
/>
```

## 10. Edge Cases & Notes

| Edge Case | Handling |
|-----------|----------|
| Empty input save attempt | Button is `disabled` when `inputToken.trim() === ""` |
| Whitespace-only token | Trimmed before send: `inputToken.trim()` |
| Very long token | Input handles via `w-full` + text overflow (no truncation) |
| Multiple rapid saves | Button disabled during `saving`, subsequent clicks ignored |
| Token shows as masked | `type="password"` with `font-mono` for consistent character width |
| Paste from clipboard | Standard browser paste works — no custom handlers needed |
| Backend validation error | Displayed verbatim in error banner from API error message |
| Token already configured | Pre-fill input, show "Update Token" label, small "configured" indicator |
| Dialog close during save | Close is still allowed — but API call completes in background (fire-and-forget) |
| Network error | API client returns `"Could not connect to the server"` — displayed in error banner |

## 11. Testing Guidance (for QA)

| Test Case | Expected |
|-----------|----------|
| Open modal | Dialog appears with animation, focus on input |
| Type a token | Characters masked by default |
| Toggle visibility | Characters shown/hidden, aria-label updates |
| Click external link | Opens `https://huggingface.co/settings/tokens` in new tab |
| Save with empty input | Button disabled, no action |
| Save valid token | Loading state, success banner, auto-close after 1.5s |
| Save invalid token | Loading state, error banner with API message |
| Cancel during save | Dialog closes, API call completes in background |
| Re-open after save | Input pre-filled with stored token |
| Escape key | Dialog closes, state resets |
| Tab navigation | Focus cycles through all interactive elements |
| Screen reader | Title, description, and input label announced |
| Mobile viewport | Dialog is full-width with padding `p-6` |
