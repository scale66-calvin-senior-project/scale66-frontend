# Supabase Migrations

This directory contains SQL migration files for your Supabase database.

## Creating Migrations

Use the Supabase CLI to create new migrations:

```bash
# Create a new migration
supabase migration new migration_name

# Example: Create initial schema
supabase migration new create_initial_schema
```

## Running Migrations

### Local Development

```bash
# Start Supabase locally
supabase start

# Apply migrations
supabase db reset
```

### Production

Migrations are automatically applied when you push to production:

```bash
supabase db push
```

## Migration Files

Create migration files in this directory with the naming convention:
`YYYYMMDDHHMMSS_migration_name.sql`

Example: `20240115120000_create_initial_schema.sql`

## Initial Schema

Your database schema (from the prompt) includes:

- **users** - User accounts (extends auth.users)
- **brand_kits** - Brand information
- **campaigns** - Campaign management
- **posts** - Generated carousel posts
- **post_variations** - Post variations/alternatives
- **chat_history** - User chat/prompt history
- **social_media_accounts** - Connected social accounts
- **payment_transactions** - Payment records
- **sessions** - User sessions (if not using Supabase Auth)

## Row Level Security (RLS)

All tables should have RLS enabled with appropriate policies to ensure users can only access their own data.

Example RLS policy:

```sql
-- Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only read their own posts
CREATE POLICY "Users can read own posts"
  ON posts FOR SELECT
  USING (auth.uid() = user_id);

-- Policy: Users can insert their own posts
CREATE POLICY "Users can create posts"
  ON posts FOR INSERT
  WITH CHECK (auth.uid() = user_id);
```

## Example Migration File

See `20240115000000_create_initial_schema.sql` for a complete example of the initial database schema.

