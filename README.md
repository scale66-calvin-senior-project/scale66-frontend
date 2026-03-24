# Scale66 Frontend

Scale66 is an AI-powered social media content platform that generates branded carousel posts for Instagram, TikTok, LinkedIn, and Twitter. Users configure a brand kit, create campaigns, and generate complete carousel content — captions, images, and slide layouts — through an AI pipeline in the backend.

## Features

- **AI Carousel Generation** — Generate fully designed carousels from a text prompt, with captions and images produced by an AI pipeline
- **Brand Kit** — Configure brand name, niche, style, and customer pain points to keep all content on-brand
- **Campaigns** — Organise content into campaigns and manage posts across multiple social platforms
- **Canvas** — Core content editor for reviewing, editing, and managing AI-generated carousel posts and variations
- **Onboarding** — 7-step guided setup wizard to configure a brand kit and connect social accounts
- **Authentication** — Supabase Auth with email/password, email verification, and OAuth social login
- **Payments** — Stripe-powered subscription and transaction management
- **Settings** — Account and profile management

## Tech Stack

| Layer          | Technology                              |
| -------------- | --------------------------------------- |
| Framework      | Next.js 15 (App Router + Turbopack)     |
| Language       | TypeScript (Strict Mode)                |
| Styling        | CSS Modules                             |
| Authentication | Supabase Auth (JWT)                     |
| Backend API    | FastAPI (Python) via Axios              |
| Payments       | Stripe                                  |
| Package Manager | npm                                    |

## Getting Started

```bash
npm install
cp .env.example .env
# Edit .env with your Supabase credentials and backend API URL
npm run dev
# http://localhost:3000
```

```bash
npm run build && npm start  # Production
npm run type-check          # Type checking
npm run lint                # Linting
```

### Environment Variables

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...  # Optional
```

## Architecture

The frontend is organized into **feature modules** — each feature owns its components, hooks, services, and types. All backend communication goes through a centralized Axios service layer that automatically attaches Supabase JWT tokens to every request.

```
src/
├── app/                    # Next.js App Router (route groups)
│   ├── (landing)/          # Public marketing pages
│   ├── (auth)/             # Login, signup, email verification
│   └── (app)/              # Protected app pages
│       ├── dashboard/
│       ├── welcome/        # Post-signup onboarding entry
│       ├── brand-kit/
│       ├── campaigns/
│       ├── canvas/[id]/    # AI canvas — core feature
│       ├── payment/
│       └── settings/
│
├── features/               # Feature modules (co-located components, hooks, services, types)
│   ├── auth/
│   ├── brand-kit/
│   ├── campaigns/
│   ├── canvas/             # AI carousel generation
│   ├── dashboard/
│   ├── landing/
│   ├── onboarding/
│   ├── payment/
│   ├── posting/
│   └── settings/
│
├── components/             # Shared UI (Button, Input, Card, Modal, layouts)
├── context/                # Auth, AuthModal, Brand, Theme providers
├── services/api/           # Axios client + JWT interceptors
├── hooks/                  # useAuth, useUser, useDebounce, useLocalStorage, useMediaQuery
├── lib/                    # Supabase and Stripe clients
├── types/                  # Shared TypeScript interfaces
└── middleware.ts           # Route protection
```

## Backend API

Base URL: `http://localhost:8000/api/v1`

```
Users:      GET, PUT  /users/me
Brand Kits: POST      /brand-kits
            GET, PUT  /brand-kits/me
Campaigns:  POST, GET /campaigns
            GET, PUT, DELETE /campaigns/{id}
Carousel:   POST      /campaigns/{id}/carousel       ← AI generation
Posts:      POST, GET /campaigns/{id}/posts
            GET, PUT, DELETE /posts/{id}
Variations: POST, GET /posts/{id}/variations
            GET, PUT, DELETE /posts/{id}/variations/{vid}
Social:     POST, GET /social-accounts
            GET, PUT, DELETE /social-accounts/{id}
Payments:   POST, GET /payments/transactions
            POST      /payments/webhook
```

See [README_API.md](README_API.md) for full API documentation.
