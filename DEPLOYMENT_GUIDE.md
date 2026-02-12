# 🚀 VegGo Deployment Guide

## Local Development Setup

### Step 1: Install Python Dependencies
```bash
cd veggo-platform
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure Environment
1. Copy `.env.example` to `.env`
2. Update all values with your credentials:
   - MongoDB URI
   - SMTP settings
   - Google Maps API key
   - Secret key (generate a secure random string)

### Step 3: Initialize Database
```bash
python init_db.py
```

This creates:
- Default admin account (admin@veggo.com / admin123)
- Database indexes
- Sample products
- Default delivery settings

### Step 4: Run Locally
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/docs for API documentation

---

## Vercel Deployment

### Prerequisites
- Vercel account (https://vercel.com)
- Vercel CLI installed: `npm install -g vercel`

### Step 1: Login to Vercel
```bash
vercel login
```

### Step 2: Configure Environment Variables

Go to your Vercel project → Settings → Environment Variables

Add these variables:

```
MONGODB_URI=mongodb+srv://...
DATABASE_NAME=veggo_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@veggo.com
FROM_NAME=VegGo Platform
GOOGLE_MAPS_API_KEY=your-google-maps-key
BASE_DELIVERY_FEE=50
PRICE_PER_KM=10
PRICE_PER_METER=0.01
FRONTEND_URL=https://your-frontend.vercel.app
ORDER_CANCEL_TIME_MINUTES=5
```

### Step 3: Deploy
```bash
cd veggo-platform
vercel --prod
```

### Step 4: Initialize Production Database

After deployment, run init script locally but connected to production:

```bash
# Update .env to use production MongoDB URI
python init_db.py
```

---

## MongoDB Atlas Setup

### Step 1: Create Account
Go to https://www.mongodb.com/cloud/atlas

### Step 2: Create Cluster
1. Choose Free tier (M0)
2. Select region closest to your users
3. Name your cluster

### Step 3: Create Database User
1. Go to Database Access
2. Add new database user
3. Choose password authentication
4. Save username and password

### Step 4: Configure Network Access
1. Go to Network Access
2. Add IP Address: 0.0.0.0/0 (Allow from anywhere)
   - For production, restrict to specific IPs

### Step 5: Get Connection String
1. Click "Connect" on your cluster
2. Choose "Connect your application"
3. Copy the connection string
4. Replace `<password>` with your database user password

---

## Gmail SMTP Setup

### Step 1: Enable 2-Factor Authentication
1. Go to Google Account settings
2. Security → 2-Step Verification
3. Enable it

### Step 2: Generate App Password
1. Go to Security → App passwords
2. Select app: Mail
3. Select device: Other (Custom name)
4. Generate password
5. Copy the 16-character password

### Step 3: Configure .env
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=<16-character-app-password>
```

---

## Google Maps API Setup

### Step 1: Create Project
1. Go to https://console.cloud.google.com/
2. Create new project

### Step 2: Enable APIs
1. Go to APIs & Services → Library
2. Enable these APIs:
   - Distance Matrix API
   - Geocoding API
   - Maps JavaScript API (for frontend)

### Step 3: Create API Key
1. Go to APIs & Services → Credentials
2. Create credentials → API key
3. Copy the API key

### Step 4: Restrict API Key (Recommended)
1. Edit API key
2. API restrictions → Restrict key
3. Select the APIs you enabled
4. Application restrictions → Set domain/IP restrictions

---

## Testing the Deployment

### Test API Endpoints

1. **Health Check**
```bash
curl https://your-api.vercel.app/health
```

2. **Admin Login**
```bash
curl -X POST https://your-api.vercel.app/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@veggo.com","password":"admin123"}'
```

3. **Get Products**
```bash
curl https://your-api.vercel.app/api/products
```

---

## Security Checklist

- [ ] Change default admin password
- [ ] Use strong SECRET_KEY
- [ ] Enable MongoDB authentication
- [ ] Restrict MongoDB network access
- [ ] Use environment variables (never hardcode)
- [ ] Enable HTTPS (Vercel does this automatically)
- [ ] Restrict Google Maps API key
- [ ] Use app-specific passwords for Gmail
- [ ] Set proper CORS origins for production
- [ ] Regular backup of MongoDB database

---

## Monitoring & Maintenance

### Monitor Logs
```bash
vercel logs <your-deployment-url>
```

### Update Deployment
```bash
# Make changes
git add .
git commit -m "Update"
vercel --prod
```

### Database Backup
Use MongoDB Atlas:
1. Go to Clusters
2. Click "..." → Take snapshot
3. Schedule automated backups

---

## Troubleshooting

### Issue: "Module not found"
**Solution:** Ensure all dependencies are in requirements.txt

### Issue: "Database connection failed"
**Solution:** Check MongoDB URI and network access settings

### Issue: "Email not sending"
**Solution:** Verify SMTP credentials and app password

### Issue: "Google Maps error"
**Solution:** Check API key and ensure APIs are enabled

### Issue: "CORS error"
**Solution:** Update CORS settings in main.py for production origins

---

## Scaling Tips

1. **Database Indexing**: Already done in init_db.py
2. **Caching**: Add Redis for session/data caching
3. **CDN**: Use Vercel CDN for static assets
4. **Rate Limiting**: Implement API rate limiting
5. **Load Balancing**: Vercel handles this automatically

---

## Cost Estimation

**Free Tier:**
- Vercel: Free for hobby projects
- MongoDB Atlas: 512 MB free (M0)
- Google Maps: $200 free credit/month

**Paid (Small Scale):**
- Vercel: $20/month (Pro)
- MongoDB: $9/month (M2 Shared)
- Google Maps: Pay as you go after free credits

---

## Support & Updates

- API Docs: https://your-api.vercel.app/docs
- GitHub Issues: Report bugs
- Email: support@veggo.com

---

**Happy Deploying! 🚀**
