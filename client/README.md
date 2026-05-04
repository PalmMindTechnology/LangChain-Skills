# Skills Agent Chat — Next.js Frontend

A production-grade chat interface for the Skills Agent FastAPI backend (LangGraph).

---

## Prerequisites

- **Node.js** v18+ — https://nodejs.org
- **npm** v9+ (bundled with Node) or **pnpm** / **yarn**
- Your FastAPI Skills Agent backend running (default: `http://localhost:8089`)

---

## Installation

### 1. Clone / copy the project

```bash
cd skills-agent-chat
```

### 2. Install dependencies

```bash
npm install
```

Or with pnpm:
```bash
pnpm install
```

Or with yarn:
```bash
yarn install
```

### 3. Configure environment

```bash
cp .env.local.example .env.local
```

Edit `.env.local` and set your backend URL:

```
NEXT_PUBLIC_API_URL=http://localhost:8089
```

---

## Running the Dev Server

```bash
npm run dev
```

Open http://localhost:3000 in your browser.

---

## Building for Production

```bash
npm run build
npm start
```

---

## Project Structure

```
skills-agent-chat/
├── app/
│   ├── layout.tsx       # Root layout (fonts, global styles)
│   ├── page.tsx         # Main chat page
│   └── globals.css      # Global CSS & design tokens
├── components/
│   ├── MessageBubble.tsx  # Individual chat message
│   ├── ChatInput.tsx      # Input textarea + controls
│   ├── StatusBar.tsx      # Health check + thread ID
│   └── EmptyState.tsx     # Welcome screen with suggestions
├── hooks/
│   └── useChat.ts         # Core chat state + API calls
├── lib/
│   └── api.ts             # Typed API client (chat, stream, health)
├── types/
│   └── chat.ts            # Shared TypeScript types
└── .env.local             # Your local environment config
```

---

## Features

- **Streaming & non-streaming** modes (toggle in the input bar)
- **Thread persistence** via `sessionStorage` — same conversation survives page reloads
- **"New thread"** button to start a fresh conversation
- **Live health indicator** — polls `/health` every 15s
- **Skill badges** — shows `loaded_skills` returned by the agent
- **Error handling** — displays error messages inline with distinct styling
