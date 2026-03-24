# Scale66 Frontend

AI-powered social media content generation platform built with Next.js 15 and TypeScript. Very cool app

## Tech Stack

- **Framework:** Next.js 15 (App Router with Turbopack)
- **Language:** TypeScript (Strict Mode)
- **Styling:** CSS Modules
- **Authentication:** Supabase Auth (JWT tokens)
- **Backend API:** FastAPI (Python) via Axios
- **Payment:** Stripe
- **Email:** Resend
- **Package Manager:** npm

## Quick Start

```bash
# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials and backend API URL

# Run development server
npm run dev
# Server runs at http://localhost:3000

#cp the .env.example file
cp .env.example .env

# Build for production
npm run build
npm start
```

## File Structure

```
frontend/
├── package.json              # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
├── next.config.ts           # Next.js configuration
│
├── public/                  # Static assets
│   ├── favicon.ico
│   └── logo.png
│
└── src/
    ├── app/                 # Next.js App Router
    │   ├── (landing)/           # Public marketing pages
    │   │   ├── page.tsx             # Homepage
    │   │   ├── blog/
    │   │   ├── waitlist/
    │   │   ├── support/
    │   │   ├── privacy-policy/
    │   │   └── terms-conditions/
    │   │
    │   ├── (auth)/              # Authentication pages
    │   │   ├── login/
    │   │   └── signup/
    │   │
    │   └── (app)/               # Protected app pages
    │       ├── dashboard/
    │       ├── onboarding/
    │       ├── brand-kit/
    │       ├── campaigns/
    │       ├── canvas/[id]/     # CORE FEATURE - AI canvas
    │       └── settings/
    │
    ├── components/          # Reusable components
    │   ├── ui/                  # UI primitives (Button, Input, Card, etc.)
    │   ├── common/              # Shared components (LoadingSpinner, ErrorBoundary)
    │   └── layouts/             # Layout components (Landing, Auth, App)
    │
    ├── features/            # Feature-based modules
    │   ├── auth/                # Authentication
    │   ├── brand-kit/           # Brand management
    │   ├── campaigns/           # Campaign management
    │   ├── canvas/              # AI content generation (CORE)
    │   ├── dashboard/           # Dashboard
    │   ├── landing/             # Landing pages
    │   ├── onboarding/          # User onboarding
    │   ├── payment/             # Stripe integration
    │   ├── posting/             # Social media posting
    │   └── settings/            # User settings
    │
    ├── context/             # React Context providers
    │   ├── AuthContext.tsx      # Authentication state
    │   ├── BrandContext.tsx     # Brand kit state
    │   └── ThemeContext.tsx     # Theme state
    │
    ├── hooks/               # Shared custom hooks
    │   ├── useAuth.ts
    │   ├── useUser.ts
    │   ├── useDebounce.ts
    │   ├── useLocalStorage.ts
    │   └── useMediaQuery.ts
    │
    ├── services/            # API service layer
    │   └── api/
    │       ├── client.ts            # Axios client with JWT
    │       └── interceptors.ts      # Request/response interceptors
    │
    ├── lib/                 # Third-party integrations
    │   ├── supabase.ts          # Supabase client (auth only)
    │   └── stripe.ts            # Stripe client
    │
    ├── types/               # Shared TypeScript types
    │   ├── api.types.ts
    │   ├── user.types.ts
    │   ├── brand.types.ts
    │   ├── campaign.types.ts
    │   └── post.types.ts
    │
    ├── utils/               # Utility functions
    │   ├── constants.ts
    │   ├── formatters.ts
    │   ├── validation.ts
    │   ├── storage.ts
    │   └── date.ts
    │
    ├── data/                # Static data
    │   ├── brandStyles.ts
    │   ├── pricingPlans.ts
    │   └── socialPlatforms.ts
    │
    ├── config/              # App configuration
    │   ├── app.config.ts
    │   └── env.ts
    │
    ├── styles/              # Global styles
    │   ├── variables.css
    │   └── utilities.css
    │
    └── middleware.ts        # Route protection
```

## Architecture Overview

### App Router Structure

**Route Groups:**

- `(landing)` - Public marketing pages
- `(auth)` - Authentication pages
- `(app)` - Protected application pages

**Key Features:**

- Server Components by default
- Nested layouts for consistent structure
  - Automatic code splitting per route
- Built-in loading and error states

### Feature-Based Architecture

Each feature is self-contained with its own:

- `components/` - Feature-specific UI components
- `hooks/` - Feature-specific React hooks
- `services/` - Backend API calls
- `types/` - TypeScript type definitions
- `index.ts` - Public exports

**Benefits:**

- Clear feature boundaries
- Independent development
- Minimal merge conflicts
- Easy to locate code
- Scalable structure

### API Service Layer

**Centralized HTTP communication:**

- Axios client with automatic JWT injection
- Request interceptor adds auth token from Supabase
- Response interceptor handles errors globally
- Auto-redirect to login on 401 errors
- Type-safe requests and responses

**Critical:** All backend API calls go through the service layer. Supabase is used ONLY for authentication.

### Authentication Flow

1. User signs up/logs in via Supabase Auth
2. Supabase returns JWT token
3. Token stored in session (handled automatically)
4. API client includes token in all backend requests
5. Backend validates JWT and authorizes requests

**Supabase Usage:**

- Authentication only (signup, login, logout, OAuth)
- Session management with automatic refresh
- JWT token generation for backend API

**Backend API:**

- All database operations
- AI content generation
- File storage
- Social media integration
- Payment processing

## Feature Status

| Feature           | Status          | Dependencies          | Notes                                          |
| ----------------- | --------------- | --------------------- | ---------------------------------------------- |
| **Landing Pages** | Complete        | None                  | Hero, Features, Pricing, FAQ fully implemented |
| **Auth**          | Structure Ready | Supabase Auth         | Auth service and types defined, UI pending     |
| **Dashboard**     | Planned         | `/api/v1/campaigns`   | Structure in place, implementation pending     |
| **Onboarding**    | Planned         | `/api/v1/brand-kit`   | 6-step wizard structure defined                |
| **Brand Kit**     | Planned         | `/api/v1/brand-kit`   | Service and types ready                        |
| **Campaigns**     | Planned         | `/api/v1/campaigns/*` | Service layer defined                          |
| **Canvas**        | Planned         | `/api/v1/content/*`   | CORE FEATURE - AI chat interface               |
| **Posting**       | Planned         | `/api/v1/social/*`    | Social media posting                           |
| **Payment**       | Planned         | `/api/v1/payment/*`   | Stripe integration structure ready             |
| **Settings**      | Planned         | `/api/v1/posts/*`     | Account settings structure                     |

**Status Legend:**

- Complete: Fully functional
- Structure Ready: Architecture defined, implementation pending
- Planned: Not yet started

## Components

### UI Components (Design System)

Primitive, reusable components:

- Button (primary, secondary, ghost variants)
- Input, TextArea
- Card, Modal
- Dropdown, Checkbox
- Spinner

**Pattern:** Each component has `.tsx`, `.module.css`, and `index.ts`

### Common Components

Shared composite components:

- LoadingSpinner - Full-page loading state
- ErrorBoundary - Error handling wrapper
- EmptyState - Empty state displays
- SuccessMessage - Success notifications

### Layouts

- LandingLayout - Marketing pages with navbar/footer
- AuthLayout - Centered authentication forms
- AppLayout - App pages with sidebar/header

## Context Providers

**Global state management:**

- **AuthContext** - User authentication state

  - Current user and session
  - Auth status (isAuthenticated)
  - JWT token for API calls

- **BrandContext** - Active brand kit data

  - Fetched from backend API
  - Available across app

- **ThemeContext** - Theme preferences
  - Dark/light mode
  - User preferences

## Environment Variables

Required environment variables:

```env
# Backend API
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Supabase (Authentication only)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Optional
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

Copy `.env.example` and configure with your credentials.

## Development

### Adding Dependencies

```bash
npm install package-name          # Production dependency
npm install --save-dev package-name # Dev dependency
```

### Running the Server

```bash
# Development with hot reload
npm run dev

# Production build
npm run build
npm start

# Type checking
npm run type-check

# Linting
npm run lint
```

### Development Workflow

1. **Define types first** - Create TypeScript interfaces in `types/`
2. **Build service layer** - Create API service in feature's `services/`
3. **Create components** - Build UI components with CSS Modules
4. **Add hooks if needed** - Custom hooks for stateful logic
5. **Export publicly** - Add to `index.ts` for clean imports

### Component Hierarchy

- **UI** - Primitives with no business logic
- **Common** - Shared composites used across features
- **Feature** - Feature-specific components

### Key Development Rules

- All API calls through service layer (never direct fetch in components)
- TypeScript strict mode - no `any` types
- Use path aliases (`@/components/ui`, `@/hooks`, etc.)
- CSS Modules for component styling
- Type all function parameters and return values

## Path Aliases

Configure in `tsconfig.json`:

```
@/components  → src/components
@/features    → src/features
@/hooks       → src/hooks
@/lib         → src/lib
@/types       → src/types
@/utils       → src/utils
@/data        → src/data
@/config      → src/config
@/services    → src/services
@/context     → src/context
@/styles      → src/styles
```

## Backend API Integration

Base URL: `http://localhost:8000/api/v1`

**Available Endpoints:**

```
Brand Kit:   POST,GET,PUT,DELETE /brand-kit
Campaigns:   GET,POST /campaigns, GET,PUT,DELETE /campaigns/{id}
Content:     POST /content/generate, GET /content/status/{job_id}
Posts:       GET,POST /posts, GET,PUT,DELETE /posts/{id}
Social:      GET /social/connect/{platform}, GET /social/accounts
Payment:     POST /payment/create-checkout-session, POST /payment/webhook
```

**Authentication:** Frontend uses Supabase Auth directly. Backend validates JWT tokens in all requests.

## Implementation Status

**Complete:**

- Project structure and configuration
- Landing pages (Hero, Features, Pricing, FAQ)
- Component library (UI primitives and layouts)
- API service layer with interceptors
- TypeScript types and interfaces
- Route groups and layouts

**Structure Ready:**

- Feature modules (auth, dashboard, canvas, etc.)
- Supabase authentication integration
- Context providers
- Custom hooks
- Middleware for route protection

**In Progress:**

- Feature component implementation
- Backend API integration
- Form validation and error handling
- Loading and empty states

**Planned:**

- Canvas AI chat interface (CORE)
- Campaign management UI
- Brand kit configuration
- Social media posting flow
- Stripe payment integration

## Workflow

**Branch Naming:** `frontend/{feature,fix,refactor}/[name]`

**Code Review Checklist:**

- TypeScript strict mode passing
- No console.log statements
- Path aliases used correctly
- API calls through service layer
- Proper error handling
- Loading states implemented
- Mobile responsive design
- CSS Modules for styling

## Architecture Principles

1. **Feature Co-location** - Everything a feature needs lives together
2. **Type Safety** - Comprehensive TypeScript coverage
3. **Service Abstraction** - All API calls through dedicated layer
4. **Component Reusability** - Build from primitives to composites
5. **Separation of Concerns** - Clear boundaries between layers
6. **Backend-First** - Database operations via backend API only
7. **Auth Simplicity** - Supabase handles authentication, backend handles everything else
