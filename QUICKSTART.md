# Quick Setup Guide for Cloud Deployment

## Step 1: Update Local Secrets (✓ Done)
You've already configured `.streamlit/secrets.toml` with your FreeSQLDatabase credentials.

## Step 2: Initialize Remote Database
Run this command to create tables and seed data on your remote database:

```bash
python init_remote_db.py
```

This will:
- Create all tables (users, students, courses, modules, etc.)
- Create triggers for RBAC
- Seed initial data (10 rows per table)

## Step 3: Configure Streamlit Cloud Secrets

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Find your deployed app
3. Click **⚙️ Settings** → **Secrets**
4. Paste this exactly:

```toml
[mysql]
host = "sql8.freesqldatabase.com"
user = "sql8810071"
password = "QTS5mGlaDF"
database = "sql8810071"
port = 3306
```

5. Click **Save**

## Step 4: Deploy
Your app will automatically redeploy with the new database connection!

## Testing Locally
After running `init_remote_db.py`, you can test locally:

```bash
streamlit run app.py
```

The app will now connect to your remote database instead of localhost.

## Login Credentials (After Seeding)
- **Student**: `STU001` / `pass123`
- **Module Staff**: `MS001` / `pass123`
- **Welfare Staff**: `WS001` / `pass123`
- **Admin**: `ADMIN01` / `admin123`
