# 🎬 CineFlix Bot - সম্পূর্ণ Setup Guide (বাংলা)

এই guide অনুসরণ করে তুমি তোমার production-ready Telegram bot deploy করতে পারবে।

---

## 📋 Table of Contents

1. [Prerequisites (প্রয়োজনীয় জিনিস)](#prerequisites)
2. [MongoDB Atlas Setup](#mongodb-setup)
3. [Bot Configuration](#bot-configuration)
4. [Railway Deployment](#railway-deployment)
5. [Testing](#testing)
6. [Admin Commands](#admin-commands)
7. [Mini App Integration](#mini-app-integration)
8. [Troubleshooting](#troubleshooting)

---

## 1️⃣ Prerequisites (প্রয়োজনীয় জিনিস) {#prerequisites}

তোমার কাছে যা যা থাকতে হবে:

✅ Telegram Bot Token (@BotFather থেকে)
✅ তোমার Telegram User ID (@userinfobot থেকে)
✅ Content Channel (Bot কে admin বানাতে হবে)
✅ Force Join Channel (Bot কে admin বানাতে হবে)
✅ MongoDB Atlas Account (Free)
✅ Railway Account (Free)
✅ GitHub Account (Optional, কিন্তু recommended)

---

## 2️⃣ MongoDB Atlas Setup {#mongodb-setup}

### Step 1: Account তৈরি করো

1. যাও: https://www.mongodb.com/cloud/atlas/register
2. Sign up করো (Google/GitHub দিয়ে করতে পারো)
3. Free tier select করো (M0 Sandbox - Forever Free)

### Step 2: Cluster তৈরি করো

1. "Create a Cluster" বাটনে ক্লিক করো
2. **FREE tier** select করো (M0)
3. Cloud Provider: **AWS** (recommended)
4. Region: তোমার কাছের region select করো (Singapore/Mumbai)
5. Cluster Name: `cineflix-cluster` (যেকোনো নাম দিতে পারো)
6. "Create Cluster" বাটনে ক্লিক করো
7. ⏳ 1-3 মিনিট wait করো cluster তৈরি হতে

### Step 3: Database User তৈরি করো

1. Left sidebar থেকে **"Database Access"** এ যাও
2. "Add New Database User" ক্লিক করো
3. **Authentication Method:** Password
4. **Username:** `joymodol717` (already set)
5. **Password:** `risha464323` (already set)
6. **Database User Privileges:** "Read and write to any database"
7. "Add User" বাটনে ক্লিক করো

### Step 4: Network Access Setup

1. Left sidebar থেকে **"Network Access"** এ যাও
2. "Add IP Address" ক্লিক করো
3. **"Allow Access from Anywhere"** select করো
4. IP Address: `0.0.0.0/0` (automatically fill হবে)
5. "Confirm" ক্লিক করো

### Step 5: Connection String নাও

1. Left sidebar থেকে **"Database"** এ ফিরে যাও
2. তোমার cluster এ **"Connect"** বাটনে ক্লিক করো
3. "Connect your application" select করো
4. Driver: **Python**, Version: **3.11 or later**
5. Connection string copy করো:
   ```
   mongodb+srv://joymodol717:risha464323@cluster0.i9ueyks.mongodb.net/?appName=Cluster0
   ```
6. ✅ এটা তোমার `.env` file এ use করবে

---

## 3️⃣ Bot Configuration {#bot-configuration}

### Step 1: Project Download করো

তুমি project ZIP file পেয়ে গেছো। Extract করো।

### Step 2: .env File তৈরি করো

1. `.env.example` file কে rename করো `.env` (dot env)
2. অথবা নতুন `.env` file তৈরি করো
3. নিচের template copy করো এবং তোমার values দাও:

```env
# Bot Credentials
BOT_TOKEN=8006015641:AAHX1rE8ppAGsK4fnEmBUnFEr_xoWhfLDc4
API_ID=25115930
API_HASH=11f8f3d058991d44083d5c7c135964c5

# Admin
ADMIN_ID=1858324638

# Channels
CONTENT_CHANNEL_ID=-1003872857468
FORCE_JOIN_CHANNEL_ID=-1003749088877
CHANNEL_USERNAME=@Cineflixofficialbd

# Database
MONGODB_URI=mongodb+srv://joymodol717:risha464323@cluster0.i9ueyks.mongodb.net/?appName=Cluster0
DATABASE_NAME=cineflix_bot

# Notifications
ENABLE_NOTIFICATIONS=Yes
```

### Step 3: Verify Bot Permissions

নিশ্চিত করো:

1. ✅ Bot তোমার **Content Channel** এ admin
2. ✅ Bot তোমার **Force Join Channel** এ admin
3. ✅ Bot এর permissions:
   - ✅ Post Messages
   - ✅ Edit Messages
   - ✅ Delete Messages
   - ✅ Invite Users via Link

---

## 4️⃣ Railway Deployment {#railway-deployment}

### Option A: GitHub থেকে Deploy (Recommended)

#### Step 1: GitHub এ Code Upload করো

```bash
# Terminal open করো project folder এ

git init
git add .
git commit -m "Initial commit - CineFlix Bot"

# GitHub এ নতুন repository তৈরি করো
# তারপর:

git remote add origin https://github.com/YOUR_USERNAME/cineflix-bot.git
git branch -M main
git push -u origin main
```

#### Step 2: Railway এ Deploy করো

1. যাও: https://railway.app/
2. **"Start a New Project"** ক্লিক করো
3. **"Deploy from GitHub repo"** select করো
4. তোমার `cineflix-bot` repository select করো
5. Railway automatically detect করবে এবং deploy শুরু করবে

#### Step 3: Environment Variables Add করো

1. Railway dashboard এ তোমার project ক্লিক করো
2. **"Variables"** tab এ যাও
3. **"Raw Editor"** ক্লিক করো
4. তোমার `.env` file এর সব content paste করো
5. **"Save"** ক্লিক করো

#### Step 4: Deploy সম্পূর্ণ হবে

⏳ 2-5 মিনিট wait করো। Railway automatically:
- ✅ Dependencies install করবে
- ✅ Bot start করবে
- ✅ Database connect করবে

### Option B: Direct Upload (GitHub ছাড়া)

1. Railway dashboard এ **"Deploy from CLI"** option use করো
2. Railway CLI install করো
3. Project folder এ:
   ```bash
   railway login
   railway init
   railway up
   ```

---

## 5️⃣ Testing {#testing}

### Test 1: Bot Running Check

1. Telegram এ তোমার bot খোলো
2. `/start` command পাঠাও
3. Welcome message আসা উচিত

### Test 2: Force Join Check

1. Force join channel থেকে leave করো
2. Bot এ কোনো content request করো (deep link)
3. Join করতে বলবে

### Test 3: Content Delivery Test

#### Video Test:

1. Content channel এ একটা video পাঠাও/forward করো
2. Bot তোমাকে notification পাঠাবে copy_id দিয়ে
3. সেই copy_id দিয়ে deep link তৈরি করো:
   ```
   https://t.me/Cinaflix_Streembot?start=content_COPY_ID
   ```
4. লিংকে ক্লিক করো
5. Video পাওয়া উচিত (forwarding disabled)

#### Link Test:

1. Content channel এ একটা link পাঠাও (YouTube/Drive link)
2. Bot notification পাঠাবে copy_id সহ
3. Deep link তৈরি করো এবং test করো

### Test 4: Admin Panel

```
/admin - Admin panel open করো
/stats - Statistics দেখো
/testcontent - Test content delivery
```

---

## 6️⃣ Admin Commands {#admin-commands}

### 🎯 Main Commands

```
/start - Bot শুরু করো
/admin - Admin panel খোলো
/stats - Bot statistics
/help - Help message
```

### 📊 Statistics

```
/stats - সম্পূর্ণ statistics দেখো
```

### 📢 Channel Management

```
/addchannel CHANNEL_ID - Extra force join channel add করো
/removechannel CHANNEL_ID - Channel remove করো
/listchannels - সব channels list দেখো
```

**Example:**
```
/addchannel -1001234567890
/removechannel -1001234567890
/listchannels
```

### 🧪 Testing

```
/testcontent - Test menu খোলো
/testcontent generate - Test copy_id generate করো
/testcontent video MESSAGE_ID - Test video delivery
/testcontent link URL - Test link delivery
```

**Example:**
```
/testcontent generate
/testcontent video 123
/testcontent link https://youtube.com/watch?v=xxx
```

---

## 7️⃣ Mini App Integration {#mini-app-integration}

### Deep Link Format

```
https://t.me/YOUR_BOT_USERNAME?start=content_COPY_ID
```

**Example:**
```
https://t.me/Cinaflix_Streembot?start=content_abc12345
```

### Google Sheets Integration

#### Sheet Structure:

| Content Name | Copy ID | Type | Deep Link |
|-------------|---------|------|-----------|
| Movie 1 | abc123 | video | =CONCATENATE("https://t.me/Cinaflix_Streembot?start=content_", B2) |
| Movie 2 | xyz789 | video | =CONCATENATE("https://t.me/Cinaflix_Streembot?start=content_", B3) |

#### Mini App HTML Example:

```html
<!DOCTYPE html>
<html>
<head>
    <title>CineFlix Content</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
</head>
<body>
    <div id="content-list"></div>
    
    <script>
        // Telegram Mini App initialization
        let tg = window.Telegram.WebApp;
        tg.expand();
        
        // Sample content from Google Sheets API
        const contents = [
            { name: "Movie 1", copyId: "abc123", type: "video" },
            { name: "Movie 2", copyId: "xyz789", type: "video" }
        ];
        
        // Render content
        contents.forEach(item => {
            const btn = document.createElement('button');
            btn.textContent = item.name;
            btn.onclick = () => {
                // Open bot with deep link
                tg.openTelegramLink(`https://t.me/Cinaflix_Streembot?start=content_${item.copyId}`);
            };
            document.getElementById('content-list').appendChild(btn);
        });
    </script>
</body>
</html>
```

---

## 8️⃣ Troubleshooting {#troubleshooting}

### ❌ Bot Start হচ্ছে না

**সমাধান:**
1. Railway logs check করো
2. `.env` variables ঠিক আছে কিনা দেখো
3. MongoDB URI correct কিনা verify করো
4. Railway এ restart করো

### ❌ Database Connection Failed

**সমাধান:**
1. MongoDB Atlas এ IP whitelist check করো (`0.0.0.0/0` আছে কিনা)
2. Database user credentials ঠিক আছে কিনা দেখো
3. Connection string এ special characters escape করা আছে কিনা check করো

### ❌ Content Deliver হচ্ছে না

**সমাধান:**
1. Bot content channel এ admin কিনা check করো
2. Message ID সঠিক কিনা verify করো
3. Content channel ID ঠিক আছে কিনা দেখো
4. Bot এর post messages permission আছে কিনা check করো

### ❌ Force Join কাজ করছে না

**সমাধান:**
1. Bot force join channel এ admin কিনা check করো
2. Channel ID negative (-100 দিয়ে শুরু) কিনা verify করো
3. Bot এর "Invite Users" permission আছে কিনা check করো

### ❌ Duplicate Prevention কাজ করছে না

**সমাধান:**
1. Database connection check করো
2. `/stats` command দিয়ে database status দেখো
3. Railway restart করো

---

## 🎉 Congratulations!

তোমার **CineFlix Bot** এখন fully functional এবং production-ready! 🚀

### 📞 Support

কোনো সমস্যা হলে:
1. প্রথমে `/admin` panel check করো
2. Railway logs দেখো
3. MongoDB Atlas status verify করো

---

## 🔄 Updates & Maintenance

### Regular Maintenance:

1. **Weekly:**
   - `/stats` দিয়ে bot health check করো
   - Database size monitor করো (Free tier: 512MB)

2. **Monthly:**
   - Unused delivery records cleanup করো
   - Channel list update করো

3. **As Needed:**
   - Extra channels add/remove করো
   - Force join requirements adjust করো

---

## 📚 Additional Features (Future)

আমরা ভবিষ্যতে add করতে পারি:

- 📊 Advanced analytics
- 📢 Broadcast messaging
- 🎨 Custom themes
- 📱 Web dashboard
- 🔔 User notifications
- 💰 Payment integration

---

**Built with ❤️ by CineFlix Team**
**Version:** 1.0.0 (Production Ready)
