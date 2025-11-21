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
│   │   ├── __init__.py                       # Models package (comprehensive exports)
│   │   ├── brand_kit.py                      # Brand kit schemas (create, update, response)
│   │   ├── campaign.py                       # Campaign schemas
│   │   ├── post.py                           # Post schemas
│   │   ├── user.py                           # User schemas
│   │   ├── social.py                         # Social media integration schemas
│   │   ├── payment.py                        # Stripe payment schemas
│   │   ├── content.py                        # Content generation request/response schemas
│   │   ├── common.py                         # Shared schemas (MessageResponse, ErrorResponse, enums)
│   │   └── pipeline.py                       # AI pipeline schemas (6-step agent I/O models)
│   │
│   ├── services/                             # External Integrations
│   │   ├── __init__.py                       # Services package
│   │   ├── ai/                               # AI Services
│   │   │   ├── __init__.py                   # AI services package
│   │   │   ├── anthropic_service.py          # Anthropic Claude API (text + vision) - IMPLEMENTED
│   │   │   └── gemini_service.py             # Gemini Service using Imagen 4 (image generation) - IMPLEMENTED
│   │   ├── email_service.py                  # Resend email API
│   │   ├── image_overlay_service.py          # Image composition (text overlay with Pillow)
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
└── .venv/                                    # Virtual environment (created by uv)
```

---

## 2. Major Folders

### **agents/**

**6-step sequential AI pipeline for carousel content generation**

- **Purpose:** Orchestrate multi-agent AI workflow to generate branded carousel content
- **Architecture:** Base agent class with 5 specialized agents executing in strict sequence
- **Flow:**
  1. **Orchestrator** - Coordinates entire pipeline, manages state (OrchestratorInput)
  2. **Format Decider** - Selects optimal carousel format (CarouselFormatDeciderInput/Output)
  3. **Story Generator** - Creates hook → script → splits into slides (StoryGeneratorInput/Output)
  4. **Image Generator** - Generates AI images for all slides (ImageGeneratorInput/Output)
  5. **Text Generator** - Creates on-screen text with styling (TextGeneratorInput/Output)
  6. **Finalizer** - Overlays text on images (FinalizerInput/Output)
- **Key Feature:** Sequential execution with dependencies (each step receives output from previous)
- **AI Models:**
  - Claude Sonnet 4.5 (complex reasoning, story generation)
  - Claude Haiku 4.5 (fast, simple tasks)
  - Claude Opus 4.1 (highest quality, final output)
  - Claude Vision (image analysis for text placement)
  - Imagen 4.0 (image generation)
- **Data Flow:** Fully typed with Pydantic schemas in `models/pipeline.py`
- **Status:** Pipeline schemas fully defined, agent classes structure complete, implementation in progress

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
  - **Pipeline internal models** - Complete agent communication schemas (pipeline.py)
    - Step 1: OrchestratorInput
    - Step 2: CarouselFormatDeciderInput/Output
    - Step 3: StoryGeneratorInput/Output
    - Step 4: ImageGeneratorInput/Output
    - Step 5: TextGeneratorInput/Output
    - Step 6: FinalizerInput/Output
  - **Common models** - Shared schemas (common.py)
    - MessageResponse, ErrorResponse
    - Enums: PostStatus, PipelineStatus, SocialPlatform
    - Mixins: TimestampedMixin
    - Base classes: BasePipelineStep
- **Benefits:** Type safety, automatic validation, OpenAPI docs generation
- **Organization:** One file per feature for clarity
- **Status:** Fully defined with comprehensive type validation

### **services/**

**External API integrations**

- **AI Services (ai/):**
  - **anthropic_service.py** - IMPLEMENTED
    - Singleton pattern with AsyncAnthropic client
    - `generate_text()` - Text generation using Claude Sonnet 4.5
    - `analyze_image()` - Vision analysis with base64 image support
    - Error handling with AnthropicServiceError
    - Configurable temperature and max_tokens
  - **gemini_service.py** (Imagen 4) - IMPLEMENTED
    - Singleton pattern with Gemini client
    - `generate_image()` - Image generation with Imagen 4.0
    - Configurable aspect ratio (1:1, 3:4, 4:3, 9:16, 16:9) and size (1K, 2K)
    - Returns base64 encoded images
    - Error handling with GeminiServiceError
- **Social Media:**
  - **social_media_service.py** - Instagram Graph API, TikTok Content Posting API
    - OAuth integration
    - Post publishing
- **Payments:**
  - **stripe_service.py** - Stripe integration
    - Checkout sessions
    - Webhooks
    - Subscription management
- **Storage:**
  - **storage_service.py** - File storage (Supabase Storage/S3)
    - Image upload and retrieval
- **Email:**
  - **email_service.py** - Resend API integration
    - Transactional emails
    - Waitlist management
- **Image Processing:**
  - **image_overlay_service.py** - Pillow-based image manipulation
    - Text overlay on generated images
    - Font styling and positioning

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
- **AI Services:**
  - **Anthropic Claude** - Text generation and vision analysis (IMPLEMENTED)
    - Sonnet 4.5 (complex reasoning, story generation)
    - Vision API (image analysis for text placement)
  - **Google Imagen 4** - Image generation (IMPLEMENTED)
    - Imagen 4.0 (carousel image generation with configurable aspect ratios)
- **Image Processing:** Pillow (PIL) for text overlay
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

1. **Orchestrator** - Coordinates entire pipeline (OrchestratorInput)
2. **Format Decider** - Selects optimal carousel format (CarouselFormatDeciderInput/Output)
3. **Story Generator** - Creates hook → script → splits into slides (StoryGeneratorInput/Output)
4. **Image Generator** - Generates AI images for all slides via Gemini (ImageGeneratorInput/Output)
5. **Text Generator** - Creates on-screen text with styling (TextGeneratorInput/Output)
6. **Finalizer** - Overlays text on images using Claude Vision + Pillow (FinalizerInput/Output)

**Data Models:** Fully typed with Pydantic schemas for each step (see `app/models/pipeline.py`)

**Output:** Ready-to-post carousel slides with metadata

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
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# AI Services
ANTHROPIC_API_KEY=sk-...
VOYAGE_API_KEY=...
GEMINI_API_KEY=...

# Email
RESEND_API_KEY=re_...
RESEND_AUDIENCE_ID=...

# Social Media
INSTAGRAM_CLIENT_ID=...
INSTAGRAM_CLIENT_SECRET=...
TIKTOK_CLIENT_KEY=...
TIKTOK_CLIENT_SECRET=...

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# App Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

See `.env.example` for complete list.

## Database Setup

**Using Supabase:**

1. Create a project at https://supabase.com
2. Set up your database schema through Supabase Dashboard or SQL Editor
3. Copy your project credentials to `.env`:
   - `SUPABASE_URL` - Your project URL
   - `SUPABASE_KEY` - Anonymous/public key
   - `SUPABASE_SERVICE_KEY` - Service role key
   - `SUPABASE_JWT_SECRET` - JWT secret for token validation

**Required Database Tables:**

- `users` - User profiles and settings
- `brand_kits` - Brand identity configurations
- `campaigns` - Campaign management
- `posts` - Generated content posts
- `post_variations` - Post variations and A/B tests
- `chat_history` - AI conversation history
- `social_media_accounts` - Connected social accounts
- `payment_transactions` - Payment and subscription records

**Additional Setup:**

- Enable Row Level Security (RLS) on all tables
- Create storage buckets for carousel images and brand assets
- Configure authentication providers in Supabase Dashboard

## Development

### Adding Dependencies

```bash
uv add package-name              # Add dependency
uv add --optional dev pytest-mock # Add to optional group
uv sync                          # Sync environment
```

### Running the Server

```bash
# Development (auto-reload)
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uv run python main.py
```

## Implementation Status

**Core Infrastructure:** Complete

- Supabase client initialization: IMPLEMENTED
- Configuration and settings: IMPLEMENTED
- Security and JWT validation: IMPLEMENTED

**AI Services:**

- Anthropic service (text + vision): IMPLEMENTED
- Gemini service (image generation via Imagen 4): IMPLEMENTED

**Models (Pydantic Schemas):** Fully defined

- All entity models (User, BrandKit, Campaign, Post): COMPLETE
- All API request/response models: COMPLETE
- Pipeline models (6-step agent I/O): COMPLETE
- Common models (enums, mixins, base classes): COMPLETE

**Agents (AI Pipeline):** Structure complete, implementation in progress

- Base agent class: COMPLETE
- 5 specialized agents: Structure defined, logic pending

**API Endpoints:** Structure complete, implementation in progress

- Route handlers defined
- Dependency injection configured
- Integration with agents pending

**Services:** Structure complete, implementation varies

- Anthropic: IMPLEMENTED
- Gemini: PARTIAL
- Email, Storage, Stripe, Social Media: Structure complete, implementation pending
