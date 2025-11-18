# Scale66 Frontend

AI-powered social media content generation platform built with Next.js App Router.

## Project Overview

Scale66 helps businesses generate engaging social media content using AI. The MVP focuses on Instagram and TikTok carousel post generation with an intuitive canvas-based AI chat interface.

### Tech Stack

- **Framework:** Next.js (App Router with Turbopack)
- **Language:** TypeScript (Strict Mode)
- **Styling:** CSS Modules
- **Authentication:** Firebase Auth (configured)
- **Database:** Firebase Firestore
- **Email:** Resend
- **Payment:** Stripe
- **Deployment:** Firebase Hosting
- **Icons:** React Icons
- **SEO:** Next-SEO

## Architecture

This project follows a **feature-based architecture**. Key principles:

- **Feature Co-location:** Everything a feature needs lives together
- **Type Safety First:** TypeScript strict mode with comprehensive type definitions
- **Service Abstraction:** All API calls through dedicated service layer
- **Component Hierarchy:** UI primitives → Common composites → Feature-specific components

### Directory Structure

```
src/
├── app/                        # Next.js App Router
│   ├── (landing)/             # Public marketing pages
│   ├── (auth)/                # Authentication pages
│   ├── (app)/                 # Protected app pages
│   ├── layout.tsx             # Root layout
│   ├── globals.css            # Global styles
│   └── api/                   # API routes
├── components/
│   ├── ui/                    # Primitive components (Button, Input, Modal, etc.)
│   ├── common/                # Shared composites (LoadingSpinner, ErrorBoundary, etc.)
│   └── layouts/               # Layout components (LandingLayout, AppLayout, AuthLayout)
├── features/                   # Feature modules (see below)
├── lib/                       # Third-party integrations (Firebase configured, Stripe planned)
├── hooks/                     # Shared custom hooks
├── context/                   # React contexts (Auth, Brand, Theme)
├── services/api/              # API service layer
├── types/                     # Shared TypeScript types
├── utils/                     # Utility functions
├── data/                      # Static data/constants
├── config/                    # App configuration
├── styles/                    # Global styles (variables, utilities)
└── middleware.ts              # Route protection middleware
```

## Feature Status

| Feature           | Status      | Backend Deps       | Notes                                       |
| ----------------- | ----------- | ------------------ | ------------------------------------------- |
| **Landing Pages** | ✅ Complete | None               | Migrated from Pages Router                  |
| **Auth**          | 🔨 Setup    | `/api/auth/*`      | Login/Signup/OAuth ready for implementation |
| **Onboarding**    | 🔨 Setup    | `/api/onboarding`  | 6-step wizard structure                     |
| **Payment**       | 🔨 Setup    | Stripe API         | Structure ready, Stripe integration needed  |
| **Dashboard**     | 🔨 Setup    | `/api/campaigns`   | Main landing page after login               |
| **Campaigns**     | 🔨 Setup    | `/api/campaigns/*` | Campaign management grid                    |
| **Canvas**        | 🔨 Setup    | `/api/ai/generate` | **CORE FEATURE** - AI chat interface        |
| **Posting**       | 🔨 Setup    | Social media APIs  | Post to Instagram/TikTok                    |
| **Brand Kit**     | 🔨 Setup    | `/api/brand/*`     | Brand profile management                    |
| **Settings**      | 🔨 Setup    | `/api/user/*`      | Account settings                            |

**Legend:**

- ✅ Complete - Fully functional
- 🔨 Setup - Structure created, needs implementation
- ⏳ Pending - Not yet started

## Getting Started

```bash
# Install
npm install

# Environment variables (.env.local)
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
NEXT_PUBLIC_FIREBASE_APP_ID=
NEXT_PUBLIC_API_BASE_URL=
RESEND_API_KEY=

# Run dev server
npm run dev

# Build
npm run build
npm start

# Deploy
firebase deploy --only hosting
```

## Development Guide

### Feature Structure

```
src/features/[feature-name]/
├── components/    # Feature components
├── hooks/         # Custom hooks
├── services/      # API calls
├── types/         # TypeScript types
└── index.ts       # Barrel exports
```

### Development Flow

1. Define types first (`types/[feature].types.ts`)
2. Create service layer (`services/[feature].service.ts`)
3. Build components with CSS Modules
4. Create custom hooks if needed
5. Add barrel exports

### Component Hierarchy

- **UI** (`components/ui/`) - Primitive, reusable, no business logic
- **Common** (`components/common/`) - Shared composites (LoadingSpinner, ErrorBoundary)
- **Feature** (`features/[feature]/components/`) - Feature-specific

### Key Rules

- All API calls through service layer
- TypeScript strict mode, no `any` types
- Use path aliases (`@/components/ui`, `@/hooks`, etc.)
- CSS Modules with variables from `styles/variables.css`
- Type all functions with return types

## Path Aliases

All paths use `@/` prefix: `@/components/ui`, `@/hooks`, `@/features/auth`, `@/lib`, `@/types`, `@/utils`, `@/data`, `@/config`, `@/services`, `@/context`, `@/styles`

## Backend API Endpoints

```
Auth:        POST /api/auth/{login,signup,logout}, GET /api/auth/me
Campaigns:   GET,POST /api/campaigns, GET,PUT,DELETE /api/campaigns/:id
AI (CORE):   POST /api/ai/{generate,variations,enhance-prompt}
Brand:       GET,PUT /api/brand, POST /api/brand/assets
Posting:     POST /api/post/{instagram,tiktok}, GET /api/post/status/:id
Payment:     POST /api/payment/{create-checkout,webhook}, GET /api/payment/subscription
```

## Workflow

**Branch naming:** `frontend/{feature,fix,refactor}/[name]`

**Code review checklist:**

- TypeScript strict mode passing
- No console.log statements
- Path aliases used
- Service layer for API calls
- Proper interfaces and types

## Implementation Roadmap

**Core:** Auth (Firebase + OAuth) → Onboarding (6-step wizard) → Brand Kit → Canvas (AI chat interface - CORE FEATURE) → Dashboard → Campaigns → Payment (Stripe)

**Additional:** Posting (Instagram/TikTok) → Settings → Testing
