# Cloud Deployment Guide for Streamlit

## Step 1: Configure Database Secrets in Streamlit Cloud

1. Go to your app's dashboard on [share.streamlit.io](https://share.streamlit.io)
2. Click on your deployed app
3. Click the **⚙️ Settings** button
4. Select **Secrets** from the sidebar
5. Add the following configuration (replace with your actual database credentials):

```toml
[mysql]
host = "your-database-host.com"
user = "your-username"
password = "your-password"
database = "APP"
```

## Step 2: Database Options

### Option 1: Free MySQL Hosting (Recommended for Testing)
- **Aiven** - Free MySQL (limited storage)
- **PlanetScale** - Free tier with generous limits
- **Railway** - Free starter plan

### Option 2: Cloud Provider MySQL
- **AWS RDS** - Pay-as-you-go
- **Google Cloud SQL** - Pay-as-you-go
- **Azure Database for MySQL** - Pay-as-you-go

### Option 3: Use Your Local Database (Advanced)
- Expose your local MySQL via ngrok or similar tunneling service
- **Not recommended for production**

## Step 3: Deploy

1. Commit and push your changes:
```bash
git add .
git commit -m "Add cloud deployment configuration"
git push
```

2. Streamlit Cloud will automatically redeploy with the new configuration

## Local Development

For local development, edit `.streamlit/secrets.toml` with your local database credentials:

```toml
[mysql]
host = "localhost"
user = "warlord"
password = "Warlord@200206"
database = "APP"
```

**Important:** Never commit `.streamlit/secrets.toml` to git (it's already in .gitignore)
