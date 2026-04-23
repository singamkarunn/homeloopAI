# 🎯 Personal Command Center Dashboard

A comprehensive Python-based personal productivity dashboard with AI integration, inventory management, job tracking, and more!

## 🚀 Features

### ✅ Currently Working

1. **AI Chatbot Assistant**
   - Integrated with Anthropic's Claude API
   - Natural language commands
   - Voice-style commands: "I cooked alpha and beta"
   - Navigation assistance

2. **Smart Inventory Management**
   - Track 5 essential ingredients (Eggs, Bread, Rice, Chicken, Vegetables)
   - Visual progress bars and charts
   - Automatic threshold monitoring
   - Auto-add to grocery list when low

3. **Recipe System**
   - 5 pre-loaded recipes
   - Check ingredient availability
   - AI-powered inventory updates via voice commands

4. **Job Application Tracker**
   - Add/edit/delete applications
   - Track status (Applied, Interview, Offer, Rejected)
   - Statistics and visualizations
   - Target companies list

5. **Vocabulary Learning**
   - Add words with definitions and examples
   - Daily word tracking (3 words/day goal)
   - Complete vocabulary archive

6. **Expense Tracking**
   - Log daily expenses by category
   - Track spending patterns

7. **Data Persistence**
   - All data saved automatically to JSON files
   - Survives between sessions

8. **Beautiful Visualizations**
   - Interactive Plotly charts
   - Real-time inventory status
   - Job application statistics

## 📋 Requirements

- Python 3.8 or higher
- pip (Python package manager)

## 🔧 Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up Anthropic API Key (Optional but Recommended)

The AI chat feature requires an Anthropic API key. You have two options:

**Option A: Environment Variable (Recommended)**
```bash
# On Windows
set ANTHROPIC_API_KEY=your-api-key-here

# On Mac/Linux
export ANTHROPIC_API_KEY=your-api-key-here
```

**Option B: Edit the Code**
Open `personal_dashboard.py` and find this line (around line 149):
```python
client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY', 'your-api-key-here'))
```
Replace `'your-api-key-here'` with your actual API key.

**Get an API Key:**
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key

**Note:** The dashboard will work without an API key, but the AI chat responses will be limited to basic commands (cooking updates, navigation).

## 🎮 Usage

### Running the Dashboard

```bash
streamlit run personal_dashboard.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

### Navigation

Use the sidebar to navigate between sections:
- **Dashboard** - Overview of all your data
- **Jobs** - Job application tracker
- **Reading** - Vocabulary and book tracking
- **Inventory & Recipes** - Manage ingredients and recipes
- **Data Collection** - Expenses and projects
- **Schedule** - Daily tasks and routines
- **AI Chat** - Talk to your AI assistant

### Using the AI Chat

Try these commands:
- `"I cooked alpha and beta"` - Automatically updates inventory
- `"Show my inventory status"` - Get current stock levels
- `"How many jobs have I applied to?"` - Get job statistics
- `"What's on my grocery list?"` - See items to buy

### Managing Inventory

1. Go to "Inventory & Recipes" tab
2. View current stock levels with visual indicators
3. Update quantities manually or use AI chat
4. When items fall below threshold, they're auto-added to grocery list

### Tracking Jobs

1. Go to "Jobs" tab
2. Click "Add New Job Application"
3. Fill in company, position, status, date
4. View statistics and charts
5. Track dream companies in the "Target Companies" section

### Learning Vocabulary

1. Go to "Reading" tab
2. Click "Add New Word"
3. Enter word, definition, and example sentence
4. View today's words (first 3) prominently displayed
5. Browse all learned words in grid view

## 📁 Data Storage

All data is stored in the `dashboard_data/` directory as JSON files:
- `inventory.json` - Ingredient quantities
- `grocery_list.json` - Shopping list
- `job_applications.json` - Job tracker data
- `vocabulary_words.json` - Vocabulary database
- `expenses.json` - Expense records
- And more...

**Backup Your Data:** Simply copy the `dashboard_data/` folder to back up all your information.

## 🎨 Customization

### Adding More Recipes

Edit the `RECIPES` dictionary in `personal_dashboard.py`:

```python
RECIPES = {
    'your_recipe': {
        'name': 'Your Recipe Name',
        'ingredients': {'a': 2, 'b': 1, 'e': 3}  # ingredient: quantity
    }
}
```

### Adding More Ingredients

1. Update `INGREDIENT_NAMES` dictionary
2. Update `THRESHOLDS` dictionary
3. Initialize in `init_session_state()` function

### Changing the Theme

Streamlit supports themes! Create a `.streamlit/config.toml` file:

```toml
[theme]
primaryColor="#667eea"
backgroundColor="#0f172a"
secondaryBackgroundColor="#1e293b"
textColor="#ffffff"
font="sans serif"
```

## 🔮 Coming Soon

Features planned for future updates:
- VFX and video editing task tracker
- Pet care schedule (grooming, feeding, vet appointments)
- Household task management (cleaning, laundry)
- Daily schedule with time blocks
- Book reading progress tracker (tech 75%, non-tech 25%)
- Advanced analytics and insights
- Calendar integration
- Export/import functionality
- Mobile app version
- Voice-to-voice feature

## 🐛 Troubleshooting

**Dashboard won't start:**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

**AI Chat not working:**
- Verify API key is set correctly
- Check API key has credits/quota available
- Basic commands (cooking, navigation) work without API key

**Data not persisting:**
- Check that `dashboard_data/` directory exists
- Ensure you have write permissions in the directory

**Charts not displaying:**
- Update plotly: `pip install --upgrade plotly`
- Clear browser cache

## 💡 Tips

1. **Use the AI Chat** for quick updates - it's faster than clicking through menus
2. **Set your API key as environment variable** for security
3. **Regularly backup** the `dashboard_data/` folder
4. **Check grocery list on Dashboard** for quick shopping reference
5. **Use expanders** to keep the interface clean and organized

## 📝 Example Workflow

**Morning Routine:**
1. Open dashboard
2. Check grocery list on Dashboard
3. Add vocabulary words for the day
4. Review job applications
5. Log any expenses from yesterday

**After Cooking:**
1. Go to AI Chat
2. Type: "I cooked alpha for breakfast"
3. Inventory updates automatically
4. Check if anything added to grocery list

**Weekly Review:**
1. Check job application statistics
2. Review vocabulary progress
3. Analyze expense patterns
4. Update target companies list

## 🤝 Contributing

This is a personal project, but feel free to fork and customize for your needs!

## 📄 License

Personal use - customize as needed for your productivity!

---

**Happy Organizing! 🎯**

For questions or issues, refer to the code comments or Streamlit documentation at https://docs.streamlit.io
