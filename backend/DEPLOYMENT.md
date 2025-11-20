# Deployment Guide

## Railway Backend Deployment

### Prerequisites
- Railway account ([railway.app](https://railway.app))
- GitHub repository connected to Railway

### Step 1: Create PostgreSQL Database on Railway

1. Go to Railway dashboard
2. Click "New Project"
3. Select "Provision PostgreSQL"
4. Wait for database to be provisioned
5. Copy the connection string from the "Connect" tab (format: `postgresql://...`)

### Step 2: Deploy Backend Service

1. In the same Railway project, click "New Service"
2. Select "GitHub Repo"
3. Choose your repository
4. **IMPORTANT**: Set root directory to `/backend`
   - Go to "Settings" → "Service Settings" → "Root Directory"
   - Set to: `backend`

### Step 3: Configure Environment Variables

In Railway backend service settings, add these environment variables:

```bash
# Database (Railway will provide this automatically if you link the PostgreSQL service)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Security - GENERATE A NEW SECRET KEY!
SECRET_KEY=your-super-secret-key-here-change-this

# CORS - Update with your Vercel frontend URL
ALLOWED_ORIGINS=http://localhost:5174,https://your-app.vercel.app

# Optional
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**To generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 4: Link Database to Backend

1. In Railway backend service, go to "Settings" → "Service Variables"
2. Click "Add Variable Reference"
3. Select your PostgreSQL service
4. Choose `DATABASE_URL`
5. This automatically sets the correct connection string

### Step 5: Deploy

1. Railway will automatically detect the `Dockerfile` and build
2. Initial deployment takes 2-5 minutes
3. Check logs for any errors
4. Once deployed, Railway provides a public URL (e.g., `https://your-app.up.railway.app`)

### Step 6: Initialize Database

Railway PostgreSQL comes empty. You need to run your database migrations/initialization:

**Option A: Using Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run database initialization (if you have a script)
railway run python init_db.py
```

**Option B: Connect remotely and run migrations**
```bash
# Use the DATABASE_URL from Railway
psql "postgresql://user:password@host:port/dbname"

# Then run your SQL schema/migrations
```

### Health Check

After deployment, verify:
- `https://your-app.up.railway.app/health` → Should return `{"status": "healthy"}`
- `https://your-app.up.railway.app/docs` → FastAPI Swagger documentation

---

## Vercel Frontend Deployment

### Step 1: Prepare Frontend

Update [frontend/src/services/api.js](frontend/src/services/api.js) with Railway backend URL:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://your-app.up.railway.app'
```

### Step 2: Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository
4. **Configure build settings:**
   - Framework Preset: `Vite`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

### Step 3: Set Environment Variables

In Vercel project settings → Environment Variables:

```bash
VITE_API_URL=https://your-app.up.railway.app
```

### Step 4: Deploy

1. Click "Deploy"
2. Wait for build to complete (~2-3 minutes)
3. Vercel provides a production URL (e.g., `https://your-app.vercel.app`)

### Step 5: Update CORS

Go back to Railway backend environment variables and update:

```bash
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:5174
```

Redeploy backend service for changes to take effect.

---

## Performance Notes

### Why Railway?

With Railway PostgreSQL, your backend and database are in the **same datacenter**:
- **Query latency**: ~2-5ms (vs. 100-450ms to Raspberry Pi)
- **Expected speedup**: 20-50x faster database operations
- **Dashboard load time**: <500ms (vs. 5+ seconds)

### Optimization Applied

The backend includes these performance improvements:
- ✅ User caching (10-minute TTL)
- ✅ Optimized N+1 queries in categories endpoint
- ✅ Connection pooling (pool_size=5, max_overflow=10)
- ✅ Query performance monitoring

---

## Monitoring

### Railway Logs

View real-time logs in Railway dashboard:
- Click on backend service
- Go to "Deployments" → "View Logs"
- Look for performance metrics:
  - `⏱️ START:` - Request initiated
  - `✅ DONE:` - Request completed (with timing)
  - `🐌 SLOW QUERY:` - Database queries >100ms

### Health Monitoring

Railway provides:
- Automatic health checks
- Auto-restart on failure
- Metrics dashboard (CPU, Memory, Network)

---

## Troubleshooting

### Database Connection Issues

If you see "could not connect to database":
1. Check `DATABASE_URL` is set correctly
2. Verify PostgreSQL service is running
3. Ensure services are in the same Railway project
4. Check Railway dashboard for service status

### CORS Errors

If frontend can't connect to backend:
1. Verify `ALLOWED_ORIGINS` includes your Vercel URL
2. Check Railway backend is deployed and running
3. Test backend directly: `curl https://your-app.up.railway.app/health`

### Build Failures

If Docker build fails:
1. Check Railway logs for error details
2. Verify all files are committed to Git
3. Test Dockerfile locally: `docker build -t fintracker .`

---

## Local Testing with Docker

Test the Docker setup locally before deploying:

```bash
# Build image
cd backend
docker build -t fintracker-backend .

# Run container (use your local .env)
docker run -p 8000:8000 --env-file .env fintracker-backend

# Test
curl http://localhost:8000/health
```

---

## Cost Estimate

**Railway** (with PostgreSQL):
- Starter plan: $5/month for 500 hours
- Or usage-based: ~$0.01/hour
- PostgreSQL: Included in Starter plan

**Vercel**:
- Hobby plan: Free
- Pro plan: $20/month (if needed for team/custom domains)

**Total**: ~$5-25/month depending on usage

---

## Next Steps

1. ✅ Create Railway account
2. ✅ Provision PostgreSQL database
3. ✅ Deploy backend with proper environment variables
4. ✅ Initialize database schema
5. ✅ Test backend API endpoints
6. ✅ Update frontend API URL
7. ✅ Deploy frontend to Vercel
8. ✅ Update CORS settings
9. ✅ Test full application flow
10. ✅ Monitor performance improvements

---

## Support

- Railway docs: https://docs.railway.app
- Vercel docs: https://vercel.com/docs
- FastAPI deployment: https://fastapi.tiangolo.com/deployment/
