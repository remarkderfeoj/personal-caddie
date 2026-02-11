# Personal Caddie - Deployment Guide

## Access the Web App

Once deployed, visit: `https://your-app.railway.app/app`

---

## Quick Deploy to Railway (Recommended)

Railway is the easiest option - same platform where your OpenClaw is running.

### 1. Create `railway.toml` (for Railway config)

Create this file in the root of the repo:

```toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r backend/requirements.txt"

[deploy]
startCommand = "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
restartPolicyType = "on-failure"
```

### 2. Deploy

**Option A: Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd /data/workspace/personal-caddie
railway init

# Deploy
railway up
```

**Option B: GitHub + Railway Dashboard**

1. Push your code to GitHub (already done!)
2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `remarkderfeoj/personal-caddie`
5. Railway will auto-detect and deploy

### 3. Access Your App

Railway will give you a URL like:
`https://personal-caddie-production-xyz.up.railway.app`

Visit: `https://your-url.railway.app/app` to use the mobile web app! 🎉

---

## Alternative: Render (Free Tier)

### 1. Create `render.yaml`

```yaml
services:
  - type: web
    name: personal-caddie
    env: python
    region: oregon
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
```

### 2. Deploy

1. Go to [render.com](https://render.com)
2. Connect your GitHub repo
3. Render auto-deploys on push

---

## Alternative: DigitalOcean App Platform

### 1. Create `.do/app.yaml`

```yaml
name: personal-caddie
services:
- name: api
  github:
    repo: remarkderfeoj/personal-caddie
    branch: main
  build_command: pip install -r backend/requirements.txt
  run_command: cd backend && uvicorn main:app --host 0.0.0.0 --port 8080
  http_port: 8080
  health_check:
    http_path: /health
```

### 2. Deploy

1. Go to DigitalOcean Apps
2. Create App from GitHub
3. Select repo

---

## Testing Locally First

Before deploying, test locally:

```bash
cd /data/workspace/personal-caddie/backend
python3 main.py
```

Then visit on your phone (same WiFi network):
`http://YOUR_MAC_IP:8000/app`

Find your Mac's IP:
```bash
ipconfig getifaddr en0  # WiFi
# or
ifconfig | grep "inet " | grep -v 127.0.0.1
```

---

## Environment Variables (Optional)

For production, you can set:

- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins (default: `*`)
- `PORT`: Server port (default: 8000, Railway auto-sets this)

---

## Database Setup (Future)

Currently using in-memory storage. To add PostgreSQL:

1. Add Postgres addon in Railway
2. Railway auto-sets `DATABASE_URL`
3. Run migration:
   ```bash
   python backend/db/migrate.py create
   python backend/db/migrate.py import
   ```

See `docs/POSTGRES_MIGRATION.md` for details.

---

## Troubleshooting

**App won't load:**
- Check Railway logs: `railway logs`
- Verify `/health` endpoint returns 200

**CORS errors:**
- Set `ALLOWED_ORIGINS=*` in Railway env vars

**No courses showing:**
- Courses auto-load from `backend/data/*.json`
- Check logs to confirm data loaded

---

## Next Steps

1. **Deploy to Railway** (5 minutes)
2. **Save the URL** and add to home screen on your phone
3. **Test with a real round** at Augusta, St Andrews, etc.
4. **Add your own courses** as you play them
5. **(Optional) Add player profiles** for personalized recommendations

---

Need help? Check the logs or ping me in Telegram!
