# Scale66 Backend

AI-powered carousel content generation platform built with FastAPI and Supabase.

## Tech Stack

- **Framework:** FastAPI + Uvicorn
- **Package Manager:** uv (modern Python package management)
- **Database:** Supabase (PostgreSQL + Auth + Storage)
- **AI Services:**
  - Anthropic Claude (text generation + vision) - IMPLEMENTED
  - Google Imagen 4 (image generation) - IMPLEMENTED
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
    │   ├── carousel_format_decider.py # Format selection
    │   ├── story_generator.py       # Content creation
    │   ├── image_generator.py       # Image generation via Imagen 4
    │   ├── text_generator.py        # Text overlay generation
    │   └── finalizer.py             # Final composition
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
    │   │   └── gemini_service.py    # Imagen 4 integration
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

### AI Pipeline

**6-step sequential process for carousel generation:**

1. **Orchestrator** - Coordinates entire pipeline and manages state
2. **Format Decider** - Selects optimal carousel format and structure
3. **Story Generator** - Creates hook, script, and splits content into slides
4. **Image Generator** - Generates AI images for slides using Imagen 4
5. **Text Generator** - Creates on-screen text with styling
6. **Finalizer** - Overlays text on images using Claude Vision + Pillow

**AI Models:**
- Claude Sonnet 4.5 (text generation and complex reasoning)
- Claude Vision (image analysis for text placement)
- Imagen 4.0 (image generation)

**Data Flow:**
- Fully typed with Pydantic schemas in `models/pipeline.py`
- Sequential execution with dependencies (each step receives output from previous)
- Base agent class provides error handling and service access

**Implementation Status:** Agent structure defined, core logic in progress

### API Endpoints

Base URL: `http://localhost:8000/api/v1`

**Key Endpoints:**
- `/content/generate` - Trigger AI carousel generation (CORE)
- `/content/status/{job_id}` - Check generation status
- `/brand-kit` - Brand kit CRUD operations
- `/campaigns` - Campaign management
- `/posts` - Post management and publishing
- `/social/connect/{platform}` - Social media OAuth
- `/payment/create-checkout-session` - Stripe checkout
- `/payment/webhook` - Stripe webhook handler

**Authentication:**
- Frontend handles auth via Supabase Auth
- Backend validates JWT tokens from Supabase
- All protected endpoints use `get_current_user()` dependency

**Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Implementation Status:** Route structure defined, handlers in progress

### Core Configuration

**config.py** - Application settings
- Environment variable validation via Pydantic
- API keys: Anthropic, Gemini, Supabase, Stripe, Resend
- Model configuration: Claude Sonnet 4.5, Imagen 4.0
- Logging and server settings

**logging.py** - Centralized logging
- Application-wide logging configuration
- Environment-aware (development/production)
- Console and file output with rotation

**security.py** - Authentication
- JWT token validation (Supabase-issued)
- Bearer token extraction
- User authentication dependency

**supabase.py** - Database client
- RLS-aware client for user operations
- Admin client for system operations
- FastAPI dependencies for route injection
- Singleton pattern for efficiency

**Implementation Status:** Fully implemented and operational

### CRUD Operations

**Purpose:** Abstract database operations into reusable methods

**Pattern:**
- Base CRUD class with generic operations (create, read, update, delete)
- Entity-specific implementations for complex queries
- Respects Row Level Security policies

**Entities:**
- Brand Kit - Brand profile and settings
- Campaign - Campaign management
- Post - Generated content and variations
- User - User profile and preferences
- Session - User session tracking

**Implementation Status:** Structure defined, operations in progress

### Pydantic Models

**Purpose:** Type-safe request/response validation and serialization

**Model Types:**
- Entity models (User, BrandKit, Campaign, Post)
- API request/response schemas (Create, Update, Response)
- Pipeline schemas (6-step agent input/output models)
- Common schemas (MessageResponse, ErrorResponse, enums)

**Pipeline Schemas:**
1. OrchestratorInput
2. CarouselFormatDeciderInput/Output
3. StoryGeneratorInput/Output
4. ImageGeneratorInput/Output
5. TextGeneratorInput/Output
6. FinalizerInput/Output

**Benefits:**
- Automatic validation and type checking
- OpenAPI documentation generation
- Type safety across the application

**Implementation Status:** Fully defined and validated

### Services

**AI Services (IMPLEMENTED):**
- **Anthropic Service** - Claude API integration
  - Text generation with Claude Sonnet 4.5
  - Image analysis with Claude Vision
  - Configurable parameters (temperature, max_tokens)
  - Singleton pattern with async client
  
- **Gemini Service** - Imagen 4 integration
  - Image generation with configurable aspect ratio (1:1, 3:4, 4:3, 9:16, 16:9)
  - Size options (1K, 2K)
  - Base64 encoded output
  - Error handling and logging

**Other Services (Structure Defined):**
- Email Service - Resend API for transactional emails
- Image Overlay Service - Pillow-based text overlays
- Social Media Service - Instagram/TikTok OAuth and posting
- Storage Service - Supabase Storage/S3 file management
- Stripe Service - Payment processing and webhooks

### Utilities

**Purpose:** Pure helper functions for common operations

**Modules:**
- file_handlers.py - File upload/download validation
- formatters.py - Date formatting and JSON transformations
- validators.py - Input validation (email, URLs, colors)

**Pattern:** Stateless functions with no business logic

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
2. Set up database schema via SQL Editor or Dashboard
3. Configure authentication providers
4. Enable Row Level Security on all tables
5. Create storage buckets for images and brand assets
6. Copy credentials to `.env` file

**Required Tables:**
- users - User profiles and settings
- brand_kits - Brand configurations
- campaigns - Campaign management
- posts - Generated content
- post_variations - Content variations
- social_media_accounts - OAuth connections
- payment_transactions - Billing records

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
- Supabase client with RLS support
- AI services (Anthropic Claude + Imagen 4)
- Pydantic models and schemas (all entities + pipeline)
- Base agent class with error handling

**In Progress:**
- AI pipeline agents (6-step sequential process)
- API endpoint handlers
- CRUD operations
- External service integrations (email, storage, payments, social media)

**Architecture Ready:**
- FastAPI application structure
- Dependency injection system
- JWT authentication flow
- Error handling and logging
- Type-safe data models
