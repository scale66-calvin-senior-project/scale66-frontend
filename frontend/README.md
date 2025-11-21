# **Scale66 Frontend Documentation**

## 1. File Structure

```
frontend/
├── package.json                               # Dependencies (Next.js 15, React 19, Supabase, Axios, Stripe)
├── package-lock.json                          # Locked dependency versions
├── tsconfig.json                              # TypeScript configuration (strict mode)
├── tsconfig.tsbuildinfo                       # TypeScript build cache
├── next.config.ts                             # Next.js configuration (Turbopack enabled)
├── next-env.d.ts                              # Next.js TypeScript declarations
├── eslint.config.mjs                          # ESLint configuration
│
├── .gitignore                                 # Git ignore patterns
├── README.md                                  # Frontend documentation & architecture guide
├── MIGRATION_NOTES.md                         # Firebase → Supabase migration documentation
├── env.example                                # Environment variables template
│
├── public/                                    # Static Assets
│   ├── favicon.ico                            # App favicon
│   └── logo.png                               # Brand logo
│
└── src/                                       # MAIN APPLICATION SOURCE
    ├── app/                                   # Next.js App Router (Route Handlers)
    │   ├── layout.tsx                         # Root layout with providers
    │   ├── globals.css                        # Global styles & CSS reset
    │   │
    │   ├── (landing)/                         # Landing pages (public)
    │   │   ├── layout.tsx                     # Landing layout with navbar/footer
    │   │   ├── page.tsx                       # Home page (marketing)
    │   │   ├── blog/
    │   │   │   └── page.tsx                   # Blog listing page
    │   │   ├── waitlist/
    │   │   │   └── page.tsx                   # Waitlist signup page
    │   │   ├── support/
    │   │   │   └── page.tsx                   # Support/contact page
    │   │   ├── privacy-policy/
    │   │   │   └── page.tsx                   # Privacy policy page
    │   │   └── terms-conditions/
    │   │       └── page.tsx                   # Terms & conditions page
    │   │
    │   ├── (auth)/                            # Authentication pages (public)
    │   │   ├── layout.tsx                     # Auth layout (centered forms)
    │   │   ├── login/
    │   │   │   └── page.tsx                   # Login page (email/password, OAuth)
    │   │   └── signup/
    │   │       └── page.tsx                   # Signup page (email/password, OAuth)
    │   │
    │   └── (app)/                             # Protected app pages (authenticated)
    │       ├── layout.tsx                     # App layout (sidebar, header)
    │       ├── dashboard/
    │       │   └── page.tsx                   # Dashboard (campaign overview)
    │       ├── onboarding/
    │       │   └── page.tsx                   # 6-step onboarding wizard
    │       ├── brand-kit/
    │       │   └── page.tsx                   # Brand kit management
    │       ├── campaigns/
    │       │   └── page.tsx                   # Campaigns list & management
    │       ├── canvas/
    │       │   └── [id]/
    │       │       └── page.tsx               # AI chat canvas (CORE FEATURE)
    │       └── settings/
    │           └── page.tsx                   # User settings & account
    │
    ├── components/                            # Reusable Components
    │   ├── index.ts                           # Components barrel exports
    │   │
    │   ├── ui/                                # UI Primitives (Design System)
    │   │   ├── index.ts                       # UI components barrel
    │   │   ├── Button/
    │   │   │   ├── Button.tsx                 # Button component (primary, secondary, ghost)
    │   │   │   ├── Button.module.css          # Button styles
    │   │   │   └── index.ts                   # Button exports
    │   │   ├── Input/
    │   │   │   ├── Input.tsx                  # Input field component
    │   │   │   ├── Input.module.css           # Input styles
    │   │   │   └── index.ts                   # Input exports
    │   │   ├── TextArea/
    │   │   │   ├── TextArea.tsx               # Textarea component
    │   │   │   ├── TextArea.module.css        # Textarea styles
    │   │   │   └── index.ts                   # Textarea exports
    │   │   ├── Card/
    │   │   │   ├── Card.tsx                   # Card container component
    │   │   │   ├── Card.module.css            # Card styles
    │   │   │   └── index.ts                   # Card exports
    │   │   ├── Modal/
    │   │   │   ├── Modal.tsx                  # Modal dialog component
    │   │   │   ├── Modal.module.css           # Modal styles
    │   │   │   └── index.ts                   # Modal exports
    │   │   ├── Dropdown/
    │   │   │   ├── Dropdown.tsx               # Dropdown select component
    │   │   │   ├── Dropdown.module.css        # Dropdown styles
    │   │   │   └── index.ts                   # Dropdown exports
    │   │   ├── Checkbox/
    │   │   │   ├── Checkbox.tsx               # Checkbox input component
    │   │   │   ├── Checkbox.module.css        # Checkbox styles
    │   │   │   └── index.ts                   # Checkbox exports
    │   │   └── Spinner/
    │   │       ├── Spinner.tsx                # Loading spinner component
    │   │       ├── Spinner.module.css         # Spinner styles
    │   │       └── index.ts                   # Spinner exports
    │   │
    │   ├── common/                            # Common Composites
    │   │   ├── index.ts                       # Common components barrel
    │   │   ├── LoadingSpinner/
    │   │   │   ├── LoadingSpinner.tsx         # Full-page loading spinner
    │   │   │   ├── LoadingSpinner.module.css  # Loading styles
    │   │   │   └── index.ts                   # LoadingSpinner exports
    │   │   ├── ErrorBoundary/
    │   │   │   ├── ErrorBoundary.tsx          # Error boundary wrapper
    │   │   │   ├── ErrorBoundary.module.css   # Error boundary styles
    │   │   │   └── index.ts                   # ErrorBoundary exports
    │   │   ├── EmptyState/
    │   │   │   ├── EmptyState.tsx             # Empty state component
    │   │   │   ├── EmptyState.module.css      # Empty state styles
    │   │   │   └── index.ts                   # EmptyState exports
    │   │   └── SuccessMessage/
    │   │       ├── SuccessMessage.tsx         # Success toast/message
    │   │       ├── SuccessMessage.module.css  # Success message styles
    │   │       └── index.ts                   # SuccessMessage exports
    │   │
    │   └── layouts/                           # Layout Components
    │       ├── index.ts                       # Layouts barrel
    │       ├── LandingLayout/
    │       │   ├── LandingLayout.tsx          # Landing page layout
    │       │   ├── LandingLayout.module.css   # Landing layout styles
    │       │   ├── Navbar.tsx                 # Landing navbar
    │       │   ├── Navbar.module.css          # Navbar styles
    │       │   ├── Footer.tsx                 # Landing footer
    │       │   ├── Footer.module.css          # Footer styles
    │       │   └── index.ts                   # LandingLayout exports
    │       ├── AuthLayout/
    │       │   ├── AuthLayout.tsx             # Auth pages layout (centered)
    │       │   ├── AuthLayout.module.css      # Auth layout styles
    │       │   └── index.ts                   # AuthLayout exports
    │       └── AppLayout/
    │           ├── AppLayout.tsx              # App pages layout (sidebar, header)
    │           ├── AppLayout.module.css       # App layout styles
    │           └── index.ts                   # AppLayout exports
    │
    ├── features/                              # Feature Modules (Feature-Based Architecture)
    │   ├── index.ts                           # Features barrel exports
    │   │
    │   ├── auth/                              # Authentication Feature
    │   │   ├── index.ts                       # Auth feature barrel
    │   │   ├── components/
    │   │   │   ├── index.ts                   # Auth components barrel
    │   │   │   ├── LoginForm/
    │   │   │   │   ├── LoginForm.tsx          # Login form component
    │   │   │   │   ├── LoginForm.module.css   # Login form styles
    │   │   │   │   └── index.ts               # LoginForm exports
    │   │   │   ├── SignupForm/
    │   │   │   │   ├── SignupForm.tsx         # Signup form component
    │   │   │   │   ├── SignupForm.module.css  # Signup form styles
    │   │   │   │   └── index.ts               # SignupForm exports
    │   │   │   ├── SocialAuthButtons/
    │   │   │   │   ├── SocialAuthButtons.tsx  # OAuth buttons (Google, etc.)
    │   │   │   │   ├── SocialAuthButtons.module.css
    │   │   │   │   └── index.ts               # SocialAuthButtons exports
    │   │   │   └── AuthToggle/
    │   │   │       ├── AuthToggle.tsx         # Login/Signup toggle
    │   │   │       ├── AuthToggle.module.css  # Toggle styles
    │   │   │       └── index.ts               # AuthToggle exports
    │   │   ├── hooks/
    │   │   │   ├── index.ts                   # Auth hooks barrel
    │   │   │   ├── useAuth.ts                 # Auth state hook
    │   │   │   ├── useLogin.ts                # Login mutation hook
    │   │   │   └── useSignup.ts               # Signup mutation hook
    │   │   ├── services/
    │   │   │   ├── index.ts                   # Auth services barrel
    │   │   │   └── auth.service.ts            # Supabase auth calls (login, signup, logout)
    │   │   └── types/
    │   │       ├── index.ts                   # Auth types barrel
    │   │       └── auth.types.ts              # User, LoginRequest, SignupRequest types
    │   │
    │   ├── brand-kit/                         # Brand Kit Feature
    │   │   ├── index.ts                       # Brand kit barrel
    │   │   ├── components/
    │   │   │   └── index.ts                   # Brand kit components (TBD)
    │   │   ├── hooks/
    │   │   │   ├── index.ts                   # Brand kit hooks barrel
    │   │   │   └── usebrandkit.ts             # Brand kit state & mutations
    │   │   ├── services/
    │   │   │   ├── index.ts                   # Brand kit services barrel
    │   │   │   └── brand-kit.service.ts       # Backend API calls for brand kit
    │   │   └── types/
    │   │       ├── index.ts                   # Brand kit types barrel
    │   │       └── brand-kit.types.ts         # BrandKit, BrandColors, BrandStyle types
    │   │
    │   ├── campaigns/                         # Campaigns Feature
    │   │   ├── index.ts                       # Campaigns barrel
    │   │   ├── components/
    │   │   │   └── index.ts                   # Campaign components (TBD)
    │   │   ├── hooks/
    │   │   │   ├── index.ts                   # Campaigns hooks barrel
    │   │   │   └── usecampaigns.ts            # Campaigns state & CRUD
    │   │   ├── services/
    │   │   │   ├── index.ts                   # Campaigns services barrel
    │   │   │   └── campaigns.service.ts       # Backend API calls for campaigns
    │   │   └── types/
    │   │       ├── index.ts                   # Campaigns types barrel
    │   │       └── campaigns.types.ts         # Campaign, CampaignCreate types
    │   │
    │   ├── canvas/                            # Canvas Feature - CORE FEATURE
    │   │   ├── index.ts                       # Canvas barrel
    │   │   ├── components/
    │   │   │   └── index.ts                   # Canvas components (AI chat, preview, etc.)
    │   │   ├── hooks/
    │   │   │   ├── index.ts                   # Canvas hooks barrel
    │   │   │   └── usecanvas.ts               # Canvas state & AI generation
    │   │   ├── services/
    │   │   │   ├── index.ts                   # Canvas services barrel
    │   │   │   └── canvas.service.ts          # Backend API calls for AI generation
    │   │   └── types/
    │   │       ├── index.ts                   # Canvas types barrel
    │   │       └── canvas.types.ts            # GenerateRequest, CarouselOutput types
    │   │
    │   ├── dashboard/                         # Dashboard Feature
    │   │   ├── index.ts                       # Dashboard barrel
    │   │   ├── components/
    │   │   │   └── index.ts                   # Dashboard components (stats, recent, etc.)
    │   │   ├── hooks/
    │   │   │   ├── index.ts                   # Dashboard hooks barrel
    │   │   │   └── usedashboard.ts            # Dashboard data hook
    │   │   ├── services/
    │   │   │   ├── index.ts                   # Dashboard services barrel
    │   │   │   └── dashboard.service.ts       # Backend API calls for dashboard
    │   │   └── types/
    │   │       ├── index.ts                   # Dashboard types barrel
    │   │       └── dashboard.types.ts         # DashboardStats, RecentActivity types
    │   │
    │   ├── landing/                           # Landing Pages Feature
    │   │   ├── index.ts                       # Landing barrel
    │   │   ├── landing-page/
    │   │   │   ├── index.ts                   # Landing page components barrel
    │   │   │   ├── HeroSection.tsx            # Hero section component
    │   │   │   ├── HeroSection.module.css     # Hero styles
    │   │   │   ├── FeaturesSection.tsx        # Features showcase
    │   │   │   ├── FeaturesSection.module.css # Features styles
    │   │   │   ├── PricingSection.tsx         # Pricing table
    │   │   │   ├── PricingSection.module.css  # Pricing styles
    │   │   │   ├── TestimonialsSection.tsx    # Customer testimonials
    │   │   │   ├── TestimonialsSection.module.css
    │   │   │   ├── CTASection.tsx             # Call-to-action section
    │   │   │   └── CTASection.module.css      # CTA styles
    │   │   ├── blog/
    │   │   │   ├── index.ts                   # Blog components barrel
    │   │   │   ├── BlogCard.tsx               # Blog post card
    │   │   │   ├── BlogCard.module.css        # Blog card styles
    │   │   │   └── BlogList.tsx               # Blog listing component
    │   │   ├── waitlist/
    │   │   │   ├── index.ts                   # Waitlist components barrel
    │   │   │   ├── WaitlistForm.tsx           # Waitlist signup form
    │   │   │   ├── WaitlistForm.module.css    # Waitlist form styles
    │   │   │   ├── WaitlistSuccess.tsx        # Success confirmation
    │   │   │   └── WaitlistSuccess.module.css # Success styles
    │   │   ├── legal/
    │   │   │   ├── index.ts                   # Legal pages barrel
    │   │   │   ├── PrivacyPolicy.tsx          # Privacy policy content
    │   │   │   ├── PrivacyPolicy.module.css   # Privacy policy styles
    │   │   │   ├── TermsConditions.tsx        # Terms & conditions content
    │   │   │   └── TermsConditions.module.css # Terms styles
    │   │   └── support/
    │   │       ├── index.ts                   # Support components barrel
    │   │       ├── ContactForm.tsx            # Support contact form
    │   │       ├── ContactForm.module.css     # Contact form styles
    │   │       └── FAQSection.tsx             # FAQ accordion
    │   │
    │   ├── onboarding/                        # Onboarding Feature
    │   │   ├── index.ts                       # Onboarding barrel
    │   │   ├── components/
    │   │   │   └── index.ts                   # Onboarding components (wizard steps)
    │   │   ├── hooks/
    │   │   │   ├── index.ts                   # Onboarding hooks barrel
    │   │   │   └── useonboarding.ts           # Onboarding wizard state
    │   │   ├── services/
    │   │   │   ├── index.ts                   # Onboarding services barrel
    │   │   │   └── onboarding.service.ts      # Backend API calls for onboarding
    │   │   └── types/
    │   │       ├── index.ts                   # Onboarding types barrel
    │   │       └── onboarding.types.ts        # OnboardingStep, OnboardingData types
    │   │
    │   ├── payment/                           # Payment Feature
    │   │   ├── index.ts                       # Payment barrel
    │   │   ├── components/
    │   │   │   └── index.ts                   # Payment components (pricing, checkout)
    │   │   ├── hooks/
    │   │   │   ├── index.ts                   # Payment hooks barrel
    │   │   │   └── usepayment.ts              # Payment & subscription hooks
    │   │   ├── services/
    │   │   │   ├── index.ts                   # Payment services barrel
    │   │   │   └── payment.service.ts         # Backend API calls for Stripe
    │   │   └── types/
    │   │       ├── index.ts                   # Payment types barrel
    │   │       └── payment.types.ts           # CheckoutSession, Subscription types
    │   │
    │   ├── posting/                           # Social Posting Feature
    │   │   ├── index.ts                       # Posting barrel
    │   │   ├── components/
    │   │   │   └── index.ts                   # Posting components (platform select, preview)
    │   │   ├── hooks/
    │   │   │   ├── index.ts                   # Posting hooks barrel
    │   │   │   └── useposting.ts              # Social media posting hooks
    │   │   ├── services/
    │   │   │   ├── index.ts                   # Posting services barrel
    │   │   │   └── posting.service.ts         # Backend API calls for social posting
    │   │   └── types/
    │   │       ├── index.ts                   # Posting types barrel
    │   │       └── posting.types.ts           # PostRequest, Platform types
    │   │
    │   └── settings/                          # Settings Feature
    │       ├── index.ts                       # Settings barrel
    │       ├── components/
    │       │   └── index.ts                   # Settings components (profile, account, etc.)
    │       ├── hooks/
    │       │   ├── index.ts                   # Settings hooks barrel
    │       │   └── usesettings.ts             # Settings state & updates
    │       ├── services/
    │       │   ├── index.ts                   # Settings services barrel
    │       │   └── settings.service.ts        # Backend API calls for settings
    │       └── types/
    │           ├── index.ts                   # Settings types barrel
    │           └── settings.types.ts          # UserSettings, Preferences types
    │
    ├── context/                               # React Context Providers
    │   ├── index.ts                           # Context barrel exports
    │   ├── AuthContext.tsx                    # Auth state provider (user, session, isAuthenticated)
    │   ├── BrandContext.tsx                   # Brand kit state provider
    │   └── ThemeContext.tsx                   # Theme state provider (dark/light mode)
    │
    ├── hooks/                                 # Shared Custom Hooks
    │   ├── index.ts                           # Hooks barrel exports
    │   ├── useAuth.ts                         # Global auth hook (wrapper for AuthContext)
    │   ├── useUser.ts                         # User data hook
    │   ├── useDebounce.ts                     # Debounce hook for search inputs
    │   ├── useLocalStorage.ts                 # LocalStorage persistence hook
    │   └── useMediaQuery.ts                   # Responsive breakpoint hook
    │
    ├── services/                              # API Service Layer
    │   └── api/
    │       ├── index.ts                       # API services barrel
    │       ├── client.ts                      # Axios client with JWT injection
    │       └── interceptors.ts                # Request/response interceptors (auth, errors, logging)
    │
    ├── lib/                                   # Third-Party Integrations
    │   ├── supabase.ts                        # Supabase client (AUTH ONLY - no database queries)
    │   └── stripe.ts                          # Stripe client initialization
    │
    ├── types/                                 # Shared TypeScript Types
    │   ├── index.ts                           # Types barrel exports
    │   ├── api.types.ts                       # API request/response types
    │   ├── user.types.ts                      # User, Profile types
    │   ├── brand.types.ts                     # BrandKit, BrandColors types
    │   ├── campaign.types.ts                  # Campaign types
    │   └── post.types.ts                      # Post, Carousel types
    │
    ├── utils/                                 # Utility Functions
    │   ├── index.ts                           # Utils barrel exports
    │   ├── constants.ts                       # App constants (API URLs, limits, etc.)
    │   ├── formatters.ts                      # Data formatting (dates, numbers, text)
    │   ├── validation.ts                      # Input validation functions
    │   ├── storage.ts                         # LocalStorage helpers
    │   └── date.ts                            # Date utilities
    │
    ├── data/                                  # Static Data & Constants
    │   ├── index.ts                           # Data barrel exports
    │   ├── brandStyles.ts                     # Predefined brand styles
    │   ├── pricingPlans.ts                    # Pricing tier data
    │   └── socialPlatforms.ts                 # Social platform configurations
    │
    ├── config/                                # App Configuration
    │   ├── index.ts                           # Config barrel exports
    │   ├── app.config.ts                      # App-wide configuration
    │   └── env.ts                             # Environment variable validation (Supabase, Backend API)
    │
    ├── styles/                                # Global Styles
    │   ├── variables.css                      # CSS variables (colors, spacing, fonts)
    │   └── utilities.css                      # Utility classes (flex, grid, spacing)
    │
    └── middleware.ts                          # Route Protection Middleware (Supabase auth check, redirects)
```

---

## 2. Major Folders

### **app/**

**Next.js 15 App Router with route groups**

- **Purpose:** File-system based routing with layouts and pages
- **Structure:** 3 route groups - `(landing)`, `(auth)`, `(app)`
- **Route Groups:**
  - **(landing)/** - Public marketing pages (SEO optimized)
  - **(auth)/** - Authentication pages (login, signup with Supabase)
  - **(app)/** - Protected app pages (requires Supabase auth middleware)
- **Key Features:**
  - Server Components by default
  - Nested layouts (root → group → page)
  - Automatic code splitting per route
  - Built-in loading & error states

### **components/**

**Reusable component library (3-tier hierarchy)**

- **Purpose:** Shared UI components organized by abstraction level
- **Structure:**
  - **ui/** - Primitive components (Button, Input, Modal, Card, etc.)
    - No business logic
    - CSS Modules for styling
    - TypeScript props with strict typing
    - Reusable across entire app
  - **common/** - Composite components (LoadingSpinner, ErrorBoundary, EmptyState)
    - Built from UI primitives
    - Shared business logic
    - Used across multiple features
  - **layouts/** - Layout components (LandingLayout, AuthLayout, AppLayout)
    - Page structure containers
    - Navbar, sidebar, footer composition
    - Route-specific layouts
- **Pattern:** Each component in own folder with `.tsx`, `.module.css`, `index.ts`

### **features/**

**Feature-based architecture (co-located by domain) CORE ARCHITECTURE**

- **Purpose:** Organize code by business feature, not file type
- **Pattern:** Each feature contains:
  - `components/` - Feature-specific UI components
  - `hooks/` - Feature-specific custom hooks
  - `services/` - **Backend API calls** (not direct database access)
  - `types/` - TypeScript interfaces/types
  - `index.ts` - Barrel exports
- **Features:**
  - **auth/** - Login, signup, OAuth via Supabase Auth
  - **brand-kit/** - Brand profile, colors, style (via backend API)
  - **campaigns/** - Campaign CRUD, analytics (via backend API)
  - **canvas/** - **CORE FEATURE** - AI chat interface for carousel generation
  - **dashboard/** - Main landing page, stats, recent activity
  - **landing/** - Marketing pages (hero, features, pricing, testimonials)
  - **onboarding/** - 6-step wizard for new users
  - **payment/** - Stripe checkout, subscription management (via backend API)
  - **posting/** - Instagram/TikTok publishing (via backend API)
  - **settings/** - User preferences, account settings
- **Benefits:**
  - Easy to find feature code
  - Clear feature boundaries
  - Independent feature development
  - Scalable architecture
  - Each feature can be worked on in a separate branch and cause almost no merge conflicts when pushing
- **Key Principle:** Features call **backend API**, not Supabase directly (except auth)

### **context/**

**React Context providers for global state**

- **Purpose:** Share state across component tree without prop drilling
- **Contexts:**
  - **AuthContext** - User authentication state (user, session, isAuthenticated)
    - Uses Supabase `auth.onAuthStateChange()` to track session
    - Provides JWT token for API calls
  - **BrandContext** - Active brand kit data (fetched from backend API)
  - **ThemeContext** - Dark/light mode, theme preferences
- **Pattern:** Context + Provider + custom hook (`useAuth`, `useBrand`, `useTheme`)

### **hooks/**

**Shared custom React hooks**

- **Purpose:** Reusable stateful logic across components
- **Hooks:**
  - `useAuth()` - Global auth hook (wrapper for AuthContext)
  - `useUser()` - Current user data (fetched from backend API)
  - `useDebounce()` - Debounce search inputs (300ms delay)
  - `useLocalStorage()` - Persist state to localStorage
  - `useMediaQuery()` - Responsive breakpoints (mobile, tablet, desktop)
- **Pattern:** Pure functions returning state/functions, TypeScript generics

### **services/api/**

**API service layer (centralized backend communication) CRITICAL**

- **Purpose:** Abstract all HTTP calls to backend, handle auth, errors, retries
- **Files:**
  - **client.ts** - Axios client with:
    - Base URL pointing to FastAPI backend
    - Request interceptor: Auto-adds JWT token from Supabase session
    - Response interceptor: Handles 401/403/500 errors globally
    - 30-second timeout
  - **interceptors.ts** - Additional interceptors:
    - Logging interceptor (development only)
    - Retry logic for network failures
- **Pattern:** All API calls go through this service layer (no direct fetch in components)
- **Benefits:**
  - Single source of truth for API config
  - Automatic JWT token injection
  - Centralized error handling (auto-redirect to /login on 401)
  - Easy to mock for testing
  - Type-safe requests/responses

### **lib/**

**Third-party library integrations**

- **Purpose:** Initialize and configure external services
- **Files:**
  - **supabase.ts** - Supabase client for **AUTHENTICATION ONLY** - **Enhanced**
    - **Authentication Functions:**
      - `signUp(email, password)` - Register new user
      - `signInWithPassword(email, password)` - Email/password login
      - `signInWithOAuth(provider)` - OAuth login (Google, GitHub, Apple)
      - `signOut()` - Log out current user
      - `resetPassword(email)` - Send password reset email
      - `updatePassword(newPassword)` - Update user password
    - **Session Management:**
      - `getSession()` - Get active session with JWT
      - `getCurrentUser()` - Get authenticated user data
      - `getAccessToken()` - Get JWT for backend API calls
    - NOT used for: Database queries, storage, realtime (use backend API instead)
    - Auto-refreshes tokens, persists session to localStorage
    - Type-safe with TypeScript exports: `Session`, `User`
  - **stripe.ts** - Stripe client configuration (for frontend checkout flows)
- **Pattern:** Export configured client instances and helper functions, not raw SDKs
- **Critical Note:** Supabase is ONLY for auth. All other operations go through backend API.

### **types/**

**Shared TypeScript types & interfaces**

- **Purpose:** Type definitions used across multiple features
- **Files:**
  - `api.types.ts` - API request/response types, pagination, errors
  - `user.types.ts` - User, Profile, UserSettings
  - `brand.types.ts` - BrandKit, BrandColors, BrandStyle
  - `campaign.types.ts` - Campaign, CampaignStats
  - `post.types.ts` - Post, Carousel, Slide
- **Benefits:** Type safety, autocomplete, refactoring safety

### **utils/**

**Utility functions (pure, stateless helpers)**

- **Purpose:** Shared logic that doesn't fit in components/hooks
- **Files:**
  - `constants.ts` - API URLs, limits, regex patterns
  - `formatters.ts` - Format dates, numbers, currency, text truncation
  - `validation.ts` - Email, URL, phone, color validation
  - `storage.ts` - localStorage/sessionStorage helpers
  - `date.ts` - Date formatting, relative time, time ago
- **Pattern:** Pure functions, no side effects, fully typed

### **data/**

**Static data & configuration constants**

- **Purpose:** Hardcoded data that doesn't change at runtime
- **Files:**
  - `brandStyles.ts` - Predefined brand styles (minimalist, bold, elegant)
  - `pricingPlans.ts` - Pricing tiers (free, pro, enterprise)
  - `socialPlatforms.ts` - Instagram/TikTok configs (limits, formats)
- **Pattern:** Export typed constants/arrays

### **config/**

**Application configuration**

- **Purpose:** App-wide settings, environment validation
- **Files:**
  - `app.config.ts` - App name, version, feature flags
  - `env.ts` - Environment variable validation and exports:
    - `apiBaseUrl` - Backend API URL (http://localhost:8000)
    - `supabaseUrl` - Supabase project URL
    - `supabaseAnonKey` - Supabase anonymous key (for auth)
- **Pattern:** Export config objects, validate on import

### **styles/**

**Global CSS (variables, utilities)**

- **Purpose:** Shared styles, design tokens, utility classes
- **Files:**
  - `variables.css` - CSS custom properties (colors, fonts, spacing)
  - `utilities.css` - Utility classes (flex, grid, text-align)
- **Pattern:** Import in root layout, use CSS Modules for components

### **middleware.ts**

**Next.js middleware (route protection with Supabase auth)**

- **Purpose:** Run code before request completes (auth check, redirects)
- **Use Cases:**
  - Check Supabase session for protected routes
  - Redirect unauthenticated users to `/login`
  - Redirect authenticated users away from `/login` to `/dashboard`
  - Add security headers
- **Pattern:** Export `middleware` function, configure `matcher` for protected routes
- **Implementation:** Uses Supabase `getSession()` to validate JWT token

---

# Scale66 Frontend

AI-powered social media content generation platform built with Next.js App Router.

## Project Overview

Scale66 helps businesses generate engaging social media content using AI. The MVP focuses on Instagram and TikTok carousel post generation with an intuitive canvas-based AI chat interface.

### Tech Stack

- **Framework:** Next.js 15 (App Router with Turbopack)
- **Language:** TypeScript (Strict Mode)
- **Styling:** CSS Modules
- **Authentication:** Supabase Auth (JWT tokens)
- **Backend API:** FastAPI (Python) - All database operations via backend
- **HTTP Client:** Axios (with automatic JWT injection)
- **Email:** Resend
- **Payment:** Stripe
- **Icons:** React Icons
- **SEO:** Next-SEO

## Architecture

This project follows a **feature-based architecture**. Key principles:

- **Feature Co-location:** Everything a feature needs lives together
- **Type Safety First:** TypeScript strict mode with comprehensive type definitions
- **Service Abstraction:** All API calls through dedicated service layer
- **Component Hierarchy:** UI primitives → Common composites → Feature-specific components

## Feature Status

| Feature           | Status   | Backend Deps           | Notes                                      |
| ----------------- | -------- | ---------------------- | ------------------------------------------ |
| **Landing Pages** | Complete | None                   | Migrated from Pages Router                 |
| **Auth**          | Ready    | Supabase Auth (direct) | Authentication functions fully implemented |
| **Onboarding**    | Setup    | `/api/v1/brand-kit`    | 6-step wizard structure                    |
| **Payment**       | Setup    | `/api/v1/payment/*`    | Structure ready, Stripe integration needed |
| **Dashboard**     | Setup    | `/api/v1/campaigns`    | Main landing page after login              |
| **Campaigns**     | Setup    | `/api/v1/campaigns/*`  | Campaign management grid                   |
| **Canvas**        | Setup    | `/api/v1/content/*`    | **CORE FEATURE** - AI chat interface       |
| **Posting**       | Setup    | `/api/v1/social/*`     | Post to Instagram/TikTok                   |
| **Brand Kit**     | Setup    | `/api/v1/brand-kit`    | Brand profile management                   |
| **Settings**      | Setup    | `/api/v1/posts/*`      | Account settings                           |

**Legend:**

- Complete - Fully functional
- Setup - Structure created, needs implementation
- Pending - Not yet started

## Getting Started

```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build
npm start
```

**Note:** Supabase authentication is fully configured. The client provides complete auth functionality including:

- Email/password authentication
- OAuth (Google, GitHub, Apple)
- Password reset flows
- Session management with automatic JWT refresh

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

## Architecture Overview

### Backend API Endpoints

FastAPI backend at `http://localhost:8000/api/v1/`

```
Brand Kit:   POST,GET,PUT,DELETE /brand-kit
Campaigns:   GET,POST /campaigns, GET,PUT,DELETE /campaigns/{id}
Content:     POST /content/generate, GET /content/status/{job_id}  [CORE]
Posts:       GET,POST /posts, GET,PUT,DELETE /posts/{id}, POST /posts/{id}/publish
Social:      GET /social/connect/{platform}, GET /social/accounts
Payment:     POST /payment/create-checkout-session, POST /payment/webhook
```

**Note:** Authentication (signup/login) is handled by frontend → Supabase Auth directly. Backend validates JWT tokens. All other operations go through backend API.

## Workflow

**Branch naming:** `frontend/{feature,fix,refactor}/[name]`

**Code review checklist:**

- TypeScript strict mode passing
- No console.log statements
- Path aliases used
- Service layer for API calls
- Proper interfaces and types

## Implementation Roadmap

**Core:** Auth (Supabase + OAuth) → Onboarding (6-step wizard) → Brand Kit → Canvas (AI chat interface - CORE FEATURE) → Dashboard → Campaigns → Payment (Stripe)

**Additional:** Posting (Instagram/TikTok) → Settings → Testing
