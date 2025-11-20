# Firebase → Supabase Migration Summary

## Changes Made

### ✅ Deleted Files
- `src/lib/firebase.ts` - Removed Firebase SDK
- `firebase.json` - Removed Firebase Hosting config
- `.firebaserc` - Removed Firebase project config

### ✅ Created Files
- `src/lib/supabase.ts` - Minimal Supabase client (auth only)
- `.env.local.example` - Environment variables template

### ✅ Updated Files
- `package.json` - Removed `firebase`, added `@supabase/supabase-js` and `axios`
- `src/config/env.ts` - Replaced Firebase env vars with Supabase
- `src/middleware.ts` - Updated auth comments to reference Supabase
- `next.config.ts` - Removed Firebase comments, added Supabase image domains
- `src/services/api/client.ts` - Complete Axios client with JWT injection
- `src/services/api/interceptors.ts` - Error handling and logging
- `README.md` - Updated tech stack and architecture documentation

---

## Architecture Overview

### Before (Firebase)
```
Frontend → Firebase Auth → Firebase JWT → ❌ Backend (incompatible)
Frontend → Firebase Firestore → Direct DB access
```

### After (Supabase)
```
Frontend → Supabase Auth → Supabase JWT → ✅ Backend (validates)
Frontend → Backend API → Supabase PostgreSQL
```

---

## Frontend Supabase Usage

### ✅ ALLOWED (Auth Only)
```typescript
import { supabase } from '@/lib/supabase'

// Login
await supabase.auth.signInWithPassword({ email, password })

// Signup
await supabase.auth.signUp({ email, password })

// Logout
await supabase.auth.signOut()

// Get session
const { data: { session } } = await supabase.auth.getSession()

// Listen to auth changes
supabase.auth.onAuthStateChange((event, session) => { ... })
```

### ❌ NOT ALLOWED (Use Backend API Instead)
```typescript
// ❌ Don't do this in frontend
await supabase.from('brand_kits').select()
await supabase.from('campaigns').insert()
await supabase.storage.from('images').upload()

// ✅ Do this instead
import { apiClient } from '@/services/api/client'

await apiClient.get('/api/v1/brand-kit')
await apiClient.post('/api/v1/campaigns', data)
await apiClient.post('/api/v1/upload', formData)
```

---

## API Client Usage

### Automatic JWT Injection

All API requests automatically include the JWT token:

```typescript
import { apiClient } from '@/services/api/client'

// JWT token is automatically added to Authorization header
const { data } = await apiClient.get('/api/v1/brand-kit')
// → Request includes: Authorization: Bearer <jwt-token>
```

### Example: Brand Kit Service

```typescript
// features/brand-kit/services/brand-kit.service.ts
import { apiClient } from '@/services/api/client'
import { BrandKit, BrandKitCreate } from '../types'

export const brandKitService = {
  getBrandKit: async (): Promise<BrandKit> => {
    const { data } = await apiClient.get('/api/v1/brand-kit')
    return data
  },
  
  createBrandKit: async (brandData: BrandKitCreate): Promise<BrandKit> => {
    const { data } = await apiClient.post('/api/v1/brand-kit', brandData)
    return data
  },
  
  updateBrandKit: async (brandData: Partial<BrandKit>): Promise<BrandKit> => {
    const { data } = await apiClient.put('/api/v1/brand-kit', brandData)
    return data
  },
}
```

---

## Next Steps

### 1. Install New Dependencies
```bash
npm install
```

### 2. Update Environment Variables
```bash
cp .env.local.example .env.local
# Fill in your Supabase credentials
```

### 3. Implement Auth Context

Update `src/context/AuthContext.tsx`:

```typescript
import { supabase } from '@/lib/supabase'
import { useEffect, useState } from 'react'

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session?.user ?? null)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading }}>
      {children}
    </AuthContext.Provider>
  )
}
```

### 4. Implement Login/Signup

Update `src/features/auth/services/auth.service.ts`:

```typescript
import { supabase } from '@/lib/supabase'

export const authService = {
  login: async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    if (error) throw error
    return data
  },

  signup: async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    })
    if (error) throw error
    return data
  },

  logout: async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  },
}
```

### 5. Test the Flow

1. User signs up/logs in → Supabase Auth
2. Frontend gets JWT token
3. All API calls include JWT token automatically
4. Backend validates JWT and processes requests

---

## Benefits

✅ **Security** - Single source of truth for business logic (backend)
✅ **Cost Control** - Backend can rate limit AI API calls
✅ **Type Safety** - Backend validates all data before DB
✅ **Monitoring** - Centralized logging and error tracking
✅ **Simplicity** - Frontend only handles UI and auth

---

## Troubleshooting

### Issue: "Missing Supabase environment variables"
**Solution:** Copy `.env.local.example` to `.env.local` and add your Supabase credentials

### Issue: 401 Unauthorized on API calls
**Solution:** 
1. Check if user is logged in: `const session = await supabase.auth.getSession()`
2. Verify backend JWT validation is working
3. Check that Supabase URL and keys match between frontend/backend

### Issue: CORS errors
**Solution:** Backend must allow frontend origin in CORS middleware

---

## Resources

- [Supabase Auth Docs](https://supabase.com/docs/guides/auth)
- [Next.js + Supabase Guide](https://supabase.com/docs/guides/getting-started/quickstarts/nextjs)
- [Backend Supabase Setup](../backend/README.md)

