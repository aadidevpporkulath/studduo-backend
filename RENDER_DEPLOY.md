# Render Deployment Guide

## Quick Setup

### 1. Create a Web Service on Render
- Connect your GitHub repository
- **Build Command**: `bash render-build.sh`
- **Start Command**: `bash render-start.sh`
- **Environment**: `Python 3`

### 2. Environment Variables
Set these in Render Dashboard → Environment:

#### Required
- `GOOGLE_API_KEY` - Your Google Gemini API key
- `FIREBASE_PROJECT_ID` - Your Firebase project ID
- `FIREBASE_CREDENTIALS_PATH` - `/etc/secrets/firebase-credentials.json`

#### Optional (with defaults)
- `APP_ENV` - `production` (default: `development`)
- `API_PORT` - Port number (Render sets `$PORT` automatically)
- `ALLOWED_ORIGINS` - CORS origins (default: `http://localhost:3000,http://localhost:5173`)
- `TESSERACT_CMD` - `/usr/bin/tesseract` (set by render-start.sh)
- `CHROMA_PERSIST_DIR` - `./chroma_db` (default)
- `KNOWLEDGE_DIR` - `./knowledge` (default)
- `MODEL_NAME` - `gemini-pro` (default)
- `TEMPERATURE` - `0.7` (default)
- `MAX_TOKENS` - `8192` (default)

### 3. Secret Files
Upload `firebase-credentials.json`:
- Go to Render Dashboard → Environment → Secret Files
- **File Name**: `firebase-credentials.json`
- **Mount Path**: `/etc/secrets/firebase-credentials.json`
- **Content**: Paste your Firebase credentials JSON

### 4. Persistent Disk (Recommended for ChromaDB)
If you want to persist the vector store between deploys:
- Create a Render Disk
- Mount it to `/var/data/chroma_db`
- Set `CHROMA_PERSIST_DIR=/var/data/chroma_db`

**Note**: Without a disk, ChromaDB will reinitialize on each deploy (ephemeral storage).

### 5. Deploy
- Commit and push changes
- Render will automatically build and deploy

## Health Check
- Endpoint: `https://your-app.onrender.com/api/health`
- Should return: `{"status": "healthy", "service": "studduo-api"}`

## Troubleshooting

### Build Fails
- Check build logs for missing dependencies
- Verify `render-build.sh` has correct permissions

### App Won't Start
- Check environment variables are set correctly
- Verify Firebase credentials are mounted properly
- Check app logs for errors

### OCR/PDF Issues
- Tesseract is installed via `render-build.sh`
- Path is set to `/usr/bin/tesseract` automatically

### Vector Store Empty
- If using ephemeral storage, run document ingestion after each deploy
- Consider using a Render Disk for persistence
- Or run ingestion as a one-time job

## Production Checklist
- [ ] All environment variables configured
- [ ] Firebase credentials uploaded as Secret File
- [ ] CORS origins updated to production URLs
- [ ] Consider adding a Render Disk for ChromaDB
- [ ] Set `APP_ENV=production`
- [ ] Monitor logs after first deploy
