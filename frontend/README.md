# Scale66 Frontend

AI-powered social media content generation platform built with Next.js App Router.

## Project Overview

Scale66 helps businesses generate engaging social media content using AI. The MVP focuses on Instagram and TikTok carousel post generation with an intuitive canvas-based AI chat interface.

### Tech Stack

- **Framework:** Next.js 15.5.4 (App Router)
- **Language:** TypeScript (Strict Mode)
- **Styling:** CSS Modules
- **Authentication:** Firebase Auth
- **Payment:** Stripe
- **Deployment:** Firebase Hosting

## Architecture

This project follows a **feature-based architecture** as detailed in `/SCALE66_FILE_STRUCTURE_PHILOSOPHY.md`. Key principles:

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
├── lib/                       # Third-party integrations (Firebase, Stripe)
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

| Feature | Status | Priority | Backend Deps | Notes |
|---------|--------|----------|--------------|-------|
| **Landing Pages** | ✅ Complete | - | None | Migrated from Pages Router |
| **Auth** | 🔨 Setup | P0 | `/api/auth/*` | Login/Signup/OAuth ready for implementation |
| **Onboarding** | 🔨 Setup | P0 | `/api/onboarding` | 6-step wizard structure |
| **Payment** | 🔨 Setup | P0 | Stripe API | Pricing tiers skeleton |
| **Dashboard** | 🔨 Setup | P0 | `/api/campaigns` | Main landing page after login |
| **Campaigns** | 🔨 Setup | P0 | `/api/campaigns/*` | Campaign management grid |
| **Canvas** | 🔨 Setup | P0 | `/api/ai/generate` | **CORE FEATURE** - AI chat interface |
| **Posting** | 🔨 Setup | P1 | Social media APIs | Post to Instagram/TikTok |
| **Brand Kit** | 🔨 Setup | P1 | `/api/brand/*` | Brand profile management |
| **Settings** | 🔨 Setup | P1 | `/api/user/*` | Account settings |

**Legend:**
- ✅ Complete - Fully functional
- 🔨 Setup - Structure created, needs implementation
- ⏳ Pending - Not yet started

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Firebase project (for authentication)
- Stripe account (for payments)

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Fill in your environment variables in .env.local
```

### Environment Variables

See `.env.example` for required variables:
- Firebase configuration (6 variables)
- Stripe keys (publishable & secret)
- API base URL
- OAuth credentials (Google, Apple)

### Development

```bash
# Run development server
npm run dev

# Open http://localhost:3000
```

### Build

```bash
# Production build
npm run build

# Start production server
npm start
```

## Development Guide

### Adding a New Feature

1. **Create Feature Folder**
   ```
   src/features/[feature-name]/
   ├── components/
   ├── hooks/
   ├── services/
   ├── types/
   └── index.ts
   ```

2. **Define Types First**
   ```typescript
   // types/[feature].types.ts
   export interface FeatureData {
     // Define your interfaces
   }
   ```

3. **Create Service Layer**
   ```typescript
   // services/[feature].service.ts
   export const featureService = {
     async getData(): Promise<FeatureData> {
       // API call
     }
   };
   ```

4. **Build Components**
   ```
   components/[Component]/
   ├── Component.tsx
   ├── Component.module.css
   └── index.ts
   ```

5. **Create Custom Hooks**
   ```typescript
   // hooks/use[Feature].ts
   export const useFeature = () => {
     // Hook logic
   };
   ```

6. **Add Barrel Export**
   ```typescript
   // index.ts
   export * from './components';
   export * from './hooks';
   export * from './services';
   export * from './types';
   ```

### Component Patterns

**UI Components** (`components/ui/`):
- Primitive, reusable components
- No business logic
- Accept all native HTML attributes
- Fully typed with interfaces

**Common Components** (`components/common/`):
- Composite components used across features
- Can contain app-specific logic
- Examples: LoadingSpinner, ErrorBoundary

**Feature Components** (`features/[feature]/components/`):
- Feature-specific components
- Can use hooks and services from same feature
- Import UI/Common components via path aliases

### Service Layer

All API calls must go through the service layer:

```typescript
// services/api/client.ts
export const apiClient = {
  get: async (url: string) => { /* ... */ },
  post: async (url: string, data: any) => { /* ... */ },
};

// features/[feature]/services/[feature].service.ts
import { apiClient } from '@/services/api';

export const featureService = {
  async getData() {
    return await apiClient.get('/api/feature');
  },
};
```

### Type Safety Guidelines

1. **No `any` types** - Use `unknown` if type is truly unknown
2. **Define interfaces** for all data structures
3. **Type all functions** including return types
4. **Use enums** for fixed value sets
5. **Leverage path aliases** for clean imports

### CSS Organization

**Global Styles:**
- `app/globals.css` - Base resets and imports
- `styles/variables.css` - CSS custom properties
- `styles/utilities.css` - Utility classes

**Component Styles:**
- Co-located CSS Modules (`.module.css`)
- Use CSS variables from `styles/variables.css`
- BEM-like naming within modules

## Path Aliases

All imports use path aliases for clean, maintainable code:

```typescript
// ✅ Good
import { Button } from '@/components/ui';
import { useAuth } from '@/hooks';
import { authService } from '@/features/auth';

// ❌ Bad
import { Button } from '../../../components/ui/Button';
```

Available aliases:
- `@/` - `src/`
- `@/components/*` - `src/components/*`
- `@/features/*` - `src/features/*`
- `@/lib/*` - `src/lib/*`
- `@/types/*` - `src/types/*`
- `@/hooks/*` - `src/hooks/*`
- `@/utils/*` - `src/utils/*`
- `@/data/*` - `src/data/*`
- `@/config/*` - `src/config/*`
- `@/services/*` - `src/services/*`
- `@/context/*` - `src/context/*`
- `@/styles/*` - `src/styles/*`

## API Integration

### Expected Backend Endpoints

**Authentication:**
- `POST /api/auth/login` - Email/password login
- `POST /api/auth/signup` - User registration
- `POST /api/auth/oauth/google` - Google OAuth
- `POST /api/auth/oauth/apple` - Apple OAuth
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

**Campaigns:**
- `GET /api/campaigns` - List user campaigns
- `POST /api/campaigns` - Create campaign
- `GET /api/campaigns/:id` - Get campaign details
- `PUT /api/campaigns/:id` - Update campaign
- `DELETE /api/campaigns/:id` - Delete campaign

**AI Generation (CORE):**
- `POST /api/ai/generate` - Generate carousel content
- `POST /api/ai/variations` - Generate variations
- `POST /api/ai/enhance-prompt` - Enhance user prompt

**Brand Kit:**
- `GET /api/brand` - Get user brand
- `PUT /api/brand` - Update brand
- `POST /api/brand/assets` - Upload brand assets

**Posting:**
- `POST /api/post/instagram` - Post to Instagram
- `POST /api/post/tiktok` - Post to TikTok
- `GET /api/post/status/:id` - Check post status

**Payment:**
- `POST /api/payment/create-checkout` - Create Stripe checkout
- `POST /api/payment/webhook` - Stripe webhook handler
- `GET /api/payment/subscription` - Get subscription status

### Request/Response Format

```typescript
// Standard API Response
interface ApiResponse<T> {
  data: T;
  error?: string;
  message?: string;
}

// Error Response
interface ApiError {
  error: string;
  code?: string;
  details?: any;
}
```

## Team Workflow

### Branch Naming

- Feature: `frontend/feature/[feature-name]`
- Bugfix: `frontend/fix/[issue-description]`
- Refactor: `frontend/refactor/[scope]`

### Feature Implementation

1. **Assign Feature** - Pick from status table
2. **Create Branch** - `frontend/feature/[feature-name]`
3. **Implement**
   - Start with types
   - Build service layer
   - Create components
   - Add hooks
   - Write tests (when testing infrastructure is ready)
4. **PR Review** - At least one approval required
5. **Merge to Dev** - After approval
6. **Deploy** - Automatic on merge

### Code Review Checklist

- [ ] TypeScript strict mode passing
- [ ] No console.log statements
- [ ] All imports use path aliases
- [ ] Components have proper interfaces
- [ ] Service layer used for API calls
- [ ] CSS uses variables from styles/
- [ ] Follows feature structure pattern
- [ ] TODO comments for incomplete work

## Next Steps

### Immediate Priorities (Week 1)

1. **Auth Implementation** (P0)
   - Implement LoginForm and SignupForm
   - Firebase Auth integration
   - OAuth setup (Google, Apple)
   - Auth context and middleware

2. **Onboarding Flow** (P0)
   - 6-step wizard implementation
   - Form validation
   - Progress tracking
   - Data persistence

3. **Canvas (CORE)** (P0)
   - AI chat interface
   - Real-time message handling
   - Content generation display
   - Variations generation

### Medium Term (Week 2-3)

4. **Dashboard** - Main landing after login
5. **Campaigns** - Campaign management
6. **Payment** - Stripe integration
7. **Posting** - Social media integration

### Later (Week 4+)

8. **Brand Kit** - Brand management
9. **Settings** - Account settings
10. **Testing** - Unit and E2E tests

## Resources

- [Next.js App Router Docs](https://nextjs.org/docs/app)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Firebase Auth Guide](https://firebase.google.com/docs/auth)
- [Stripe Integration](https://stripe.com/docs)
- [Scale66 Philosophy Doc](/SCALE66_FILE_STRUCTURE_PHILOSOPHY.md)

## Support

For questions or issues:
- Check the philosophy document for architecture decisions
- Review this README for implementation patterns
- Ask in team chat for clarification

---

**Ready to build!** 🚀

All infrastructure is in place. Pick a feature from the status table and start implementing.

