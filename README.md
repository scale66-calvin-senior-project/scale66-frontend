# Scale66

**The AI-powered marketing platform for software startups** — designed to help you turn attention into paying customers through organic, authentic, and data-driven content.

## Overview

Scale66 helps small software founders:

- Build an online brand that actually converts
- Automate social content distribution across platforms
- Understand what content drives customer growth

## Tech Stack

### Backend

- **Framework:** FastAPI (Python 3.11+)
- **Package Manager:** uv
- **Database/Auth:** Supabase (PostgreSQL)
- **AI Services:** Anthropic (Claude), Google Gemini
- **Payment:** Stripe
- **Email:** Resend

### Frontend

- **Framework:** Next.js 15 (App Router) with React 19
- **Language:** TypeScript (Strict Mode)
- **Styling:** CSS Modules
- **Auth/Database:** Supabase
- **HTTP Client:** Axios
- **Package Manager:** npm

### Infrastructure

- **CI/CD:** GitHub Actions
- **Branch Strategy:** dev (development) → main (production)

---

## Getting Started

### Backend Setup

```bash
cd backend

# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run development server
uv run uvicorn main:app --reload
# Server runs at http://localhost:8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Run development server
npm run dev
# Server runs at http://localhost:3000
```

### Running Both Services

For local development, run both backend and frontend in separate terminals:

```bash
# Terminal 1 - Backend
cd backend && uv run uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend && npm run dev
```

---

## Project Structure

```
scale66/
├── backend/          # FastAPI backend (Python)
│   ├── app/
│   │   ├── agents/   # AI pipeline agents
│   │   ├── api/      # API endpoints (v1)
│   │   ├── core/     # Configuration & security
│   │   ├── crud/     # Database operations
│   │   ├── models/   # Pydantic schemas
│   │   ├── services/ # External integrations (AI, payment, email)
│   │   └── utils/    # Utility functions
│   └── main.py       # Application entry point
│
├── frontend/         # Next.js frontend (TypeScript)
│   └── src/
│       ├── app/      # Next.js App Router (pages & layouts)
│       ├── components/ # Reusable components
│       ├── features/ # Feature-based modules
│       ├── hooks/    # Custom React hooks
│       ├── services/ # API service layer
│       ├── lib/      # Third-party integrations
│       └── types/    # TypeScript types
│
└── README.md         # This file
```

For detailed architecture documentation:

- Backend: See `backend/README.md`
- Frontend: See `frontend/README.md`

---

## Branch Workflow

- **`dev`** → development environment (preview deployments)
- **`main`** → production environment (live deployments)

**Typical flow:**

```bash
git checkout dev
git add .
git commit -m "New feature"
git push origin dev

# After testing, merge to main
git checkout main
git merge dev
git push origin main
```

---

## CI/CD Setup

- Every push to `dev` triggers preview deployments
- Every push to `main` updates production
- GitHub Actions handles build & test checks automatically

---

## Contributing

1. Fork the repository
2. Create a feature branch from `dev`
3. Make your changes
4. Open a Pull Request to `dev`
5. After review and approval, merge to `dev`
6. Once stable, `dev` can be merged into `main` for production

### Pull Request Reviews

- Every Pull Request must be reviewed and approved by at least one collaborator
- Automated checks must pass before merging
- Code should follow project conventions (see backend/frontend README files)
- Features should be well-tested before merging to `main`
