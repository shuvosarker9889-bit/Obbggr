# 🎬 CineFlix Bot - Production-Ready Telegram Content Distribution System

A professional, scalable Telegram bot for controlled video and link distribution with Mini App integration, force join mechanism, and duplicate prevention.

---

## ✨ Features

### 🎯 Core Functionality
- ✅ **Deep Link Integration** - Seamless Mini App to Bot flow
- ✅ **Video Distribution** - Forward-protected content delivery
- ✅ **Link Distribution** - External content with inline buttons
- ✅ **Duplicate Prevention** - Smart re-delivery handling
- ✅ **Force Join** - Multi-channel membership requirements
- ✅ **Auto Content Detection** - Automatic copy_id generation

### 🛡️ Security & Stability
- ✅ **Protected Content** - No forwarding for videos
- ✅ **Persistent Database** - MongoDB Atlas (survives redeploys)
- ✅ **Error Handling** - Robust flood wait & reconnection logic
- ✅ **Admin Only** - Secure admin panel access

### 🎨 User Experience
- ✅ **Bilingual** - Bengali + English messages
- ✅ **Professional UI** - Clean inline keyboards
- ✅ **Instant Delivery** - Fast content distribution
- ✅ **Smart Notifications** - Admin alerts for new content

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Google Sheets  │
│   (Mini App)    │
└────────┬────────┘
         │ Copy ID
         ▼
┌─────────────────┐
│   Deep Link     │
│ t.me/bot?start= │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌─────────────────┐
│  Telegram Bot   │◄────►│  MongoDB Atlas  │
│   (Pyrogram)    │      │  (Persistent)   │
└────────┬────────┘      └─────────────────┘
         │
         ▼
┌─────────────────┐
│  User receives  │
│   Video/Link    │
└─────────────────┘
```

---

## 📦 Tech Stack

- **Bot Framework:** Pyrogram 2.0
- **Database:** MongoDB Atlas (Free tier compatible)
- **Deployment:** Railway / Render (Free tier)
- **Language:** Python 3.11+
- **Async:** asyncio for performance

---

## 🚀 Quick Start

### 1. Prerequisites

- Telegram Bot Token (from @BotFather)
- Admin User ID (from @userinfobot)
- Content Channel (bot must be admin)
- Force Join Channel (bot must be admin)
- MongoDB Atlas account (free)
- Railway/Render account (free)

### 2. Clone & Configure

```bash
# Extract the project
cd telegram-bot-project

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 3. Deploy to Railway

#### Option A: GitHub (Recommended)

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_REPO_URL
git push -u origin main
```

Then:
1. Go to Railway.app
2. New Project → Deploy from GitHub
3. Select your repo
4. Add environment variables from `.env`
5. Deploy!

#### Option B: Railway CLI

```bash
railway login
railway init
railway up
```

### 4. Test Your Bot

```
/start - Welcome message
/admin - Admin panel (admin only)
/stats - Bot statistics
```

---

## 📝 Configuration

### Environment Variables

```env
# Bot
BOT_TOKEN=your_bot_token
API_ID=25115930
API_HASH=11f8f3d058991d44083d5c7c135964c5

# Admin
ADMIN_ID=your_telegram_id

# Channels
CONTENT_CHANNEL_ID=-100xxxxxxxxxx
FORCE_JOIN_CHANNEL_ID=-100xxxxxxxxxx
CHANNEL_USERNAME=@YourChannel

# Database
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DATABASE_NAME=cineflix_bot

# Features
ENABLE_NOTIFICATIONS=Yes
```

---

## 🎮 Usage

### For Admin

#### 1. Add Content

Simply forward videos or post links to your content channel. Bot will:
- Auto-detect the content
- Generate a unique `copy_id`
- Save to database
- Notify you with the `copy_id`

#### 2. Use Copy ID in Mini App

Add the `copy_id` to your Google Sheets or Mini App:

```
Content: Movie Name
Copy ID: abc12345
Deep Link: https://t.me/YourBot?start=content_abc12345
```

#### 3. Manage Channels

```bash
/addchannel -100xxxxxxxxxx  # Add force join channel
/removechannel -100xxxxxxxxxx  # Remove channel
/listchannels  # View all channels
```

### For Users

1. Open Mini App (from Google Sheets)
2. Click on content
3. Redirected to bot via deep link
4. Must join required channels
5. Receive content instantly

---

## 🔧 Admin Commands

### Main Commands
```
/start - Start the bot
/admin - Open admin panel
/stats - View statistics
/help - Show help
```

### Channel Management
```
/addchannel CHANNEL_ID - Add force join channel
/removechannel CHANNEL_ID - Remove channel
/listchannels - List all channels
```

### Testing
```
/testcontent - Test system
/testcontent generate - Generate test copy_id
/testcontent video MSG_ID - Test video delivery
/testcontent link URL - Test link delivery
```

---

## 📊 Features Deep Dive

### 1. Duplicate Prevention

When a user requests the same content again:
- ❌ Does NOT send duplicate
- ♻️ Invalidates previous reference
- ✅ Sends only the latest request
- 💾 Tracks in database

### 2. Force Join System

Multi-channel support:
- Main channel (required)
- Extra channels (add via admin panel)
- Dynamic checking
- User-friendly join buttons

### 3. Content Types

#### Videos:
- Copied from content channel
- Protected (no forwarding)
- Original quality preserved
- Download enabled

#### Links:
- YouTube, Drive, Telegram, etc.
- Inline button to open
- Clean presentation
- Type detection

### 4. Admin Notifications

When content is added to channel:
```
🆕 New Content Added!

📋 Copy ID: abc12345
📦 Type: VIDEO
🆔 Message ID: 123

💡 Add this Copy ID to your Mini App!
```

---

## 🗄️ Database Schema

### Collections

#### `contents`
```javascript
{
  copy_id: "abc12345",      // Unique identifier
  content_type: "video",    // "video" or "link"
  message_id: 123,          // For videos
  link: "https://...",      // For links
  channel_id: -100xxx,      // Source channel
  created_at: ISODate()
}
```

#### `user_deliveries`
```javascript
{
  user_id: 123456789,       // Telegram user ID
  copy_id: "abc12345",      // Content identifier
  message_id: 456,          // Delivered message ID
  delivered_at: ISODate()
}
```

#### `extra_channels`
```javascript
{
  channel_id: -100xxx,      // Channel ID
  channel_name: "Channel",  // Display name
  is_active: true,          // Status
  added_at: ISODate()
}
```

---

## 🔍 Troubleshooting

### Bot Not Starting

**Check:**
1. Railway logs for errors
2. Environment variables are set
3. MongoDB URI is correct
4. Bot token is valid

**Fix:**
```bash
railway logs  # View Railway logs
railway restart  # Restart service
```

### Database Connection Failed

**Check:**
1. MongoDB IP whitelist (`0.0.0.0/0`)
2. Database user credentials
3. Network access settings

**Fix:**
- Go to MongoDB Atlas → Network Access
- Add `0.0.0.0/0` to IP whitelist

### Content Not Delivering

**Check:**
1. Bot is admin in content channel
2. Message ID is correct
3. Content exists in database
4. User has joined required channels

**Fix:**
```
/stats - Check database status
/testcontent - Test delivery system
```

---

## 🔄 Updates & Maintenance

### Regular Tasks

**Daily:**
- Monitor bot uptime
- Check error logs

**Weekly:**
- Review statistics (`/stats`)
- Clean up old logs

**Monthly:**
- Database optimization
- Update force join channels if needed

### Updating Bot Code

```bash
# Pull latest changes
git pull origin main

# Deploy to Railway
railway up

# Or redeploy via Railway dashboard
```

---

## 🌟 Best Practices

### 1. Content Management
- Use descriptive copy IDs
- Organize content in spreadsheets
- Regular database backups

### 2. Security
- Keep bot token secret
- Regularly update passwords
- Monitor admin access

### 3. User Experience
- Test deep links before sharing
- Keep channels active and engaging
- Respond to user feedback

---

## 📈 Scaling

### Free Tier Limits

**Railway:**
- $5/month credit
- 500 hours runtime
- 512MB RAM

**MongoDB Atlas:**
- 512MB storage
- Shared CPU
- 100 connections

**Render:**
- 750 hours/month
- 512MB RAM
- Auto-sleep after inactivity

### Upgrade Path

When you outgrow free tier:
- Railway: $5-20/month
- MongoDB Atlas: $9+/month
- VPS: $5-50/month

---

## 🤝 Contributing

This is a production bot for CineFlix. For customization:

1. Fork the project
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

## 📄 License

This project is created specifically for CineFlix content distribution.

---

## 📞 Support

For issues or questions:
1. Check `/admin` panel
2. Review Railway logs
3. Verify MongoDB status
4. Check documentation

---

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Video distribution
- ✅ Link distribution
- ✅ Force join
- ✅ Duplicate prevention
- ✅ Admin panel

### Phase 2 (Future)
- 📊 Advanced analytics
- 📢 Broadcast system
- 💰 Payment integration
- 🎨 Custom themes
- 📱 Web dashboard

---

**Built with ❤️ for CineFlix**

**Version:** 1.0.0 (Production Ready)  
**Status:** ✅ Fully Operational  
**Last Updated:** 2025
