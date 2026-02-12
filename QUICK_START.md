# 🥬 VegGo Platform - Quick Start Guide

## 📦 What You Got

A complete vegetable delivery platform with:
- ✅ User system with email verification
- ✅ Separate agent signup and approval system
- ✅ Admin panel with full management
- ✅ Google Maps integration for delivery fees
- ✅ Email notifications for everything
- ✅ Real-time order tracking
- ✅ 5-minute order cancellation
- ✅ Past delivery history
- ✅ Admin can edit delivery fees (base, per km, per meter)
- ✅ Product stock management (in/out of stock)
- ✅ Ready for mobile app + website
- ✅ Deployable to Vercel

## 🚀 Quick Setup (5 Minutes)

### 1. Extract Files
```bash
tar -xzf veggo-platform.tar.gz
cd veggo-platform
```

### 2. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment
Create `.env` file (copy from `.env.example`):
```env
MONGODB_URI=your-mongodb-uri
GOOGLE_MAPS_API_KEY=your-google-maps-key
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SECRET_KEY=change-this-to-random-string
```

### 4. Initialize Database
```bash
python init_db.py
```

### 5. Run
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Test
- API Docs: http://localhost:8000/docs
- Login as admin: admin@veggo.com / admin123

## 📚 Important Files

- `README.md` - Complete documentation
- `API_DOCUMENTATION.md` - All API endpoints
- `DEPLOYMENT_GUIDE.md` - Vercel deployment steps
- `.env.example` - Environment template
- `init_db.py` - Database setup script

## 🔑 Default Credentials

**Admin:**
- Email: admin@veggo.com
- Password: admin123

⚠️ **CHANGE IMMEDIATELY AFTER FIRST LOGIN!**

## 📋 What Admin Can Do

1. ✅ Manage all users and agents
2. ✅ Approve/reject delivery agents
3. ✅ Add/edit/delete products
4. ✅ Set products in-stock or out-of-stock
5. ✅ Manage all orders
6. ✅ Assign agents to orders
7. ✅ **Edit delivery fees:**
   - Base delivery fee
   - Price per kilometer
   - Price per meter

## 🔧 Key Features

### For Users:
- Signup with email verification
- Browse products (with stock status)
- Place orders (automatic delivery fee)
- Track orders in real-time
- See agent location on map
- View past deliveries
- Cancel orders within 5 minutes
- Email notifications for everything

### For Agents:
- Separate signup area
- Wait for admin approval
- View assigned orders
- Update location in real-time
- Update order status
- Email notification on approval

### For Admin:
- Full control dashboard
- User management
- Agent approval system
- Product management (with stock control)
- Order management
- Delivery fee settings
- Real-time statistics

## 📧 Email Notifications

Users get emails for:
- Signup verification
- Order confirmation
- Agent assignment
- Status updates (picked up, in transit, delivered)
- Order cancellation

Agents get emails for:
- Account approval/rejection

## 🗺️ Delivery Fee Formula

```
Delivery Fee = Base Fee + (Distance × Price per KM)
```

Example:
- Base Fee: ₹50
- Price per KM: ₹10
- Distance: 3 km
- **Total Delivery Fee: ₹80**

Admin can change all these values!

## 🔐 Security Features

- ✅ Password hashing (bcrypt)
- ✅ JWT authentication
- ✅ Email verification
- ✅ Agent approval required
- ✅ Time-limited order cancellation
- ✅ Secure password reset

## 📱 Mobile App Integration

The API is ready to connect with:
- React Native apps
- Flutter apps
- Native iOS/Android apps
- Any frontend framework

Just use the API endpoints with Bearer token authentication.

## 🌐 Website Integration

Same as mobile - use REST API:
1. User logs in → Gets JWT token
2. Include token in Authorization header
3. Make API calls
4. Display data

## 🚀 Deploy to Production

Full guide in `DEPLOYMENT_GUIDE.md`, but quick steps:

```bash
vercel login
vercel --prod
```

Set environment variables in Vercel dashboard.

## 📊 Project Structure

```
veggo-platform/
├── main.py              # FastAPI app
├── init_db.py          # Database setup
├── requirements.txt    # Dependencies
├── .env.example        # Environment template
├── app/
│   ├── config.py       # Settings
│   ├── database.py     # MongoDB connection
│   ├── models.py       # Data models
│   ├── auth.py         # Authentication
│   ├── email_service.py # Email handling
│   ├── maps_service.py  # Google Maps
│   └── routes/         # API endpoints
│       ├── user_routes.py
│       ├── agent_routes.py
│       ├── admin_routes.py
│       ├── product_routes.py
│       └── order_routes.py
└── docs/
    ├── README.md
    ├── API_DOCUMENTATION.md
    └── DEPLOYMENT_GUIDE.md
```

## 🆘 Need Help?

1. Check `README.md` for detailed docs
2. Check `API_DOCUMENTATION.md` for API reference
3. Check `DEPLOYMENT_GUIDE.md` for deployment
4. Test endpoints at: http://localhost:8000/docs

## ✅ Testing Checklist

- [ ] Admin login works
- [ ] Can add products
- [ ] User signup and verification
- [ ] Order creation calculates delivery fee
- [ ] Email notifications send
- [ ] Agent approval flow
- [ ] Order cancellation within 5 minutes
- [ ] Admin can edit delivery fee settings

## 🎯 Next Steps

1. Change admin password
2. Configure SMTP (Gmail)
3. Get Google Maps API key
4. Set up MongoDB Atlas
5. Add real product images
6. Deploy to Vercel
7. Connect with frontend
8. Test thoroughly
9. Launch! 🚀

---

**Built with ❤️ for VegGo Platform**

Questions? Check the documentation files!
