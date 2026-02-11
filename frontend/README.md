# Mobile Progress Dashboard

## Quick Access

View progress on your phone:

### Option 1: Local Network (Easiest)

1. **Find your computer's IP address:**

```bash
# On Linux/Mac:
hostname -I | awk '{print $1}'

# On Mac specifically:
ipconfig getifaddr en0

# On Windows:
ipconfig | findstr IPv4
```

2. **Start a simple web server:**

```bash
cd frontend
python3 -m http.server 8080
```

3. **Open on your phone:**

```
http://YOUR_COMPUTER_IP:8080/progress.html
```

For example: `http://192.168.1.100:8080/progress.html`

---

### Option 2: GitHub Pages (Public)

Deploy to GitHub Pages for access anywhere:

```bash
# From project root
git checkout -b gh-pages
git push origin gh-pages
```

Then visit: `https://remarkderfeoj.github.io/personal-caddie/frontend/progress.html`

---

### Option 3: Cloudflare Pages (Free, Fast)

1. Go to https://pages.cloudflare.com
2. Connect your GitHub repo
3. Set build output directory: `frontend`
4. Deploy

---

### Option 4: Ngrok (Public Tunnel)

Expose your local server to the internet:

```bash
# Install ngrok
brew install ngrok  # Mac
# or download from https://ngrok.com/download

# Run tunnel
cd frontend
python3 -m http.server 8080
# In another terminal:
ngrok http 8080
```

Use the ngrok URL on your phone (works from anywhere).

---

## Features

- ✅ Real-time API status
- ✅ Course/player/hole counts
- ✅ Feature checklist
- ✅ Recent commits
- ✅ Auto-refresh every 30s
- ✅ Mobile-optimized UI
- ✅ Works offline (cached commits)

---

## Customization

Edit `progress.html` to:
- Change API base URL (line 236)
- Add more metrics
- Customize colors/styling
- Add authentication

---

## Screenshots

The dashboard shows:
- 🟢 Live API status indicator
- 📊 Real-time course/player counts
- ✨ Feature badges (completed/in-progress)
- 📝 Recent commit history
- 🔄 Manual refresh button
- 🔗 Quick links to API docs

---

## Troubleshooting

**Can't connect to API:**
- Make sure Personal Caddie server is running (`uvicorn main:app --reload`)
- Check firewall allows incoming connections on port 8000
- Verify computer and phone are on same network

**Wrong IP address:**
- Computer may have multiple IPs (WiFi vs Ethernet)
- Try each IP address shown

**CORS errors:**
- Update `ALLOWED_ORIGINS` in backend `.env` file:
  ```
  ALLOWED_ORIGINS=http://192.168.1.100:8080,http://localhost:8080
  ```

---

## Production Deployment

For production, serve from the FastAPI backend:

```python
# In main.py
from fastapi.staticfiles import StaticFiles

app.mount("/dashboard", StaticFiles(directory="frontend"), name="dashboard")
```

Then visit: `http://your-server.com/dashboard/progress.html`
