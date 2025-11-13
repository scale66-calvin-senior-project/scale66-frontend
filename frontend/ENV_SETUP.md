# Environment Variables Setup

## Required Environment Variables

For the waitlist service to work in production, you need to set these environment variables:

### 1. GitHub Secrets (for build)
Add these secrets in your GitHub repository settings (Settings → Secrets and variables → Actions):

- `RESEND_API_KEY` - Your Resend API key (starts with `re_`)
- `RESEND_AUDIENCE_ID` - Your Resend audience ID (UUID format, optional)

### 2. Firebase Console (for runtime)
Since Firebase App Hosting runs Next.js in standalone mode, you also need to set these in Firebase Console:

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `scale66-app`
3. Go to **Hosting** → **Frameworks** → Your site
4. Click on **Environment variables** or **Configuration**
5. Add:
   - `RESEND_API_KEY` = `re_your_api_key_here`
   - `RESEND_AUDIENCE_ID` = `your_audience_id_here` (optional)

### 3. Local Development
Create a `.env.local` file in the `frontend` directory:

```
RESEND_API_KEY=re_your_api_key_here
RESEND_AUDIENCE_ID=your_audience_id_here
```

**Note:** Restart your dev server after adding/changing environment variables.

## Getting Your Resend Credentials

1. **API Key:**
   - Go to [Resend Dashboard](https://resend.com/api-keys)
   - Create or copy your API key (starts with `re_`)

2. **Audience ID (optional):**
   - Go to [Resend Audiences](https://resend.com/audiences)
   - Create or select your waitlist audience
   - Copy the Audience ID (UUID format)

