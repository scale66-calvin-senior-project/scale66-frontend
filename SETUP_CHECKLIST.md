# Quick Setup Checklist

## 🚀 Get Started in 3 Steps

### 1. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

**Backend** (`backend/.env`):
```env
RESEND_API_KEY=your_key_here
RESEND_AUDIENCE_ID=your_audience_id_here
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 3. Start Both Servers

**Terminal 1 - Backend:**
```bash
cd backend
./run_backend.sh
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## ✅ Test It

1. Go to http://localhost:3000/waitlist
2. Submit the form
3. Check that email arrives

## 📖 Full Documentation

See [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for complete details.

