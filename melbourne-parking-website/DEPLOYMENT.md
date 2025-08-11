# Melbourne Parking System - Full Stack Deployment Guide

## Architecture Overview
- **Frontend**: Vue.js deployed on Vercel
- **Backend**: Flask API deployed on Railway
- **Database**: PostgreSQL on Railway

## Prerequisites
- Node.js 16+ installed
- Python 3.8+ installed
- Git repository connected to GitHub
- Vercel account
- Railway account

## Backend Deployment (Railway)

### Step 1: Prepare Backend for Railway
1. Ensure all backend files are in the `backend/` directory
2. The `requirements.txt` file should include all necessary dependencies
3. The `railway.toml` configuration file is already set up

### Step 2: Deploy to Railway
1. Go to [Railway](https://railway.app)
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Select your repository: `Zhmzjy/5120`
5. Railway will detect the project structure

### Step 3: Configure Environment Variables in Railway
Add these environment variables in Railway dashboard:
```
DATABASE_URL=postgresql://... (Railway will provide this automatically)
FLASK_ENV=production
PORT=8000
PYTHONPATH=/app/backend
```

### Step 4: Set Railway Build Settings
- **Build Command**: `cd backend && pip install -r requirements.txt`
- **Start Command**: `cd backend && python run.py`
- **Root Directory**: Leave empty (Railway will use the root)

## Frontend Deployment (Vercel)

### Step 1: Update API Configuration
1. After Railway deployment completes, copy your Railway app URL
2. Update the frontend API configuration:

Edit `/frontend/src/config/api.js`:
```javascript
const config = {
  development: {
    API_BASE_URL: 'http://localhost:5002'
  },
  production: {
    API_BASE_URL: 'https://YOUR-RAILWAY-APP-NAME.railway.app'  // Replace with actual URL
  }
}
```

### Step 2: Deploy to Vercel
1. Go to [Vercel](https://vercel.com)
2. Click "Add New..." → "Project"
3. Import your GitHub repository: `Zhmzjy/5120`
4. Configure the project:
   - **Framework Preset**: Vue.js
   - **Root Directory**: `melbourne-parking-website/frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Step 3: Set Vercel Environment Variables
Add this environment variable in Vercel project settings:
```
VUE_APP_API_URL=https://YOUR-RAILWAY-APP-NAME.railway.app
```

## Database Setup

### Option 1: Railway PostgreSQL (Recommended)
1. In Railway dashboard, click "Add Service" → "Database" → "PostgreSQL"
2. Railway will automatically provide the DATABASE_URL
3. No additional configuration needed

### Option 2: External Database
If using external PostgreSQL, update the DATABASE_URL environment variable in Railway.

## CORS Configuration
The backend is already configured to handle CORS for production:
- Allows requests from `*.vercel.app` domains
- Development mode allows all origins

## Testing the Deployment

### 1. Test Backend API
Visit your Railway URL + `/api/parking/status` to check if the API is working:
```
https://your-railway-app.railway.app/api/parking/status
```

### 2. Test Frontend
Visit your Vercel deployment URL to check if the frontend loads correctly.

### 3. Test API Connection
Check browser console for any CORS or connection errors between frontend and backend.

## Troubleshooting

### Common Issues:

1. **CORS Errors**
   - Ensure the Railway URL is correctly set in frontend config
   - Check that CORS is properly configured in backend

2. **Database Connection Issues**
   - Verify DATABASE_URL environment variable in Railway
   - Check if database service is running

3. **Build Failures**
   - Check that all dependencies are listed in requirements.txt
   - Ensure Python version compatibility

4. **API Connection Failures**
   - Verify the Railway app URL is correct
   - Check network requests in browser dev tools

### Logs and Debugging:
- **Railway**: View logs in Railway dashboard under "Deployments"
- **Vercel**: Check function logs in Vercel dashboard
- **Browser**: Use developer tools to check network requests

## Post-Deployment Updates

### Backend Updates:
1. Push changes to GitHub
2. Railway will automatically redeploy

### Frontend Updates:
1. Push changes to GitHub
2. Vercel will automatically redeploy

### Environment Variables Updates:
- Railway: Update in Railway dashboard
- Vercel: Update in Vercel project settings

## URLs After Deployment
- **Frontend**: `https://melbourne-parking-frontend.vercel.app` (or your custom domain)
- **Backend API**: `https://your-railway-app.railway.app`
- **API Documentation**: `https://your-railway-app.railway.app/api/parking/status`

## Security Notes
- Never commit sensitive environment variables to Git
- Use Railway and Vercel environment variable management
- CORS is configured for production domains only
