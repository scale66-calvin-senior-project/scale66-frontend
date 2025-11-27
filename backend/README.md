# Scale66 Backend

AI-powered carousel content generation platform built with FastAPI and Supabase.

## Tech Stack

- **Framework:** FastAPI + Uvicorn
- **Package Manager:** uv (modern Python package management)
- **Database:** Supabase (PostgreSQL + Auth + Storage)
- **AI Services:**
  - Anthropic Claude (text generation + vision) - IMPLEMENTED
  - Google Gemini (image generation) - IMPLEMENTED
- **Image Processing:** Pillow (PIL)
- **Payment:** Stripe
- **Email:** Resend
- **Authentication:** Supabase Auth JWT validation

## Quick Start

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup and run
cd backend
uv sync                          # Install dependencies
cp .env.example .env            # Configure environment
uv run uvicorn main:app --reload # Start server (http://localhost:8000)
```

## File Structure

```
backend/
├── main.py                    # FastAPI application entry point
├── pyproject.toml            # Python dependencies and project config
├── uv.lock                   # Dependency lock file
├── pyrightconfig.json        # Type checking configuration
│
└── app/
    ├── agents/               # AI pipeline (6-step sequential process)
    │   ├── base_agent.py            # Base class with error handling
    │   ├── orchestrator.py          # Pipeline coordinator
    │   ├── carousel_format_decider.py # Format selection - IMPLEMENTED
    │   ├── story_generator.py       # Story/narrative generation - IMPLEMENTED
    │   ├── image_generator.py       # Image generation via Gemini - IMPLEMENTED
    │   ├── text_generator.py        # Text overlay generation - IMPLEMENTED
    │   └── finalizer.py             # Image composition & upload - IMPLEMENTED
    │
    ├── api/                  # REST API endpoints
    │   ├── deps.py                  # Dependency injection
    │   └── v1/                      # API version 1
    │       ├── brand_kit.py         # Brand kit CRUD
    │       ├── campaigns.py         # Campaign management
    │       ├── content.py           # AI content generation
    │       ├── posts.py             # Post management
    │       ├── social.py            # Social media integration
    │       └── payment.py           # Stripe integration
    │
    ├── core/                 # Core configuration
    │   ├── config.py                # Environment settings
    │   ├── logging.py               # Logging configuration
    │   ├── security.py              # JWT validation
    │   └── supabase.py              # Supabase client
    │
    ├── crud/                 # Database operations
    │   ├── base.py                  # Base CRUD class
    │   ├── brand_kit.py             # Brand kit operations
    │   ├── campaign.py              # Campaign operations
    │   ├── post.py                  # Post operations
    │   ├── session.py               # Session management
    │   └── user.py                  # User operations
    │
    ├── models/               # Pydantic schemas
    │   ├── brand_kit.py             # Brand kit schemas
    │   ├── campaign.py              # Campaign schemas
    │   ├── post.py                  # Post schemas
    │   ├── user.py                  # User schemas
    │   ├── social.py                # Social media schemas
    │   ├── payment.py               # Payment schemas
    │   ├── content.py               # Content generation schemas
    │   ├── common.py                # Shared schemas and enums
    │   └── pipeline.py              # AI pipeline schemas
    │
    ├── services/             # External integrations
    │   ├── ai/
    │   │   ├── anthropic_service.py # Claude API integration
    │   │   └── gemini_service.py    # Gemini image generation
    │   ├── email_service.py         # Resend email
    │   ├── image_overlay_service.py # Image composition
    │   ├── social_media_service.py  # Social platform APIs
    │   ├── storage_service.py       # File storage
    │   └── stripe_service.py        # Payment processing
    │
    └── utils/                # Utility functions
        ├── file_handlers.py         # File operations
        ├── formatters.py            # Data formatting
        └── validators.py            # Input validation
```

## Architecture Overview

### AI Pipeline - IMPLEMENTED

**6-step sequential carousel generation:**

1. **Orchestrator** - Coordinates pipeline and manages state flow
2. **Format Decider** - Analyzes content request and selects optimal carousel format (12 format types)
3. **Story Generator** - Creates compelling hook and body slide narratives aligned to format
4. **Image Generator** - Generates AI images for each slide using Gemini (9:16 aspect ratio)
5. **Text Generator** - Uses Claude Vision to analyze images and generate text overlays with styling
6. **Finalizer** - Overlays text on images using Pillow and uploads to Supabase Storage

**AI Models:**

- Claude Sonnet 4.5 (format decisions, story generation, text generation)
- Claude Vision (image analysis for text placement)
- Gemini (image generation - supports multiple models)

**Implementation Status:** All 5 agents fully implemented

### API Endpoints

Base URL: `http://localhost:8000/api/v1`

**Key Endpoints:**

- `/content/generate` - Trigger AI carousel generation (CORE)
- `/content/status/{job_id}` - Check generation status
- `/brand-kit` - Brand kit CRUD operations
- `/campaigns` - Campaign management
- `/posts` - Post management
- `/social/connect/{platform}` - Social media OAuth
- `/payment/create-checkout-session` - Stripe checkout

**Authentication:**

- Frontend handles auth via Supabase Auth
- Backend validates JWT tokens
- All protected endpoints use `get_current_user()` dependency

**Documentation:**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Implementation Status:** Route structure defined, integration in progress

### Core Configuration

**config.py** - Application settings

- Environment variable validation via Pydantic
- API keys: Anthropic, Gemini, Supabase, Stripe, Resend
- Model configuration and logging settings

**logging.py** - Centralized logging

- Application-wide configuration
- Environment-aware (development/production)
- Console and file output with rotation

**security.py** - Authentication

- JWT token validation (Supabase-issued)
- User authentication dependency

**supabase.py** - Database client

- RLS-aware client for user operations
- Admin client for system operations
- FastAPI dependencies with singleton pattern

**Implementation Status:** Fully operational

### CRUD Operations

**Purpose:** Abstract database operations into reusable methods

**Pattern:**

- Base CRUD class with generic operations (create, read, update, delete)
- Entity-specific implementations for complex queries
- Respects Row Level Security policies

**Entities:**

- Brand Kit, Campaign, Post, User, Session

**Implementation Status:** Structure defined, operations in progress

### Pydantic Models

**Purpose:** Type-safe request/response validation and serialization

**Model Types:**

- Entity models (User, BrandKit, Campaign, Post)
- API request/response schemas (Create, Update, Response)
- Pipeline schemas (6-step agent I/O models)
- Common schemas (MessageResponse, ErrorResponse, enums)

**Benefits:**

- Automatic validation and type checking
- OpenAPI documentation generation
- Type safety across application

**Implementation Status:** Fully defined and validated

### Services

**AI Services - IMPLEMENTED:**

- **Anthropic Service** - Claude API integration
  - Text generation (Claude Sonnet 4.5)
  - Image analysis (Claude Vision)
  - Async client with error handling
- **Gemini Service** - Image generation integration
  - Supports gemini-3-pro-image-preview and gemini-2.5-flash-image
  - Image generation with aspect ratio control
  - Size options (1K, 2K, 4K on gemini-3-pro)
  - Base64 encoded output

**Other Services:**

- Email Service - Resend API (structure defined)
- Social Media Service - Instagram/TikTok OAuth (structure defined)
- Storage Service - Supabase Storage (structure defined)
- Stripe Service - Payment processing (structure defined)

### Utilities

**Purpose:** Pure helper functions for common operations

**Modules:**

- file_handlers.py - File upload/download validation
- formatters.py - Date formatting and transformations
- validators.py - Input validation (email, URLs, colors)

## Environment Variables

Required environment variables:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# AI Services (Required for core functionality)
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
GEMINI_IMAGE_MODEL=gemini-3-pro-image-preview  # or gemini-2.5-flash-image

# Optional Services
RESEND_API_KEY=re_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
INSTAGRAM_CLIENT_ID=...
INSTAGRAM_CLIENT_SECRET=...
TIKTOK_CLIENT_KEY=...
TIKTOK_CLIENT_SECRET=...

# Application
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
LOG_LEVEL=INFO
```

Copy `.env.example` and configure with your API keys.

## Database Setup

**Supabase Configuration:**

1. Create project at https://supabase.com
2. Set up database schema via SQL Editor
3. Enable Row Level Security on all tables
4. Create storage bucket: `carousel-slides` (public)
5. Configure authentication providers
6. Copy credentials to `.env` file

**Required Tables:**

- users, brand_kits, campaigns, posts, social_media_accounts, payment_transactions

## Development

**Managing Dependencies:**

```bash
uv add package-name           # Add new dependency
uv add --dev package-name     # Add development dependency
uv sync                       # Sync virtual environment
uv lock                       # Update lock file
```

**Running the Server:**

```bash
# Development with auto-reload
uv run uvicorn main:app --reload

# Production
uv run python main.py
```

**API Documentation:**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Implementation Status

**Complete:**

- Core infrastructure (config, logging, security, database)
- AI services (Anthropic Claude + Google Gemini image generation)
- Pydantic models and schemas (all entities + pipeline)
- AI pipeline agents (all 5 agents fully implemented)
- Base agent class with error handling
- Model-agnostic Gemini integration (gemini-3-pro, gemini-2.5-flash)

**In Progress:**

- Orchestrator implementation (pipeline coordination)
- API endpoint handlers (agent integration)
- CRUD operations
- External service integrations (email, social, payments)
