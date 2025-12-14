# Supabase Setup Guide

## Step 1: Get Your Supabase Credentials

1. Go to [https://supabase.com](https://supabase.com) and sign in
2. Select your project (or create a new one)
3. Go to **Settings** → **API**
4. Copy these values:
   - **Project URL**: Found under "Project URL" (e.g., `https://xxxxx.supabase.co`)
   - **Service Role Key**: Found under "Project API keys" → `service_role` → `secret` key
     - ⚠️ **Keep this secret!** This key has full database access

## Step 2: Create Your Tables

1. In Supabase Dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy and paste the contents of `supabase_schema.sql`
4. Click **Run** to create the tables

## Step 3: Set Up Environment Variables

1. Copy `env_example.txt` to `.env` in the `backend` directory:
   ```bash
   cd backend
   copy env_example.txt .env
   ```

2. Edit `.env` and fill in your actual values:
   ```
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
   ```

3. **Important**: Make sure `.env` is in `.gitignore` (it should be already)

## Step 4: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 5: Run the Seed Script

```bash
python seed_supabase.py
```

This will insert the mock data (definitions and factors) into your Supabase database.

## Troubleshooting

- **"Missing Supabase credentials"**: Make sure your `.env` file exists and has the correct variable names
- **"Permission denied"**: Make sure you're using the `service_role` key, not the `anon` key
- **"Table does not exist"**: Run the SQL schema first to create the tables
- **"Connection error"**: Check that your Project URL is correct and includes `https://`

## Security Notes

- Never commit your `.env` file to git
- The `service_role` key has full database access - keep it secret
- For production, consider using environment variables from your hosting platform instead of `.env` files




