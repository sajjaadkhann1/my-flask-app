# Vercel Deployment Guide

## 🚀 Deploy to Vercel (Recommended)

Vercel is the **easiest way** to deploy your Flask app with a free tier, custom domains, and automatic deployments.

### ✅ Prerequisites
- GitHub account
- Vercel account (free at https://vercel.com)
- Your repo pushed to GitHub

---

## 📋 Step-by-Step Deployment

### Step 1: Push Code to GitHub
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### Step 2: Sign Up on Vercel
1. Go to https://vercel.com
2. Click **"Sign Up"**
3. Select **"Continue with GitHub"**
4. Authorize Vercel to access your GitHub

### Step 3: Import Project
1. Click **"New Project"**
2. Find and select **`my-flask-app`** repo
3. Click **"Import"**

### Step 4: Configure Project
- **Framework Preset**: Other
- **Root Directory**: `./` (default)
- **Build Command**: Leave empty (not needed)
- **Output Directory**: Leave empty
- **Install Command**: `pip install -r requirements.txt`

### Step 5: Add Environment Variables (Optional)
If using `.env` file:
1. Go to **Settings** → **Environment Variables**
2. Add any variables you need
3. Click **"Save"**

### Step 6: Deploy
Click **"Deploy"** button

🎉 **Your app is now live!** Visit the URL provided (e.g., `https://my-flask-app-xyz.vercel.app`)

---

## 🔄 Auto-Deploy on Push

Once connected to Vercel:
- Every push to `main` automatically deploys
- Commits to PRs create preview deployments
- Rollback to previous versions anytime

---

## 🌐 Custom Domain

### Add Your Domain
1. Go to **Settings** → **Domains**
2. Enter your domain (e.g., `mlapp.com`)
3. Follow DNS setup instructions
4. Vercel provides free SSL certificate

---

## 📁 Project Structure for Vercel

```
my-flask-app/
├── app.py                 # Flask app (Vercel entry point)
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
├── Procfile              # Process file
├── .gitignore            # Git ignore rules
├── static/
│   ├── uploads/          # User uploaded files
│   └── plots/            # Generated plots
└── templates/
    └── index.html        # Frontend HTML
```

---

## ⚙️ Environment Variables on Vercel

### Set Environment Variables
1. **Dashboard** → Your project
2. **Settings** → **Environment Variables**
3. Add variables:

```
FLASK_ENV=production
DEBUG=False
```

### Access in Code
```python
import os
debug_mode = os.getenv('DEBUG', 'False') == 'True'
```

---

## 🔍 Monitor & Logs

### View Logs
1. Go to **Deployments** tab
2. Click on deployment
3. View real-time logs

### View Function Logs
```bash
vercel logs my-flask-app
```

---

## 🆘 Troubleshooting

### Error: "Build failed"
- Check `requirements.txt` is updated: `pip freeze > requirements.txt`
- Push changes and redeploy

### Error: "Module not found"
```bash
pip install -r requirements.txt
pip freeze > requirements.txt
git push origin main
```

### App returning 404
- Ensure `vercel.json` is configured correctly
- Check all routes use relative paths

### File Upload Issues
- Vercel uses **ephemeral filesystem** (files deleted after deployment)
- Use external storage for uploads:
  - AWS S3
  - Cloudinary
  - Firebase Storage

---

## 💾 Handle File Uploads (Production)

For production, use cloud storage instead of local files.

### Option 1: Cloudinary (Easiest)
```bash
pip install cloudinary
```

```python
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name = "YOUR_CLOUD_NAME",
    api_key = "YOUR_API_KEY",
    api_secret = "YOUR_API_SECRET"
)

# Upload file
result = cloudinary.uploader.upload(file_path)
```

### Option 2: AWS S3
```bash
pip install boto3
```

### Option 3: Vercel Blob Storage
```bash
pip install vercel-blob
```

---

## 🚀 CLI Deployment (Alternative)

### Install Vercel CLI
```bash
npm install -g vercel
```

### Deploy
```bash
vercel login
vercel
```

### Deploy Specific Branch
```bash
vercel --prod
```

---

## 📊 Vercel Pricing

| Plan | Cost | Features |
|------|------|----------|
| Free | $0 | 1 project, auto-scaling, preview deployments |
| Pro | $20/mo | Unlimited projects, priority support |
| Enterprise | Custom | Advanced features |

✅ **Free tier includes everything you need!**

---

## ✨ Best Practices

1. **Use Environment Variables** for sensitive data (API keys, secrets)
2. **Keep dependencies minimal** for faster builds
3. **Test locally first** before pushing
4. **Use Git branches** for feature development
5. **Monitor performance** with Vercel Analytics

---

## 🎯 Your Live App

After deployment, access it at:
```
https://your-app-name.vercel.app
```

Share the link with anyone! ✨

---

## 📞 Support

- **Vercel Docs**: https://vercel.com/docs
- **Python Support**: https://vercel.com/docs/functions/serverless-functions/python
- **Common Issues**: https://vercel.com/docs/errors

---

**That's it! Your Flask ML app is now live on Vercel!** 🚀
