# Scale66 API Reference

Backend API documentation for the Scale66 frontend.

- **Base URL:** `http://localhost:8000/api/v1`
- **Auth:** All endpoints (except `/payments/webhook`) require a Supabase JWT in the `Authorization: Bearer <token>` header
- **Interactive docs:** `http://localhost:8000/docs` (Swagger) · `http://localhost:8000/redoc`

---

## API Client

All requests go through the centralized Axios client which automatically injects the Supabase JWT:

```typescript
import { apiClient } from '@/services/api/client';

// GET
const { data } = await apiClient.get<BrandKit>('/api/v1/brand-kits/me');

// POST
const { data } = await apiClient.post<Campaign>('/api/v1/campaigns', { campaign_name: 'My Campaign' });

// PUT
const { data } = await apiClient.put<Campaign>(`/api/v1/campaigns/${id}`, { campaign_name: 'Updated' });

// DELETE
await apiClient.delete(`/api/v1/campaigns/${id}`);
```

---

## Types

```typescript
// Enums
type SubscriptionTier = 'free' | 'starter' | 'growth' | 'agency';
type PostPlatform     = 'instagram' | 'tiktok' | 'linkedin' | 'twitter';
type PostStatus       = 'draft' | 'scheduled' | 'published' | 'failed';
type PaymentStatus    = 'pending' | 'succeeded' | 'failed' | 'refunded';
type SocialPlatform   = 'instagram' | 'tiktok' | 'facebook' | 'twitter' | 'linkedin' | 'youtube';

interface User {
  id: string;
  email: string;
  subscription_tier: SubscriptionTier;
  stripe_customer_id?: string;
  onboarding_completed: boolean;
  created_at: string;
  updated_at: string;
}

interface BrandKit {
  id: string;
  user_id: string;
  brand_name: string;
  brand_niche?: string;
  brand_style?: string;
  customer_pain_points: string[];
  product_service_description?: string;
  created_at: string;
  updated_at: string;
}

interface Campaign {
  id: string;
  user_id: string;
  campaign_name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

interface CarouselSlide {
  slide_number: number;
  slide_type: 'hook' | 'body' | 'cta';
  image_url?: string;
  caption?: string;
}

interface CarouselMetadata {
  carousel_id: string;
  template_id: string;
  format_type: string;
  num_body_slides: number;
  include_cta: boolean;
  total_slides: number;
}

interface Post {
  id: string;
  user_id: string;
  campaign_id: string;
  final_caption?: string;
  final_hashtags?: string;
  image_urls?: string;               // comma-separated URLs
  carousel_slides: CarouselSlide[];
  carousel_metadata: CarouselMetadata;
  platform: PostPlatform;
  status: PostStatus;
  scheduled_for?: string;
  published_at?: string;
  created_at: string;
  updated_at: string;
}

interface PostVariation {
  id: string;
  post_id: string;
  variation_number: number;
  caption?: string;
  hashtags?: string;
  image_urls?: string;
  is_posted: boolean;
  posted_platforms?: string;
  created_at: string;
  updated_at: string;
}

interface SocialAccount {
  id: string;
  user_id: string;
  platform: SocialPlatform;
  platform_user_id: string;
  platform_username?: string;
  is_active: boolean;
  expires_at?: string;
  created_at: string;
  updated_at: string;
  // Note: access_token and refresh_token are never returned in responses
}

interface PaymentTransaction {
  id: string;
  user_id: string;
  stripe_payment_intent_id: string;
  amount: number;
  subscription_tier: SubscriptionTier;
  currency: string;
  payment_method?: string;
  status: PaymentStatus;
  created_at: string;
  updated_at: string;
}
```

---

## Users

### `GET /users/me`
Get the authenticated user's profile.

```typescript
const { data: user } = await apiClient.get<User>('/api/v1/users/me');
```

### `PUT /users/me`
Update the authenticated user's profile. All fields optional.

| Field | Type | Description |
| ----- | ---- | ----------- |
| `subscription_tier` | `SubscriptionTier` | Typically updated via webhook, not directly |
| `onboarding_completed` | `boolean` | Set to `true` at end of onboarding |

```typescript
const { data: user } = await apiClient.put<User>('/api/v1/users/me', {
  onboarding_completed: true,
});
```

---

## Brand Kits

One brand kit per user. Created during onboarding.

### `POST /brand-kits`
Create a brand kit. Required once during onboarding.

| Field | Type | Required |
| ----- | ---- | -------- |
| `brand_name` | `string` (max 255) | Yes |
| `brand_niche` | `string` | No |
| `brand_style` | `string` | No |
| `customer_pain_points` | `string[]` | No |
| `product_service_description` | `string` | No |

```typescript
const { data: brandKit } = await apiClient.post<BrandKit>('/api/v1/brand-kits', {
  brand_name: 'Acme Co',
  brand_niche: 'SaaS productivity tools',
  brand_style: 'Professional and clean',
  customer_pain_points: ['Too many manual tasks', 'Poor team visibility'],
  product_service_description: 'Project management software for remote teams',
});
```

### `GET /brand-kits/me`
Get the authenticated user's brand kit. Returns `404` if not yet created.

```typescript
const { data: brandKit } = await apiClient.get<BrandKit>('/api/v1/brand-kits/me');
```

### `PUT /brand-kits/me`
Update the authenticated user's brand kit. All fields optional — only provided fields are updated.

```typescript
const { data: brandKit } = await apiClient.put<BrandKit>('/api/v1/brand-kits/me', {
  brand_style: 'Bold and energetic',
  customer_pain_points: ['Updated pain point'],
});
```

---

## Campaigns

### `POST /campaigns`

| Field | Type | Required |
| ----- | ---- | -------- |
| `campaign_name` | `string` (max 255) | Yes |
| `description` | `string` | No |

```typescript
const { data: campaign } = await apiClient.post<Campaign>('/api/v1/campaigns', {
  campaign_name: 'Q1 Launch',
  description: 'Content for the Q1 product launch',
});
```

### `GET /campaigns`
List all campaigns. Supports pagination.

| Query param | Default | Max |
| ----------- | ------- | --- |
| `limit` | `100` | `500` |
| `offset` | `0` | — |

```typescript
const { data: campaigns } = await apiClient.get<Campaign[]>('/api/v1/campaigns?limit=20&offset=0');
```

### `GET /campaigns/{id}`
### `PUT /campaigns/{id}`
### `DELETE /campaigns/{id}` → `204 No Content`

---

## Posts & Carousel Generation

### `POST /campaigns/{campaign_id}/carousel` — AI Generation
Runs the full AI pipeline to generate a branded carousel. This can take up to ~3 minutes.

| Field | Type | Required | Notes |
| ----- | ---- | -------- | ----- |
| `campaign_id` | `string` | Yes | Must match the URL parameter |
| `brand_kit_id` | `string` | Yes | Must belong to the authenticated user |
| `user_prompt` | `string` (max 2000) | Yes | Describes the carousel content |
| `platform` | `PostPlatform` | No | Defaults to `"instagram"` |

Returns a fully populated `Post` with `carousel_slides`, `carousel_metadata`, and `image_urls`.

```typescript
const { data: post } = await apiClient.post<Post>(
  `/api/v1/campaigns/${campaignId}/carousel`,
  {
    campaign_id: campaignId,
    brand_kit_id: brandKitId,
    user_prompt: '5 productivity tips for remote workers',
    platform: 'instagram',
  },
  { timeout: 180000 }, // 3-minute timeout — AI pipeline is slow
);

// Access slides
post.carousel_slides.forEach(slide => {
  console.log(slide.slide_type);  // 'hook' | 'body' | 'cta'
  console.log(slide.image_url);
  console.log(slide.caption);
});
```

### `POST /campaigns/{campaign_id}/posts`
Create a manual (non-AI) post within a campaign.

| Field | Type | Required |
| ----- | ---- | -------- |
| `campaign_id` | `string` | Yes |
| `platform` | `PostPlatform` | No (default: `"instagram"`) |
| `status` | `PostStatus` | No (default: `"draft"`) |
| `final_caption` | `string` | No |
| `final_hashtags` | `string` | No |
| `image_urls` | `string` | No (comma-separated URLs) |
| `carousel_slides` | `CarouselSlide[]` | No |
| `carousel_metadata` | `CarouselMetadata` | No |
| `scheduled_for` | `string` (ISO datetime) | No |

### `GET /campaigns/{campaign_id}/posts`
List posts in a campaign. Supports `limit` / `offset` pagination.

### `GET /posts/{id}`
### `PUT /posts/{id}`
All `PostCreate` fields are optional for update, plus `published_at`.

### `DELETE /posts/{id}` → `204 No Content`

---

## Post Variations

Variations are alternative caption/hashtag/image sets for a post.

### `POST /posts/{post_id}/variations`

| Field | Type | Required | Notes |
| ----- | ---- | -------- | ----- |
| `post_id` | `string` | Yes | |
| `variation_number` | `int` | No | Auto-generated if `0` or omitted |
| `caption` | `string` | No | |
| `hashtags` | `string` | No | |
| `image_urls` | `string` | No | |
| `is_posted` | `boolean` | No (default: `false`) | |
| `posted_platforms` | `string` | No | |

### `GET /posts/{post_id}/variations`
### `GET /posts/{post_id}/variations/{variation_id}`
### `PUT /posts/{post_id}/variations/{variation_id}`
### `DELETE /posts/{post_id}/variations/{variation_id}` → `204 No Content`

---

## Social Accounts

### `POST /social-accounts`
Connect a social media account. Returns `409 Conflict` if an account for that platform already exists.

| Field | Type | Required |
| ----- | ---- | -------- |
| `platform` | `SocialPlatform` | Yes |
| `platform_user_id` | `string` | Yes |
| `platform_username` | `string` | No |
| `is_active` | `boolean` | No (default: `true`) |
| `access_token` | `string` | No |
| `refresh_token` | `string` | No |
| `expires_at` | `string` (ISO datetime) | No |

Note: `access_token` and `refresh_token` are stored but **never returned** in responses.

```typescript
const { data: account } = await apiClient.post<SocialAccount>('/api/v1/social-accounts', {
  platform: 'instagram',
  platform_user_id: 'ig_user_123',
  platform_username: '@mybrand',
  access_token: 'oauth_token',
});
```

### `GET /social-accounts`
List connected accounts. Optional `active_only` query param (default: `false`).

```typescript
const { data: accounts } = await apiClient.get<SocialAccount[]>('/api/v1/social-accounts?active_only=true');
```

### `GET /social-accounts/{id}`

### `PUT /social-accounts/{id}`
Used to refresh tokens or update account status. All fields optional.

### `DELETE /social-accounts/{id}` → `204 No Content`
Defaults to a **soft delete** (marks `is_active: false`). Pass `?soft_delete=false` to permanently delete.

```typescript
// Soft delete (default)
await apiClient.delete(`/api/v1/social-accounts/${id}`);

// Hard delete
await apiClient.delete(`/api/v1/social-accounts/${id}?soft_delete=false`);
```

---

## Payments

### `POST /payments/transactions`
Record a new transaction when initiating a Stripe payment. Status is updated later by the webhook.

| Field | Type | Required |
| ----- | ---- | -------- |
| `stripe_payment_intent_id` | `string` | Yes |
| `amount` | `number` (> 0) | Yes |
| `subscription_tier` | `SubscriptionTier` | Yes |
| `currency` | `string` (3 chars, default: `"usd"`) | No |
| `payment_method` | `string` | No |
| `status` | `PaymentStatus` | No (default: `"pending"`) |

### `GET /payments/transactions`
List transactions. Supports `limit` / `offset` pagination.

### `GET /payments/transactions/{id}`

### `POST /payments/webhook`
Stripe webhook handler. Does **not** require authentication.

Handled events:

| Event | Action |
| ----- | ------ |
| `payment_intent.succeeded` | Sets transaction status to `succeeded`, upgrades user subscription tier |
| `payment_intent.payment_failed` | Sets transaction status to `failed` |
| `charge.refunded` | Sets transaction status to `refunded` |

---

## Error Responses

| Status | Meaning |
| ------ | ------- |
| `400` | Bad request — missing/invalid fields or no fields to update |
| `401` | Unauthorized — missing or invalid JWT |
| `404` | Resource not found |
| `409` | Conflict — e.g. social account for that platform already exists |
| `500` | Server error — includes AI pipeline failures |

```typescript
// Errors are thrown by the Axios interceptor and can be caught normally
try {
  const { data } = await apiClient.get<BrandKit>('/api/v1/brand-kits/me');
} catch (error) {
  // 401 → interceptor auto-redirects to login
  // 404 → brand kit not yet created
}
```
