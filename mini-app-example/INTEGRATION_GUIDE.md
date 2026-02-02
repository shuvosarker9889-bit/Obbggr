# 📱 Mini App Integration Guide

এই guide তোমাকে দেখাবে কিভাবে Google Sheets এর সাথে Mini App integrate করবে।

---

## 📋 Option 1: Simple Google Sheets (No Coding)

### Step 1: Create Google Sheet

1. নতুন Google Sheet তৈরি করো
2. নিচের columns বানাও:

| A: Content Name | B: Copy ID | C: Type | D: Deep Link |
|----------------|-----------|---------|--------------|

### Step 2: Add Formula for Deep Link

Cell D2 তে এই formula লিখো:
```
=CONCATENATE("https://t.me/Cinaflix_Streembot?start=content_", B2)
```

এটা automatically deep link generate করবে।

### Step 3: Share Links

Users কে সরাসরি Column D এর links share করো।

---

## 📋 Option 2: Google Sheets API + Mini App (Advanced)

### Step 1: Enable Google Sheets API

1. যাও: https://console.cloud.google.com/
2. নতুন project তৈরি করো
3. "Enable APIs and Services" ক্লিক করো
4. "Google Sheets API" search করে enable করো
5. Credentials তৈরি করো (API Key)

### Step 2: Make Sheet Public

1. তোমার Google Sheet খোলো
2. Share বাটনে ক্লিক করো
3. "Anyone with the link" select করো
4. Sheet ID copy করো (URL থেকে):
   ```
   https://docs.google.com/spreadsheets/d/SHEET_ID/edit
   ```

### Step 3: Update Mini App

`mini-app-example/index.html` file এ:

```javascript
// Replace this function:
async function loadFromGoogleSheets() {
    const SHEET_ID = 'YOUR_SHEET_ID';
    const API_KEY = 'YOUR_API_KEY';
    const RANGE = 'Sheet1!A2:C'; // Adjust range as needed
    
    const url = `https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${RANGE}?key=${API_KEY}`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        // Convert to content format
        const contents = data.values.map(row => ({
            name: row[0],      // Column A: Name
            copyId: row[1],    // Column B: Copy ID
            type: row[2],      // Column C: Type
            icon: row[2] === 'video' ? '🎬' : '🔗'
        }));
        
        return contents;
    } catch (error) {
        console.error('Error:', error);
        return [];
    }
}
```

### Step 4: Host Mini App

তুমি Mini App host করতে পারো:

#### GitHub Pages (Free):
1. GitHub এ নতুন repo তৈরি করো
2. `index.html` upload করো
3. Settings → Pages → Enable GitHub Pages
4. URL পাবে: `https://username.github.io/repo-name/`

#### Netlify (Free):
1. Netlify.com এ sign up করো
2. "New site from Git" ক্লিক করো
3. GitHub repo select করো
4. Deploy!

### Step 5: Register in Telegram

1. @BotFather এ যাও
2. তোমার bot select করো
3. `/newapp` command দাও
4. Mini App URL দাও (GitHub Pages/Netlify URL)
5. Title, description, icon set করো

---

## 📋 Option 3: Inline Buttons (Simplest)

Bot directly inline buttons দিয়ে content serve করতে পারো:

```python
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Create menu
buttons = [
    [InlineKeyboardButton("🎬 Movie 1", url="https://t.me/bot?start=content_abc123")],
    [InlineKeyboardButton("🎬 Movie 2", url="https://t.me/bot?start=content_xyz789")],
]

keyboard = InlineKeyboardMarkup(buttons)

await message.reply_text("Select content:", reply_markup=keyboard)
```

---

## 📊 Google Sheets Template

### Sheet Structure:

```
┌─────────────────┬──────────┬────────┬────────────────────────────────────────┐
│  Content Name   │ Copy ID  │  Type  │           Deep Link                    │
├─────────────────┼──────────┼────────┼────────────────────────────────────────┤
│  Movie 1        │ abc123   │ video  │ https://t.me/bot?start=content_abc123  │
│  Movie 2        │ xyz789   │ video  │ https://t.me/bot?start=content_xyz789  │
│  YouTube Link   │ yt001    │ link   │ https://t.me/bot?start=content_yt001   │
│  Drive File     │ drv002   │ link   │ https://t.me/bot?start=content_drv002  │
└─────────────────┴──────────┴────────┴────────────────────────────────────────┘
```

### Formula in Column D:
```
=CONCATENATE("https://t.me/Cinaflix_Streembot?start=content_", B2)
```

Drag down করো সব rows এ apply করতে।

---

## 🔧 Testing Mini App

### Local Testing:
1. Mini App HTML file খোলো browser এ
2. Console check করো errors এর জন্য
3. Click করে দেখো buttons কাজ করছে কিনা

### Telegram Testing:
1. Mini App URL Telegram এ open করো
2. @BotFather দিয়ে bot এ attach করো
3. Bot এ `/start` দিয়ে Mini App button দেখো
4. Click করে test করো

---

## 🎨 Customization

### Colors:
Mini App তোমার bot এর theme follow করবে।

### Icons:
Different content types এর জন্য আলাদা icons:
- 🎬 Movies
- 🎥 Videos
- ▶️ YouTube
- 📁 Drive
- 🔗 Links

### Layout:
CSS customize করো `index.html` এ।

---

## 📝 Best Practices

1. **Copy IDs:**
   - Short এবং memorable রাখো
   - Pattern follow করো (e.g., movie001, movie002)

2. **Content Organization:**
   - Categories অনুযায়ী organize করো
   - Search functionality add করো (optional)

3. **Updates:**
   - Regular update করো content list
   - Old/expired content remove করো

---

## 🚀 Advanced Features (Optional)

### Search Functionality:
```javascript
function searchContent(query) {
    return contents.filter(item => 
        item.name.toLowerCase().includes(query.toLowerCase())
    );
}
```

### Categories:
```javascript
const categories = {
    movies: contents.filter(c => c.type === 'video'),
    links: contents.filter(c => c.type === 'link')
};
```

### Pagination:
```javascript
function paginateContent(contents, page, perPage = 10) {
    const start = (page - 1) * perPage;
    const end = start + perPage;
    return contents.slice(start, end);
}
```

---

## ✅ Checklist

Before launching:

- [ ] Google Sheets setup complete
- [ ] Deep link formula working
- [ ] Copy IDs generated for all content
- [ ] Mini App hosted (if using)
- [ ] Bot tested with sample content
- [ ] Force join channels configured
- [ ] Admin notifications enabled

---

**তোমার Mini App ready! 🎉**
