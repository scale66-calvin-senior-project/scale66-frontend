"""
API v1 - Version 1 API endpoints.

Available routers:
- brand_kit: Brand kit CRUD operations
- campaigns: Campaign management
- content: AI content generation (CORE FEATURE)
- posts: Post management
- social: Social media OAuth and publishing
- payment: Stripe webhook handlers

Authentication:
- Frontend handles auth directly with Supabase Auth
- Backend validates JWT tokens via get_current_user dependency
- No auth endpoints in backend (signup/login handled by frontend → Supabase)
"""

