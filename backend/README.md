# **Scale66 Backend Documentation**

## 1. File Structure

```
backend/
├── main.py                                    # FastAPI app entry point, CORS, routers
├── pyproject.toml                            # Python dependencies (uv package manager)
├── uv.lock                                   # Locked dependency versions
├── .python-version                           # Python version specification (3.13)
├── pyrightconfig.json                        # Pyright type checker configuration
├── .gitignore                                # Git ignore patterns
│
├── app/
│   ├── __init__.py                           # App package initialization
│   │
│   ├── agents/                               # AI Pipeline Agents (6-step sequential process)
│   │   ├── __init__.py                       # Agents package
│   │   ├── base_agent.py                     # Base class: error handling, LLM calls, retry logic
│   │   ├── orchestrator.py                   # Step 1: Pipeline coordinator, manages all agents
│   │   ├── carousel_format_decider.py        # Step 2: Decides carousel format/structure
│   │   ├── story_generator.py                # Step 3: Creates hook, script, slides
│   │   ├── image_generator.py                # Step 4: Generates carousel images (Gemini)
│   │   ├── text_generator.py                 # Step 5: Generates on-screen text
│   │   └── finalizer.py                      # Step 6: Combines text + images into final carousel
│   │
│   ├── api/                                  # FastAPI Routes
│   │   ├── __init__.py                       # API package
│   │   ├── deps.py                           # Dependency injection (JWT validation, Supabase client)
│   │   └── v1/                               # API version 1
│   │       ├── __init__.py                   # V1 routes package
│   │       ├── brand_kit.py                  # Brand kit CRUD endpoints
│   │       ├── campaigns.py                  # Campaign management endpoints
│   │       ├── content.py                    # Main AI generation endpoint (triggers pipeline)
│   │       ├── posts.py                      # Generated content management
│   │       ├── social.py                     # Social media integration (Instagram, TikTok)
│   │       └── payment.py                    # Stripe payment processing
│   │
│   ├── core/                                 # Core Configuration
│   │   ├── __init__.py                       # Core package
│   │   ├── config.py                         # Settings (API keys, model names, env vars)
│   │   ├── security.py                       # JWT token validation (Supabase-issued tokens)
│   │   └── supabase.py                       # Supabase client initialization
│   │
│   ├── crud/                                 # Database Operations
│   │   ├── __init__.py                       # CRUD package
│   │   ├── base.py                           # Base CRUD class (create, read, update, delete)
│   │   ├── brand_kit.py                      # Brand kit database operations
│   │   ├── campaign.py                       # Campaign database operations
│   │   ├── post.py                           # Post database operations
│   │   ├── session.py                        # User session management
│   │   └── user.py                           # User database operations
│   │
│   ├── models/                               # Pydantic Schemas
│   │   ├── __init__.py                       # Models package
│   │   ├── brand_kit.py                      # Brand kit schemas (create, update, response)
│   │   ├── campaign.py                       # Campaign schemas
│   │   ├── post.py                           # Post schemas
│   │   ├── user.py                           # User schemas
│   │   ├── social.py                         # Social media integration schemas
│   │   ├── payment.py                        # Stripe payment schemas
│   │   ├── content.py                        # Content generation request/response schemas
│   │   ├── common.py                         # Shared/common schemas
│   │   └── pipeline.py                       # AI pipeline internal schemas (agent communication)
│   │
│   ├── services/                             # External Integrations
│   │   ├── __init__.py                       # Services package
│   │   ├── ai/                               # AI Services
│   │   │   ├── __init__.py                   # AI services package
│   │   │   ├── anthropic_service.py          # Anthropic Claude API (Sonnet 4.5, Haiku 4.5, Opus 4.1)
│   │   │   └── gemini_service.py             # Google Gemini API (gemini-2.5-flash-image)
│   │   ├── email_service.py                  # Resend email API
│   │   ├── image_overlay_service.py          # Image composition (text on images with Pillow)
│   │   ├── social_media_service.py           # Instagram/TikTok posting APIs
│   │   ├── storage_service.py                # File upload (Supabase Storage/S3)
│   │   └── stripe_service.py                 # Stripe payment processing
│   │
│   └── utils/                                # Utility Functions
│       ├── __init__.py                       # Utils package
│       ├── file_handlers.py                  # File upload/download helpers
│       ├── formatters.py                     # Data formatting utilities
│       └── validators.py                     # Input validation functions
│
└── supabase/                                 # Database Schema
    ├── config.toml                           # Supabase local config
    └── migrations/                           # SQL migrations
        ├── 20240115000000_create_initial_schema.sql  # Initial database schema
        └── README.md                         # Migration instructions
```

---

## 2. Major Folders

### **agents/**

**6-step sequential AI pipeline for carousel content generation**

- **Purpose:** Orchestrate multi-agent AI workflow to generate branded carousel content
- **Architecture:** Base agent class with 5 specialized agents executing in strict sequence
- **Flow:**
  1. **Orchestrator** - Coordinates entire pipeline, manages state
  2. **Format Decider** - Selects optimal carousel format (educational, problem-solution, etc.)
  3. **Story Generator** - Creates hook → script → splits into slides
  4. **Image Generator** - Generates AI images for all slides (Google Gemini)
  5. **Text Generator** - Creates on-screen text with styling
  6. **Finalizer** - Overlays text on images using Claude Vision + Pillow
- **Key Feature:** Sequential execution with dependencies (TextGenerator requires ImageGenerator output)
- **AI Models:**
  - Claude Sonnet 4.5 (complex reasoning, story generation)
  - Claude Haiku 4.5 (fast, simple tasks)
  - Claude Opus 4.1 (highest quality, final output)
  - Claude Vision (image analysis for text placement)
  - Google Gemini (image generation)
- **Status:** Architecture defined, implementation pending

### **api/**

**FastAPI REST endpoints**

- **Purpose:** HTTP API layer exposing backend functionality
- **Structure:** Versioned API (v1) with route modules organized by feature
- **Auth:** JWT validation (tokens issued by Supabase Auth on frontend)
- **Key Endpoints:**
  - `/api/v1/content/generate` - **CORE** - Main AI pipeline trigger
  - `/api/v1/brand-kit` - Brand kit CRUD operations
  - `/api/v1/campaigns` - Campaign management
  - `/api/v1/posts` - Generated content management
  - `/api/v1/social/connect` - Social media OAuth
  - `/api/v1/payment/checkout` - Stripe integration
- **Dependencies (`deps.py`):**
  - `get_current_user()` - Validates JWT token, extracts user info
  - `get_supabase_client()` - Provides Supabase client instance
- **Important:** No auth endpoints (signup/login) - handled by frontend directly with Supabase Auth

### **core/**

**Configuration and security**

- **Purpose:** Centralized settings and security primitives
- **Files:**
  - **config.py** - Environment variables, API keys, model selection
    - `Settings` class with environment validation
    - API keys: Anthropic, Gemini, Supabase, Stripe, Resend
    - Model configuration: Claude models, Gemini models
  - **security.py** - JWT verification (Supabase-issued tokens only)
    - `verify_supabase_jwt()` - Validates JWT tokens from frontend
    - `extract_token_from_header()` - Extracts Bearer token
    - No password hashing or token creation (handled by Supabase Auth)
  - **supabase.py** - Supabase client initialization - **Implemented**
    - `get_supabase_client()` - Client with anon key (respects RLS)
    - `get_supabase_admin_client()` - Client with service role key (bypasses RLS)
    - `get_supabase_dep()` - FastAPI dependency for RLS-aware operations
    - `get_supabase_admin_dep()` - FastAPI dependency for admin operations
    - Singleton pattern with `@lru_cache()` for efficient reuse
    - Used for database operations only (not auth)

### **crud/**

**Database operations layer**

- **Purpose:** Abstract Supabase queries into reusable operations
- **Pattern:** Base CRUD class with entity-specific implementations
- **Operations:** create, get, get_multi, update, delete
- **RLS:** Respects Supabase Row Level Security policies
- **Files:**
  - `base.py` - Generic CRUD operations
  - `brand_kit.py` - Brand kit specific queries
  - `campaign.py` - Campaign specific queries
  - `post.py` - Post management queries
  - `user.py` - User data queries (profile, settings)
  - `session.py` - Session management queries

### **models/**

**Pydantic schemas**

- **Purpose:** Request/response validation and serialization
- **Types:**
  - **Entity models** - User, BrandKit, Campaign, Post
  - **API request/response models** - Create, Update, Response schemas
  - **Pipeline internal models** - Agent communication (pipeline.py)
- **Benefits:** Type safety, automatic validation, OpenAPI docs generation
- **Organization:** One file per feature for clarity

### **services/**

**External API integrations**

- **AI Services:**
  - **Anthropic** - Claude Sonnet 4.5, Haiku 4.5, Opus 4.1 (text generation, vision)
  - **Gemini** - Google Gemini 2.5 Flash (image generation)
- **Social Media:**
  - Instagram Graph API (OAuth, posting)
  - TikTok Content Posting API (OAuth, posting)
- **Payments:** Stripe
  - Checkout sessions
  - Webhooks
  - Subscription management
- **Storage:** Supabase Storage (images, assets) or AWS S3
- **Email:** Resend API (transactional emails, waitlist)
- **Image Processing:** Pillow (PIL) for text overlay on generated images

### **utils/**

**Helper functions**

- **file_handlers.py** - Upload validation, Supabase storage wrappers
- **formatters.py** - Date formatting, JSON transformations
- **validators.py** - Custom validation logic (email, URLs, brand colors)
- **Pattern:** Pure utility functions, no business logic

---

---

# Scale66 Backend

AI-powered carousel content generation platform built with FastAPI, Supabase, and AI agents.

## Tech Stack

- **Framework:** FastAPI + Uvicorn
- **Package Manager:** uv (fast, modern Python package management)
- **Database:** Supabase (PostgreSQL + Auth + Storage)
- **AI Services:** Anthropic (Claude) + Google Gemini
  - **Text Generation:** Claude Sonnet 4.5 (smartest model for complex tasks)
  - **Image Generation:** Google Gemini (gemini-2.5-flash-image)
- **Image Processing:** Pillow
- **Payment:** Stripe
- **Email:** Resend
- **Authentication:** Supabase Auth (frontend) + JWT validation (backend)

## Quick Start with UV

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup and run
cd backend
uv sync                          # Install dependencies
cp .env.example .env            # Configure environment
uv run python main.py           # Start server (http://localhost:8000)
```

## AI Pipeline

**6-step carousel generation flow:**

1. **Orchestrator** - Coordinates entire pipeline
2. **Format Decider** - Selects optimal carousel format (educational, problem-solution, etc.)
3. **Story Generator** - Creates hook → script → splits into slides
4. **Image Generator** - Generates AI images for all slides
5. **Text Generator** - Creates on-screen text with styling
6. **Finalizer** - Overlays text on images (Claude Vision + Pillow)

**Output:** Ready-to-post carousel slides

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Core Endpoints

```
Brand Kit:   POST,GET,PUT,DELETE /brand-kit
Campaigns:   GET,POST /campaigns, GET,PUT,DELETE /campaigns/{id}
Content:     POST /content/generate, GET /content/status/{job_id}  [CORE]
Posts:       GET,POST /posts, GET,PUT,DELETE /posts/{id}, POST /posts/{id}/publish
Social:      GET /social/connect/{platform}, GET /social/accounts
Payment:     POST /payment/create-checkout-session, POST /payment/webhook
Health:      GET /health
```

**Note:** Auth (signup/login) is handled by frontend → Supabase Auth directly. Backend validates JWT tokens.

**API Docs:** http://localhost:8000/docs (Swagger) | http://localhost:8000/redoc (ReDoc)

## Environment Variables

```env
# Supabase (Required) - Configuration Implemented
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key                    # For RLS-aware database operations
SUPABASE_SERVICE_KEY=your-service-role-key    # For admin operations (bypasses RLS)
SUPABASE_JWT_SECRET=your-jwt-secret           # For validating JWT tokens from frontend

# AI Services (Required)
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...

# Email (Required)
RESEND_API_KEY=re_...

# Social Media (Optional)
INSTAGRAM_CLIENT_ID=...
INSTAGRAM_CLIENT_SECRET=...
TIKTOK_CLIENT_KEY=...
TIKTOK_CLIENT_SECRET=...

# Payment (Optional)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Storage (Optional - if using AWS instead of Supabase Storage)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=scale66-content
```

See `.env.example` for complete list.

## Database Setup

**Using Supabase:**

```bash
# 1. Create project at https://supabase.com
# 2. Copy credentials to .env
# 3. Run migrations:

brew install supabase/tap/supabase  # Install CLI (macOS)
supabase link --project-ref your-project-ref
supabase db push                     # Apply migrations
```

**Database includes:**

- 9 tables with Row Level Security (RLS)
- Storage buckets for carousel images and brand assets
- Authentication configured (managed by Supabase Auth)

**Tables:** users, brand_kits, campaigns, posts, post_variations, chat_history, social_media_accounts, payment_transactions

## Development

### Adding Dependencies

```bash
uv add package-name              # Add dependency
uv add --optional dev pytest-mock # Add to optional group
uv sync                          # Sync environment
```

### Code Quality

```bash
uv sync --extra dev              # Install dev tools
uv run black app/                # Format
uv run ruff check app/           # Lint
uv run mypy app/                 # Type check
uv run pytest                    # Run tests
```

### Running the Server

```bash
# Development (auto-reload)
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uv run python main.py
```

## Implementation Status

**Current Status:** Structure complete, core infrastructure implemented

All files contain:

- Class/function signatures with type hints
- Comprehensive docstrings
- Supabase client initialization (**IMPLEMENTED**)
- Implementation in progress

### Implementation Priority

1. **Core Infrastructure** - Supabase client (DONE), JWT validation, CRUD operations
2. **API Endpoints** - Brand kit, campaigns, content generation
3. **AI Pipeline** - Implement agents (2 → 3 → 4 → 5 → 6 → 1)
4. **Services** - Storage, email, social OAuth, Stripe

### Recently Completed

- **Supabase Client Initialization** (`app/core/supabase.py`)
  - Implemented `get_supabase_client()` with anon key (RLS-aware)
  - Implemented `get_supabase_admin_client()` with service role key (bypasses RLS)
  - Added FastAPI dependency injection functions
  - Environment variable validation with helpful error messages
  - Singleton pattern using `@lru_cache()` for efficient client reuse

**Note:** Authentication (signup/login) is handled by frontend → Supabase Auth. Backend only validates JWT tokens and performs database operations.

## Branch Strategy

**Naming:** `backend/{feature,fix,refactor}/[name]`

## License

Proprietary – Scale66 internal use only.
