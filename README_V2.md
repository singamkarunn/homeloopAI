# 🎯 Karun's Personal Command Center

A comprehensive Python-based personal productivity dashboard with AI integration, inventory management with multiple units, commute tracking, and real-time Dallas time display!

## 🚀 New Features in V2

### ✨ Major Improvements

1. **Aesthetic Navigation Bar**
   - Beautiful bookmark-style page navigation
   - Soft highlight on active page
   - Real-time Dallas, Texas clock
   - No more circular sidebar!

2. **Enhanced Dashboard**
   - **"Welcome, Karun"** instead of generic "Dashboard"
   - **Clickable tiles** that navigate to respective pages:
     - Job Applications → Jobs page
     - Vocabulary Words → Reading page
     - Grocery Items → Shows grocery list modal
     - Active Goals → Shows goals modal
     - Inventory Items → Inventory page
     - Tasks for Today → Schedule page
     - Tasks for Month → Schedule page
   - All tiles show real-time counts and statistics

3. **Advanced Inventory Management**
   - ✅ **Add new items** with custom names
   - ✅ **Delete items** you don't need
   - ✅ **Edit quantities** in real-time
   - ✅ **Adjustable thresholds** per item
   - ✅ **Multiple unit types**: quantity, lbs, oz, ml, kg, g
   - Auto-updates grocery list when below threshold
   - Visual charts with threshold lines

4. **Recipe Management**
   - ✅ **Add custom recipes** with any ingredients
   - ✅ **Delete recipes** you don't use
   - Shows which recipes you can make with current inventory
   - **One-click cooking** - updates inventory automatically
   - Uses real ingredient names (eggs, bread, rice, etc.)

5. **Commute Tracking**
   - ✅ **Auto-calculates duration** from start/end times
   - ✅ **Auto-categorizes places**:
     - Infosys → Work
     - Sarigama → Restaurant
     - Desi Brother → Grocery Store
     - Planet Fitness → Gym
     - Gas Station → Gas Station
     - Home → Home
   - Track all places visited in a day
   - View today's commutes with timeline
   - Category breakdown pie chart
   - Full commute history with sorting

6. **Real-Time Dallas Clock**
   - Shows current time in Dallas, Texas (Central Time)
   - Updates automatically
   - Displays full date and location

7. **Data Migration**
   - Automatically converts old data format to new format
   - Preserves your existing data
   - No manual migration needed!

## 📋 Complete Features List

### ✅ Currently Working

1. **AI Chatbot Assistant**
   - Integrated with Anthropic's Claude API
   - Natural language commands
   - "I cooked alpha and beta" updates inventory
   - Navigation and data queries

2. **Smart Inventory Management**
   - Multiple unit types (quantity, lbs, oz, ml, kg, g)
   - Add/delete/edit items
   - Adjustable thresholds per item
   - Auto-generates grocery list
   - Visual charts with Plotly

3. **Recipe System**
   - Add/delete custom recipes
   - Dynamic ingredient selection
   - One-click cooking
   - Shows availability status

4. **Job Application Tracker**
   - Add/edit/delete applications
   - Track status (Applied, Interview, Offer, Rejected)
   - Statistics dashboard
   - Target/dream companies list

5. **Vocabulary Learning**
   - Add words with definitions and examples
   - Daily focus on 3 words
   - Complete word archive

6. **Expense Tracking**
   - Log expenses by category
   - Track spending patterns
   - View totals

7. **Commute Tracking**
   - Auto-calculate trip duration
   - Auto-categorize locations
   - Daily timeline view
   - Full history with search

8. **Projects Tracking**
   - Manage personal projects
   - Track status and progress

9. **Task Management**
   - Daily tasks with time slots
   - Monthly tasks with deadlines
   - Checkbox completion tracking

10. **Goals System**
    - Set and track goals
    - Mark as complete
    - View active goals count

11. **Data Persistence**
    - All data saved to JSON files
    - Automatic backups
    - Format migration

## 🔧 Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- streamlit (web framework)
- anthropic (AI chat)
- plotly (charts)
- pandas (data handling)
- pytz (timezone support)

### Step 2: Set Up Anthropic API Key (Optional)

**Get a free key** at https://console.anthropic.com/

**Option A: Environment Variable (Recommended)**
```bash
# Windows
set ANTHROPIC_API_KEY=your-api-key-here

# Mac/Linux
export ANTHROPIC_API_KEY=your-api-key-here
```

**Option B: Edit the Code**
Find line ~149 in `personal_dashboard_v2.py` and add your key.

**Note:** Basic features work without API key!

## 🎮 Usage

### Running the Dashboard

```bash
streamlit run personal_dashboard_v2.py
```

Opens at `http://localhost:8501`

### Navigation

Click the page buttons in the top navigation bar:
- **Dashboard** - Welcome page with clickable tiles
- **Jobs** - Job application tracker
- **Reading** - Vocabulary and books
- **Inventory** - Manage stock levels
- **Recipes** - Add/delete/cook recipes
- **Data Collection** - Expenses and projects
- **Commute** - Track trips and places
- **Schedule** - Daily/monthly tasks and goals
- **AI Chat** - Talk to your assistant

### Real-Time Clock

The navigation bar shows:
- Current time in Dallas, Texas
- Full date (Day, Month DD, YYYY)
- Location label

### Using Clickable Dashboard Tiles

Click any tile to jump to that section:
- **Job Applications** → Jobs page
- **Vocabulary Words** → Reading page
- **Grocery Items** → Opens grocery list
- **Active Goals** → Shows goals
- **Inventory Items** → Inventory page
- **Tasks Today** → Schedule page
- **Tasks Month** → Schedule page

### Managing Inventory

1. Go to **Inventory** page
2. **Add Item**: Click "Add New Inventory Item"
   - Enter name, ID, quantity, unit type, threshold
3. **Edit Item**: Change quantity, unit, or threshold inline
4. **Delete Item**: Click 🗑️ button
5. Items below threshold auto-add to grocery list

**Supported Units:**
- `quantity` - Count (e.g., 5 eggs)
- `lbs` - Pounds
- `oz` - Ounces (fluid or weight)
- `ml` - Milliliters
- `kg` - Kilograms
- `g` - Grams

### Managing Recipes

1. Go to **Recipes** page
2. **Add Recipe**: Click "Add New Recipe"
   - Name your recipe
   - Select ingredients from inventory
   - Set amounts needed
3. **Cook Recipe**: Click "Cook This" button
   - Automatically deducts ingredients
   - Updates grocery list if needed
4. **Delete Recipe**: Click 🗑️ button

### Tracking Commute

1. Go to **Commute** page
2. **Add Entry**: Click "Add Commute Entry"
   - Select date
   - Enter start time (e.g., 11:20 AM)
   - Enter end time (e.g., 12:15 PM)
   - Enter place name (e.g., "Infosys")
   - System auto-calculates duration
   - System auto-categorizes place
3. View today's timeline and category breakdown
4. See full history sorted by date

**Example Daily Commute:**
- 11:20 AM → Infosys (Work) → Duration: 55 min
- 1:20 PM → Sarigama (Restaurant) → Duration: auto-calculated
- Gas Station → Auto-categorized
- 6:00 PM → Desi Brother (Grocery Store)
- 8:00 PM → Planet Fitness (Gym)
- 9:10 PM → Home

### Using AI Chat

Try these commands:
- `"I cooked alpha and beta"` - Updates inventory
- `"Show my inventory"` - Get current levels
- `"How many jobs applied?"` - Statistics
- Ask any question about your data!

## 📁 Data Storage

All data saved in `dashboard_data/` folder:
- `inventory.json` - Stock levels with units
- `recipes.json` - Your custom recipes
- `grocery_list.json` - Shopping list
- `job_applications.json` - Job tracker
- `vocabulary_words.json` - Word database
- `commute_log.json` - Trip history
- `expenses.json` - Spending records
- `projects.json` - Project tracking
- `daily_tasks.json` - Today's tasks
- `monthly_tasks.json` - Long-term tasks
- `goals.json` - Your goals

**Backup:** Copy `dashboard_data/` folder!

## 🎨 What Makes This Special

### Aesthetic Navigation
- Beautiful bookmark-style tabs
- Soft gradient highlights
- No clunky sidebar
- Real-time clock integration

### Smart Auto-Features
- **Auto-calculate** commute duration
- **Auto-categorize** places based on keywords
- **Auto-update** grocery list when low
- **Auto-migrate** old data format

### Clickable Dashboard
- Every tile is interactive
- Instant navigation
- Real-time statistics
- Modal popups for quick views

### Flexible Units
- Mix and match unit types
- Change units per item
- Threshold per item
- Visual charts adapt

## 🔮 Coming Soon

Features planned for future updates:
- Voice-to-voice AI chat
- VFX/Video editing tracker
- Pet care detailed schedule
- Book reading progress (75% tech, 25% non-tech)
- Advanced analytics and insights
- Calendar integration
- Export/import functionality
- Mobile optimizations

## 🐛 Troubleshooting

**Old data format issues:**
- V2 automatically migrates old data
- If issues persist, delete `dashboard_data/` and restart

**Navigation not working:**
- Make sure you're clicking the nav buttons at top
- Check console for errors

**Commute duration wrong:**
- Check start time is before end time
- Use 24-hour or AM/PM format correctly

**Inventory not updating:**
- Check ingredient names match in recipes
- Verify inventory item exists

## 💡 Pro Tips

1. **Use AI Chat** for fastest updates
2. **Click dashboard tiles** to navigate quickly
3. **Set custom thresholds** per ingredient
4. **Let auto-categorization** handle place types
5. **Check grocery list** before shopping
6. **Track commutes daily** for patterns

## 🆕 What's Different from V1

| Feature | V1 | V2 |
|---------|----|----|
| Navigation | Sidebar | Top bookmark-style bar |
| Dashboard | Generic stats | Clickable tiles |
| Title | "Dashboard" | "Welcome, Karun" |
| Inventory Units | Single type | Multiple (qty, lbs, oz, ml) |
| Inventory Edit | Limited | Full CRUD |
| Recipes | Fixed | Add/delete custom |
| Commute | Not available | Full tracking |
| Clock | Static | Real-time Dallas |
| Data Format | Old | Auto-migrated |

## 📊 Example Workflow

**Morning:**
1. Check Dashboard tiles
2. See low inventory items
3. View grocery list
4. Check today's tasks

**After Cooking:**
1. Go to AI Chat
2. Type: "I cooked alpha for breakfast"
3. Inventory auto-updates
4. Grocery list auto-updates

**During Day:**
1. Add commute entries as you travel
2. Track expenses
3. Add vocabulary words learned
4. Update job applications

**Evening:**
1. Review dashboard statistics
2. Plan tomorrow's tasks
3. Check weekly commute patterns
4. Set new goals

---

**Built with ❤️ for Karun's productivity!** 🎯

For questions, check the code comments or Streamlit docs at https://docs.streamlit.io
