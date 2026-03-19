# Scale66 API Documentation

API reference for frontend developers.

## Configuration

- **Base URL:** `http://localhost:8000/api/v1`
- **Auth:** JWT token via Supabase Auth in `Authorization: Bearer <token>` header

## API Client

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
	const {
		data: { session },
	} = await supabase.auth.getSession();
	if (!session) throw new Error("Not authenticated");

	const response = await fetch(`${API_BASE_URL}${endpoint}`, {
		...options,
		headers: {
			Authorization: `Bearer ${session.access_token}`,
			"Content-Type": "application/json",
			...options.headers,
		},
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || "API request failed");
	}

	return response.json();
}
```

## TypeScript Types

```typescript
// Brand Kit
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

// Campaign
interface Campaign {
	id: string;
	user_id: string;
	campaign_name: string;
	description?: string;
	created_at: string;
	updated_at: string;
}

// Post
type PostPlatform = "instagram" | "tiktok" | "linkedin" | "twitter";
type PostStatus = "draft" | "scheduled" | "published" | "failed";

interface Post {
	id: string;
	user_id: string;
	campaign_id: string;
	final_caption?: string;
	final_hashtags?: string;
	image_urls?: string;
	carousel_slides: CarouselSlide[];
	carousel_metadata: CarouselMetadata;
	platform: PostPlatform;
	status: PostStatus;
	scheduled_for?: string;
	published_at?: string;
	created_at: string;
	updated_at: string;
}

interface CarouselSlide {
	slide_number: number;
	slide_type: "hook" | "body" | "cta";
	image_url: string;
	caption: string;
}

interface CarouselMetadata {
	carousel_id: string;
	template_id: string;
	format_type: string;
	num_body_slides: number;
	include_cta: boolean;
	total_slides: number;
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

// Social Account
type SocialPlatform = "instagram" | "tiktok" | "facebook" | "twitter" | "linkedin" | "youtube";

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
}

// Payment
type SubscriptionTier = "free" | "pro" | "premium";
type PaymentStatus = "pending" | "succeeded" | "failed" | "refunded";

interface PaymentTransaction {
	id: string;
	user_id: string;
	stripe_payment_intent_id: string;
	amount: number;
	subscription_tier: SubscriptionTier;
	status: PaymentStatus;
	currency: string;
	payment_method?: string;
	created_at: string;
	updated_at: string;
}

// User
interface User {
	id: string;
	email: string;
	subscription_tier: SubscriptionTier;
	stripe_customer_id?: string;
	onboarding_completed: boolean;
	created_at: string;
	updated_at: string;
}
```

## Endpoints

### Brand Kits

- `POST /brand-kits` - Create brand kit
- `GET /brand-kits/me` - Get user's brand kit
- `PUT /brand-kits/me` - Update brand kit

```typescript
// Create
const brandKit = await apiRequest<BrandKit>("/brand-kits", {
	method: "POST",
	body: JSON.stringify({
		brand_name: "My Brand",
		brand_niche: "Technology",
		customer_pain_points: ["Problem 1"],
	}),
});

// Get
const brandKit = await apiRequest<BrandKit>("/brand-kits/me");
```

### Campaigns

- `POST /campaigns` - Create campaign
- `GET /campaigns` - List campaigns (`?limit=100&offset=0`)
- `GET /campaigns/{id}` - Get campaign
- `PUT /campaigns/{id}` - Update campaign
- `DELETE /campaigns/{id}` - Delete campaign

```typescript
const campaign = await apiRequest<Campaign>("/campaigns", {
	method: "POST",
	body: JSON.stringify({ campaign_name: "Summer Campaign", description: "..." }),
});
```

### Posts

- `POST /campaigns/{campaign_id}/carousel` - Create carousel post using AI pipeline
- `POST /campaigns/{campaign_id}/posts` - Create post
- `GET /campaigns/{campaign_id}/posts` - List posts in campaign
- `GET /posts/{id}` - Get post
- `PUT /posts/{id}` - Update post
- `DELETE /posts/{id}` - Delete post

```typescript
// Create carousel post using AI pipeline
const carouselPost = await apiRequest<Post>(`/campaigns/${campaignId}/carousel`, {
	method: "POST",
	body: JSON.stringify({
		campaign_id: campaignId,
		brand_kit_id: "brand-kit-id",
		user_prompt: "Create a carousel about productivity tips for remote workers",
		platform: "instagram", // optional, defaults to "instagram"
	}),
});
// Returns Post with carousel_slides, carousel_metadata, and image_urls populated

// Create regular post
const post = await apiRequest<Post>(`/campaigns/${campaignId}/posts`, {
	method: "POST",
	body: JSON.stringify({
		campaign_id: campaignId,
		platform: "instagram",
		status: "draft",
	}),
});
```

### Post Variations

- `POST /posts/{post_id}/variations` - Create variation
- `GET /posts/{post_id}/variations` - List variations
- `GET /posts/{post_id}/variations/{id}` - Get variation
- `PUT /posts/{post_id}/variations/{id}` - Update variation
- `DELETE /posts/{post_id}/variations/{id}` - Delete variation

### Social Accounts

- `POST /social-accounts` - Connect account
- `GET /social-accounts` - List accounts (`?active_only=true`)
- `GET /social-accounts/{id}` - Get account
- `PUT /social-accounts/{id}` - Update account
- `DELETE /social-accounts/{id}` - Disconnect account (`?soft_delete=true`)

```typescript
const account = await apiRequest<SocialAccount>("/social-accounts", {
	method: "POST",
	body: JSON.stringify({
		platform: "instagram",
		platform_user_id: "user123",
		access_token: "token",
	}),
});
```

### Payments

- `POST /payments/transactions` - Record transaction
- `GET /payments/transactions` - List transactions
- `GET /payments/transactions/{id}` - Get transaction

### Users

- `GET /users/me` - Get current user
- `PUT /users/me` - Update current user

```typescript
const user = await apiRequest<User>("/users/me");
await apiRequest<User>("/users/me", {
	method: "PUT",
	body: JSON.stringify({ onboarding_completed: true }),
});
```

## Error Handling

```typescript
interface APIError {
	detail: string;
	status_code: number;
}

try {
	const data = await apiRequest<BrandKit>("/brand-kits/me");
} catch (error) {
	if (error.message.includes("404")) {
		// Resource not found
	} else if (error.message.includes("401")) {
		// Unauthorized - redirect to login
	}
}
```

**Status Codes:** `400` Bad Request, `401` Unauthorized, `404` Not Found, `409` Conflict, `500` Server Error

## Common Patterns

### Creating a Carousel Post

```typescript
// 1. Create carousel post using AI pipeline
const carouselPost = await apiRequest<Post>(`/campaigns/${campaignId}/carousel`, {
	method: "POST",
	body: JSON.stringify({
		campaign_id: campaignId,
		brand_kit_id: brandKitId,
		user_prompt: "Create a carousel about 5 productivity tips for remote workers",
		platform: "instagram",
	}),
});

// 2. Access carousel data
console.log(carouselPost.carousel_slides); // Array of slides with images and captions
console.log(carouselPost.carousel_metadata); // Template info, format type, etc.
console.log(carouselPost.image_urls); // Comma-separated image URLs

// 3. Each slide contains:
carouselPost.carousel_slides.forEach((slide) => {
	console.log(`Slide ${slide.slide_number}: ${slide.slide_type}`);
	console.log(`Image: ${slide.image_url}`);
	console.log(`Caption: ${slide.caption}`);
});
```

### Onboarding Flow

```typescript
// 1. Create brand kit
const brandKit = await apiRequest<BrandKit>("/brand-kits", {
	method: "POST",
	body: JSON.stringify(brandKitData),
});

// 2. Connect social accounts
for (const account of socialAccounts) {
	await apiRequest("/social-accounts", { method: "POST", body: JSON.stringify(account) });
}

// 3. Mark onboarding complete
await apiRequest<User>("/users/me", {
	method: "PUT",
	body: JSON.stringify({ onboarding_completed: true }),
});
```

### Pagination

```typescript
async function fetchAll<T>(endpoint: string): Promise<T[]> {
	const all: T[] = [];
	let offset = 0;
	const limit = 100;

	while (true) {
		const items = await apiRequest<T[]>(`${endpoint}?limit=${limit}&offset=${offset}`);
		if (items.length === 0) break;
		all.push(...items);
		offset += limit;
		if (items.length < limit) break;
	}
	return all;
}
```

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
