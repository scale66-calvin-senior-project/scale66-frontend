# Scale66

AI-powered marketing platform for software startups. Turn attention into paying customers through AI-generated social media content.

## Overview

Scale66 helps small software founders:

- Build an online brand that converts
- Automate social content distribution
- Understand what content drives growth

## Tech Stack

### Backend (FastAPI)

- **Framework:** FastAPI + Uvicorn
- **Package Manager:** uv
- **Database:** Supabase (PostgreSQL + Auth + Storage)
- **AI Services:**
  - Anthropic Claude Sonnet 4.5 (text + vision) - IMPLEMENTED
  - Google Gemini (image generation) - IMPLEMENTED
- **Image Processing:** Pillow
- **Payment:** Stripe
- **Email:** Resend

### Frontend (Next.js)

- **Framework:** Next.js 15 (App Router with Turbopack)
- **Language:** TypeScript (Strict Mode)
- **Styling:** CSS Modules
- **Authentication:** Supabase Auth (JWT tokens)
- **Backend API:** Axios with automatic JWT injection
- **Package Manager:** npm

### Infrastructure

- **Version Control:** Git with GitHub
- **Branch Strategy:** `dev` (development) → `main` (production)
- **CI/CD:** GitHub Actions (automated testing and deployment)

## Getting Started

### Prerequisites

- Python 3.11+ (for backend)
- Node.js 18+ (for frontend)
- Supabase account (for database and auth)
- API keys for Anthropic and Google Gemini

### Backend Setup

```bash
cd backend

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Add your API keys to .env

# Run development server
uv run uvicorn main:app --reload
# Runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Add Supabase credentials and backend API URL

# Run development server
npm run dev
# Runs at http://localhost:3000
```

### Running Both Services

Run in separate terminals:

```bash
# Terminal 1 - Backend
cd backend && uv run uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend && npm run dev
```

## Project Structure

```
scale66/
├── backend/                    # FastAPI backend (Python)
│   ├── app/
│   │   ├── agents/                # AI pipeline (orchestrator + 5 agents)
│   │   ├── api/v1/                # REST API endpoints
│   │   ├── core/                  # Config, security, database
│   │   ├── crud/                  # Database operations
│   │   ├── models/                # Pydantic schemas
│   │   ├── services/              # External integrations
│   │   └── utils/                 # Utility functions
│   ├── output/                # Generated carousel output
│   └── main.py                # Application entry point
│
├── frontend/                   # Next.js frontend (TypeScript)
│   └── src/
│       ├── app/                   # App Router (pages & layouts)
│       ├── components/            # UI components
│       ├── features/              # Feature modules
│       ├── services/              # API service layer
│       ├── lib/                   # Supabase, Stripe
│       └── types/                 # TypeScript types
│
├── figma-design/               # UI/UX design references
│   ├── onboarding-*.png           # Onboarding flow mockups
│   ├── canvas-*.png               # Canvas editor designs
│   └── dashboard-*.png            # Dashboard designs
│
└── README.md                   # This file
```

**Detailed Documentation:**

- Backend: See [`backend/README.md`](backend/README.md)
- Frontend: See [`frontend/README.md`](frontend/README.md)

## Key Features

### AI Pipeline (Backend)

Sequential carousel generation pipeline orchestrated by Orchestrator agent:

1. **Orchestrator** - Coordinates entire pipeline and manages state
2. **Format Decider** - Selects optimal carousel format (12 format types)
3. **Story Generator** - Creates verbose hook and body slide narratives
4. **Text Generator** - Converts stories into short captions
5. **Image Generator** - Generates images with text rendered via Gemini 3 Pro
6. **Finalizer** - Validates quality via Claude Vision and uploads to storage

**Models Used:**

- Claude Sonnet 4.5 for text generation and caption extraction
- Claude Vision for image quality validation and OCR
- Gemini 3 Pro for image generation with text rendering (9:16 aspect ratio)

### Feature-Based Architecture (Frontend)

Each feature is self-contained:

- Auth - Authentication via Supabase
- Dashboard - Campaign overview
- Canvas - AI content generation (CORE)
- Brand Kit - Brand profile management
- Campaigns - Campaign management
- Posting - Social media publishing

**Key Principle:** Supabase handles authentication only. All other operations go through backend API.

## Development Workflow

**Branch Strategy:**

- `dev` - Development environment (preview deployments)
- `main` - Production environment (live deployments)

**Typical Flow:**

```bash
# Create feature branch
git checkout dev
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Add your feature"

# Push and create PR to dev
git push origin feature/your-feature-name

# After review, merge to dev
# After testing in dev, merge to main for production
```

**Branch Naming:**

- Features:
  `{frontend}/feature/[name]`
  `{backend}/[name]`
- Fixes: `{backend,frontend}/fix/[name]`

## Contributing

1. Fork the repository
2. Create a feature branch from `dev`
3. Make your changes following project conventions
4. Open a Pull Request to `dev`
5. Address review feedback
6. Merge after approval

**Pull Request Requirements:**

- At least one reviewer approval
- All automated checks passing
- Follows project coding conventions
- Includes tests where applicable

## Environment Setup

**Required API Keys:**

- Supabase (database + auth)
- Anthropic Claude API
- Google Gemini API
- Stripe (payment processing)
- Resend (email)

**Optional:**

- Instagram API credentials
- TikTok API credentials

See `.env.example` files in backend and frontend directories.

## Implementation Status

**Backend:**

- Core infrastructure: Complete
- AI services: Implemented (Anthropic, Gemini)
- Pydantic models: Complete
- AI pipeline: Implemented (all 5 agents + orchestrator)
- API endpoints: In progress

**Frontend:**

- Project structure: Complete
- Landing pages: Complete
- Component library: Complete
- API service layer: Complete
- Feature implementation: In progress

## Documentation

- [Backend Documentation](backend/README.md) - FastAPI, AI pipeline, database
- [Frontend Documentation](frontend/README.md) - Next.js, components, features
- API Documentation: http://localhost:8000/docs (when backend running)
