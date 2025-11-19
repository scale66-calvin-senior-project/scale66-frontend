# Scale66 Backend

AI-powered carousel content generation platform built with FastAPI, Supabase, and AI agents.

## Tech Stack

- **Framework:** FastAPI + Uvicorn
- **Package Manager:** uv (fast, modern Python package management)
- **Database:** Supabase (PostgreSQL + Auth + Storage)
- **AI Services:** OpenAI (GPT-4) + Google Gemini
- **Image Processing:** Pillow
- **Payment:** Stripe
- **Email:** Resend
- **Authentication:** Supabase Auth + JWT

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

## Project Structure

```
backend/
├── app/
│   ├── agents/              # 6-step AI pipeline
│   │   ├── orchestrator.py
│   │   ├── carousel_format_decider.py
│   │   ├── story_generator.py
│   │   ├── image_generator.py
│   │   ├── text_generator.py
│   │   └── finalizer.py
│   ├── api/v1/             # API endpoints
│   │   ├── auth.py
│   │   ├── brand_kit.py
│   │   ├── campaigns.py
│   │   ├── content.py      # AI generation
│   │   ├── posts.py
│   │   ├── social.py
│   │   └── payment.py
│   ├── core/               # Config, auth, Supabase
│   ├── crud/               # Database operations
│   ├── services/           # External integrations
│   │   ├── ai/            # OpenAI + Gemini
│   │   ├── storage_service.py
│   │   ├── stripe_service.py
│   │   └── social_media_service.py
│   └── utils/              # Helpers
├── supabase/
│   └── migrations/         # Database schema
├── main.py                 # FastAPI app
└── pyproject.toml          # Dependencies
```

## AI Pipeline

**6-step carousel generation flow:**

1. **Orchestrator** - Coordinates entire pipeline
2. **Format Decider** - Selects optimal carousel format (educational, problem-solution, etc.)
3. **Story Generator** - Creates hook → script → splits into slides
4. **Image Generator** - Generates AI images for all slides
5. **Text Generator** - Creates on-screen text with styling
6. **Finalizer** - Overlays text on images (LLM vision + Pillow)

**Output:** Ready-to-post carousel slides

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Core Endpoints

```
Auth:        POST /auth/{signup,login,logout}, GET /auth/me
Brand Kit:   POST,GET,PUT,DELETE /brand-kit
Campaigns:   GET,POST /campaigns, GET,PUT,DELETE /campaigns/{id}
Content:     POST /content/generate, GET /content/status/{job_id}
Posts:       GET,POST /posts, GET,PUT,DELETE /posts/{id}, POST /posts/{id}/publish
Social:      GET /social/connect/{platform}, GET /social/accounts
Payment:     POST /payment/create-checkout-session, POST /payment/webhook
Health:      GET /health
```

**API Docs:** http://localhost:8000/docs (Swagger) | http://localhost:8000/redoc (ReDoc)

## Environment Variables

```env
# Supabase (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# AI Services (Required)
OPENAI_API_KEY=sk-...
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
- Authentication configured

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

**Current Status:** 🟡 Structure complete, ready for implementation

All files contain:

- ✅ Class/function signatures with type hints
- ✅ Comprehensive docstrings
- ✅ TODO comments with examples
- ❌ Implementation pending (by design)

### Implementation Priority

1. **Core Infrastructure** - Supabase client, auth, CRUD operations
2. **API Endpoints** - Authentication, brand kit, campaigns
3. **AI Pipeline** - Implement agents (2 → 3 → 4 → 5 → 6 → 1)
4. **Services** - Storage, email, social OAuth, Stripe

## Branch Strategy

**Naming:** `backend/{feature,fix,refactor}/[name]`

## License

Proprietary – Scale66 internal use only.
