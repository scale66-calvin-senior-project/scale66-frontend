# Cursor Rules Organization

This directory contains Cursor AI rules organized by category to maintain consistency and best practices across the codebase.

## Folder Structure

```
.cursor/rules/
├── backend/
│   ├── api/              # FastAPI endpoint patterns and conventions
│   ├── database/         # Supabase integration and database patterns
│   ├── agents/           # AI agent development patterns
│   └── patterns/         # Design patterns (singleton, DI, etc.)
├── frontend/
│   ├── architecture/     # Feature modules, state, routing
│   ├── components/       # Component structure and patterns
│   ├── hooks/            # Custom React hooks patterns
│   └── services/         # API clients and service integrations
├── meta/                 # Project-wide and documentation rules
└── README.md             # This file
```

## Current Rules

### Backend

**API** (`backend/api/`)
- `fastapi-endpoints.mdc` - RESTful endpoint patterns, CRUD operations, dependency injection

**Database** (`backend/database/`)
- `supabase-integration.mdc` - Supabase client usage, query patterns, RLS, storage

**Agents** (`backend/agents/`)
- `ai-agent-pattern.mdc` - BaseAgent implementation, pipeline integration, error handling

**Patterns** (`backend/patterns/`)
- `singleton-pattern.mdc` - Singleton implementation for services and agents

### Frontend

**Architecture** (`frontend/architecture/`)
- `feature-modules.mdc` - Feature-based organization, barrel exports, module patterns

**Components** (`frontend/components/`)
- `frontend-components.mdc` - Component structure, CSS Modules, props patterns

### Meta

**Project-Wide** (`meta/`)
- `cursor-rules.mdc` - How to create and organize Cursor rules
- `project-structure.mdc` - Monorepo structure and navigation
- `self-improvement.mdc` - Rule improvement and maintenance
- `update-readme.mdc` - README update guidelines

## Adding New Rules

See `meta/cursor-rules.mdc` for detailed instructions on creating new rules.

Quick guidelines:
1. Choose the appropriate category folder
2. Use kebab-case for filenames (e.g., `my-new-rule.mdc`)
3. Include frontmatter with description and globs
4. Provide clear examples of good and bad patterns
5. Document when to use vs when not to use

## Rule Categories

### When to add to each folder:

**backend/api/** - Endpoint structure, middleware, routing, request/response handling

**backend/database/** - Database queries, migrations, ORM patterns, data access

**backend/agents/** - AI agent implementation, orchestration, prompts, pipelines

**backend/patterns/** - Reusable design patterns, architectural patterns

**frontend/architecture/** - App structure, state management, routing, module organization

**frontend/components/** - UI components, styling, testing, accessibility

**frontend/hooks/** - Custom hooks creation, data fetching, form management

**frontend/services/** - API clients, external integrations, service layer

**meta/** - Project-wide rules, documentation, processes, improvements

## Maintenance

Rules should be:
- Reviewed periodically for relevance
- Updated when patterns change
- Removed if no longer applicable
- Cross-referenced with related rules

See `meta/self-improvement.mdc` for the rule improvement process.


