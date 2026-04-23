import streamlit as st
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import anthropic
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import pytz

# Page configuration
st.set_page_config(
    page_title="Karun's Command Center",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for aesthetic navigation and styling
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    
    /* Hide default sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Navigation bar styling */
    .nav-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 1rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .nav-title {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .nav-tabs {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .stButton > button {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        color: rgba(255, 255, 255, 0.8);
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.5);
        color: white;
        transform: translateY(-2px);
    }
    
    /* Dashboard tiles */
    .dashboard-tile {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        cursor: pointer;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .dashboard-tile:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .tile-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .tile-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .tile-label {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .tile-sublabel {
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.6);
        margin-top: 0.25rem;
    }
    
    /* Real-time clock */
    .clock-container {
        text-align: center;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .clock-time {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .clock-date {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.7);
    }
    
    /* Section headers */
    h1, h2, h3 {
        color: #667eea;
    }
    
    /* Card styling */
    .info-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
    }
    
    /* Table styling */
    .dataframe {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Data directory
DATA_DIR = Path("dashboard_data")
DATA_DIR.mkdir(exist_ok=True)

# Place categories for commute tracking
PLACE_CATEGORIES = {
    'infosys': 'Work',
    'office': 'Work',
    'work': 'Work',
    'sarigama': 'Restaurant',
    'restaurant': 'Restaurant',
    'cafe': 'Restaurant',
    'gas station': 'Gas Station',
    'fuel': 'Gas Station',
    'desi brother': 'Grocery Store',
    'grocery': 'Grocery Store',
    'walmart': 'Grocery Store',
    'target': 'Shopping',
    'planet fitness': 'Gym',
    'gym': 'Gym',
    'fitness': 'Gym',
    'home': 'Home',
    'park': 'Recreation',
    'library': 'Education',
    'hospital': 'Healthcare',
    'doctor': 'Healthcare'
}

# Data management functions
def load_data(filename, default_value):
    """Load data from JSON file"""
    filepath = DATA_DIR / f"{filename}.json"
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading {filename}: {e}")
    return default_value

def save_data(filename, data):
    """Save data to JSON file"""
    filepath = DATA_DIR / f"{filename}.json"
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving {filename}: {e}")
        return False

# Get Dallas, Texas time
def get_dallas_time():
    """Get current time in Dallas, Texas"""
    dallas_tz = pytz.timezone('America/Chicago')
    return datetime.now(dallas_tz)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    
    # Navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Dashboard'
    
    # Inventory with units
    if 'inventory' not in st.session_state:
        st.session_state.inventory = load_data('inventory', {
            'eggs': {'quantity': 5, 'unit': 'quantity', 'threshold': 3, 'name': 'Eggs'},
            'bread': {'quantity': 6, 'unit': 'quantity', 'threshold': 4, 'name': 'Bread'},
            'rice': {'quantity': 3, 'unit': 'lbs', 'threshold': 5, 'name': 'Rice'},
            'chicken': {'quantity': 8, 'unit': 'lbs', 'threshold': 4, 'name': 'Chicken'},
            'vegetables': {'quantity': 10, 'unit': 'quantity', 'threshold': 6, 'name': 'Vegetables'},
            'milk': {'quantity': 64, 'unit': 'oz', 'threshold': 32, 'name': 'Milk'}
        })
    
    # Recipes with dynamic ingredients
    if 'recipes' not in st.session_state:
        st.session_state.recipes = load_data('recipes', {
            'alpha': {'name': 'Alpha Breakfast', 'ingredients': {'eggs': 1, 'bread': 1, 'vegetables': 3}},
            'beta': {'name': 'Beta Lunch', 'ingredients': {'vegetables': 2}},
            'gamma': {'name': 'Gamma Dinner', 'ingredients': {'rice': 1, 'chicken': 2}},
            'omega': {'name': 'Omega Snack', 'ingredients': {'eggs': 2, 'bread': 1}},
            'delta': {'name': 'Delta Meal', 'ingredients': {'rice': 2, 'chicken': 1, 'vegetables': 1}}
        })
    
    # Other data
    if 'grocery_list' not in st.session_state:
        st.session_state.grocery_list = load_data('grocery_list', [])
    
    if 'job_applications' not in st.session_state:
        st.session_state.job_applications = load_data('job_applications', [])
    
    if 'vocabulary_words' not in st.session_state:
        st.session_state.vocabulary_words = load_data('vocabulary_words', [])
    
    if 'daily_tasks' not in st.session_state:
        st.session_state.daily_tasks = load_data('daily_tasks', [])
    
    if 'monthly_tasks' not in st.session_state:
        st.session_state.monthly_tasks = load_data('monthly_tasks', [])
    
    if 'expenses' not in st.session_state:
        st.session_state.expenses = load_data('expenses', [])
    
    if 'goals' not in st.session_state:
        st.session_state.goals = load_data('goals', [])
    
    if 'target_companies' not in st.session_state:
        st.session_state.target_companies = load_data('target_companies', [])
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'projects' not in st.session_state:
        st.session_state.projects = load_data('projects', [])
    
    if 'commute_log' not in st.session_state:
        st.session_state.commute_log = load_data('commute_log', [])

# Navigation function
def navigate_to(page):
    """Navigate to a specific page"""
    st.session_state.current_page = page
    st.rerun()

# Inventory management
def add_inventory_item(item_id, name, quantity, unit, threshold):
    """Add new inventory item"""
    st.session_state.inventory[item_id] = {
        'name': name,
        'quantity': quantity,
        'unit': unit,
        'threshold': threshold
    }
    save_data('inventory', st.session_state.inventory)
    check_and_update_grocery_list()

def delete_inventory_item(item_id):
    """Delete inventory item"""
    if item_id in st.session_state.inventory:
        del st.session_state.inventory[item_id]
        save_data('inventory', st.session_state.inventory)
        # Also remove from grocery list if present
        st.session_state.grocery_list = [g for g in st.session_state.grocery_list if g['item'] != item_id]
        save_data('grocery_list', st.session_state.grocery_list)

def update_inventory_item(item_id, field, value):
    """Update inventory item field"""
    if item_id in st.session_state.inventory:
        st.session_state.inventory[item_id][field] = value
        save_data('inventory', st.session_state.inventory)
        check_and_update_grocery_list()

# Recipe management
def add_recipe(recipe_id, name, ingredients):
    """Add new recipe"""
    st.session_state.recipes[recipe_id] = {
        'name': name,
        'ingredients': ingredients
    }
    save_data('recipes', st.session_state.recipes)

def delete_recipe(recipe_id):
    """Delete recipe"""
    if recipe_id in st.session_state.recipes:
        del st.session_state.recipes[recipe_id]
        save_data('recipes', st.session_state.recipes)

# Check and update grocery list
def check_and_update_grocery_list():
    """Check inventory thresholds and update grocery list"""
    for item_id, item_data in st.session_state.inventory.items():
        if item_data['quantity'] < item_data['threshold']:
            # Check if item is already in grocery list
            if not any(g['item'] == item_id for g in st.session_state.grocery_list):
                st.session_state.grocery_list.append({
                    'item': item_id,
                    'name': item_data['name'],
                    'needed': item_data['threshold'] * 2 - item_data['quantity'],
                    'unit': item_data['unit'],
                    'added': datetime.now().strftime('%Y-%m-%d')
                })
                save_data('grocery_list', st.session_state.grocery_list)

# Update inventory based on cooked recipes
def update_inventory_from_recipe(recipe_ids):
    """Update inventory when recipes are cooked"""
    updates = []
    
    for recipe_id in recipe_ids:
        if recipe_id in st.session_state.recipes:
            recipe = st.session_state.recipes[recipe_id]
            for ingredient, amount in recipe['ingredients'].items():
                if ingredient in st.session_state.inventory:
                    old_value = st.session_state.inventory[ingredient]['quantity']
                    st.session_state.inventory[ingredient]['quantity'] -= amount
                    new_value = st.session_state.inventory[ingredient]['quantity']
                    updates.append(f"{st.session_state.inventory[ingredient]['name']}: {old_value} → {new_value}")
    
    save_data('inventory', st.session_state.inventory)
    check_and_update_grocery_list()
    return updates

# Commute tracking
def add_commute_entry(date, start_time, end_time, place, category=None):
    """Add commute entry with auto-calculated duration"""
    # Parse times
    start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
    
    # Calculate duration
    duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
    
    # Auto-categorize if not provided
    if not category:
        place_lower = place.lower()
        category = 'Other'
        for keyword, cat in PLACE_CATEGORIES.items():
            if keyword in place_lower:
                category = cat
                break
    
    entry = {
        'date': date,
        'start_time': start_time,
        'end_time': end_time,
        'place': place,
        'category': category,
        'duration_minutes': duration_minutes,
        'timestamp': datetime.now().isoformat()
    }
    
    st.session_state.commute_log.append(entry)
    save_data('commute_log', st.session_state.commute_log)
    return entry

# Categorize place
def categorize_place(place):
    """Auto-categorize place based on name"""
    place_lower = place.lower()
    for keyword, category in PLACE_CATEGORIES.items():
        if keyword in place_lower:
            return category
    return 'Other'

# AI Chat function
def chat_with_ai(user_message):
    """Process chat message with AI"""
    
    # Check for cooking commands
    if 'cooked' in user_message.lower() or 'cook' in user_message.lower():
        words = user_message.lower().split()
        cooked_recipes = []
        
        for word in words:
            if word in st.session_state.recipes:
                cooked_recipes.append(word)
        
        if cooked_recipes:
            updates = update_inventory_from_recipe(cooked_recipes)
            recipe_names = [st.session_state.recipes[r]['name'] for r in cooked_recipes]
            return f"✅ Updated inventory! You cooked {', '.join(recipe_names)}.\n\n" + '\n'.join(updates)
    
    # Check for navigation commands
    if any(keyword in user_message.lower() for keyword in ['go to', 'show', 'open', 'navigate to']):
        return "Use the navigation buttons at the top to switch between pages!"
    
    # Use Anthropic API for general queries
    try:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return "AI chat requires an API key. Set ANTHROPIC_API_KEY environment variable.\n\nTry commands like:\n- 'I cooked alpha and beta'\n- Ask about your data"
        
        client = anthropic.Anthropic(api_key=api_key)
        
        context = f"""You are Karun's personal AI assistant. Current context:
- Inventory: {len(st.session_state.inventory)} items
- Job Applications: {len(st.session_state.job_applications)} total
- Goals: {len(st.session_state.goals)} active
- Vocabulary Words: {len(st.session_state.vocabulary_words)} learned
- Daily Tasks: {len([t for t in st.session_state.daily_tasks if not t.get('completed')])} pending
- Commute Entries Today: {len([c for c in st.session_state.commute_log if c['date'] == get_dallas_time().strftime('%Y-%m-%d')])}

User query: {user_message}

Provide helpful, concise responses. Be encouraging and supportive."""
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": context}]
        )
        
        return message.content[0].text
    
    except Exception as e:
        return f"AI response error: {str(e)}\n\nBasic commands still work!"

# Visualization functions
def create_inventory_chart():
    """Create inventory bar chart with thresholds"""
    items = [data['name'] for data in st.session_state.inventory.values()]
    quantities = [data['quantity'] for data in st.session_state.inventory.values()]
    thresholds = [data['threshold'] for data in st.session_state.inventory.values()]
    units = [data['unit'] for data in st.session_state.inventory.values()]
    
    # Create hover text with units
    hover_text = [f"{items[i]}<br>{quantities[i]} {units[i]}<br>Threshold: {thresholds[i]} {units[i]}" 
                  for i in range(len(items))]
    
    fig = go.Figure()
    
    # Add bars
    colors = ['rgb(239, 68, 68)' if q < t else 'rgb(16, 185, 129)' 
              for q, t in zip(quantities, thresholds)]
    
    fig.add_trace(go.Bar(
        x=items,
        y=quantities,
        name='Current Stock',
        marker_color=colors,
        text=[f"{q} {u}" for q, u in zip(quantities, units)],
        textposition='auto',
        hovertext=hover_text,
        hoverinfo='text'
    ))
    
    # Add threshold line
    fig.add_trace(go.Scatter(
        x=items,
        y=thresholds,
        mode='lines+markers',
        name='Threshold',
        line=dict(color='rgb(251, 191, 36)', width=2, dash='dash'),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Inventory Status',
        xaxis_title='Items',
        yaxis_title='Quantity',
        template='plotly_dark',
        height=400,
        showlegend=True
    )
    
    return fig

# Navigation bar component
def render_navigation():
    """Render navigation bar"""
    dallas_time = get_dallas_time()
    
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    
    # Title and Clock
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="nav-title">🎯 Karun\'s Command Center</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="clock-container">
            <div class="clock-time">{dallas_time.strftime('%I:%M:%S %p')}</div>
            <div class="clock-date">{dallas_time.strftime('%A, %B %d, %Y')}</div>
            <div class="clock-date" style="font-size: 0.8rem;">Dallas, Texas</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation buttons
    st.markdown('<div class="nav-tabs">', unsafe_allow_html=True)
    
    pages = ['Dashboard', 'Jobs', 'Reading', 'Inventory', 'Recipes', 'Data Collection', 'Commute', 'Schedule', 'AI Chat']
    
    cols = st.columns(len(pages))
    for idx, page in enumerate(pages):
        with cols[idx]:
            # Highlight active page
            if page == st.session_state.current_page:
                if st.button(f"📍 {page}", key=f"nav_{page}", use_container_width=True):
                    navigate_to(page)
            else:
                if st.button(page, key=f"nav_{page}", use_container_width=True):
                    navigate_to(page)
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# Page renderers
def show_dashboard():
    """Display main dashboard with clickable tiles"""
    st.title("👋 Welcome, Karun")
    
    # Calculate statistics
    total_inventory = len(st.session_state.inventory)
    total_jobs = len(st.session_state.job_applications)
    total_vocab = len(st.session_state.vocabulary_words)
    total_grocery = len(st.session_state.grocery_list)
    total_goals = len([g for g in st.session_state.goals if not g.get('completed', False)])
    today_tasks = len([t for t in st.session_state.daily_tasks if not t.get('completed', False)])
    month_tasks = len([t for t in st.session_state.monthly_tasks if not t.get('completed', False)])
    
    st.markdown("### 📊 Quick Overview")
    
    # Row 1: Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f"📊\n\n{total_jobs}\n\nJob Applications\n\n{len([j for j in st.session_state.job_applications if j.get('status') == 'Interview'])} interviews", 
                     key="tile_jobs", use_container_width=True):
            navigate_to('Jobs')
    
    with col2:
        if st.button(f"📚\n\n{total_vocab}\n\nVocabulary Words\n\nTotal learned", 
                     key="tile_vocab", use_container_width=True):
            navigate_to('Reading')
    
    with col3:
        if st.button(f"🛒\n\n{total_grocery}\n\nGrocery Items\n\nTo purchase", 
                     key="tile_grocery", use_container_width=True):
            st.session_state.show_grocery = True
            st.rerun()
    
    with col4:
        if st.button(f"🎯\n\n{total_goals}\n\nActive Goals\n\nIn progress", 
                     key="tile_goals", use_container_width=True):
            st.session_state.show_goals = True
            st.rerun()
    
    # Row 2: Inventory and Tasks
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"📦\n\n{total_inventory}\n\nInventory Items\n\n{len([i for i, d in st.session_state.inventory.items() if d['quantity'] < d['threshold']])} low stock", 
                     key="tile_inventory", use_container_width=True):
            navigate_to('Inventory')
    
    with col2:
        if st.button(f"✅\n\n{today_tasks}\n\nTasks for Today\n\nPending", 
                     key="tile_tasks_day", use_container_width=True):
            navigate_to('Schedule')
    
    with col3:
        if st.button(f"📅\n\n{month_tasks}\n\nTasks for Month\n\nPending", 
                     key="tile_tasks_month", use_container_width=True):
            navigate_to('Schedule')
    
    st.markdown("---")
    
    # Grocery list modal
    if st.session_state.get('show_grocery'):
        st.subheader("🛒 Grocery List")
        if st.session_state.grocery_list:
            for item in st.session_state.grocery_list:
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.write(f"**{item['name']}** - {item['needed']} {item.get('unit', 'units')}")
                with col_b:
                    if st.button("✓", key=f"remove_grocery_{item['item']}"):
                        st.session_state.grocery_list = [g for g in st.session_state.grocery_list if g['item'] != item['item']]
                        save_data('grocery_list', st.session_state.grocery_list)
                        st.rerun()
        else:
            st.success("✨ All stocked up!")
        
        if st.button("Close"):
            st.session_state.show_grocery = False
            st.rerun()
    
    # Goals modal
    if st.session_state.get('show_goals'):
        st.subheader("🎯 Active Goals")
        if st.session_state.goals:
            for goal in [g for g in st.session_state.goals if not g.get('completed', False)]:
                st.write(f"**{goal.get('title', 'Untitled')}**")
                st.caption(goal.get('description', ''))
        else:
            st.info("No active goals. Set some goals in the Schedule section!")
        
        if st.button("Close"):
            st.session_state.show_goals = False
            st.rerun()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Inventory Status")
        fig = create_inventory_chart()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 This Week's Activity")
        # Activity summary
        today = get_dallas_time().strftime('%Y-%m-%d')
        week_start = (get_dallas_time() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        week_commutes = len([c for c in st.session_state.commute_log if c['date'] >= week_start])
        week_vocab = len([v for v in st.session_state.vocabulary_words if v.get('date', '') >= week_start])
        week_jobs = len([j for j in st.session_state.job_applications if j.get('date', '') >= week_start])
        
        st.metric("Commute Trips", week_commutes)
        st.metric("New Vocabulary", week_vocab)
        st.metric("Job Applications", week_jobs)

def show_jobs():
    """Display job applications tracker"""
    st.title("💼 Job Applications")
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Applied", len(st.session_state.job_applications))
    with col2:
        interviews = len([j for j in st.session_state.job_applications if j.get('status') == 'Interview'])
        st.metric("Interviews", interviews)
    with col3:
        offers = len([j for j in st.session_state.job_applications if j.get('status') == 'Offer'])
        st.metric("Offers", offers)
    with col4:
        rejected = len([j for j in st.session_state.job_applications if j.get('status') == 'Rejected'])
        st.metric("Rejected", rejected)
    
    st.markdown("---")
    
    # Add new application
    with st.expander("➕ Add New Job Application", expanded=False):
        with st.form("new_job"):
            col1, col2 = st.columns(2)
            with col1:
                company = st.text_input("Company Name")
                position = st.text_input("Position")
            with col2:
                status = st.selectbox("Status", ["Applied", "Interview", "Offer", "Rejected"])
                date_applied = st.date_input("Date Applied", value=get_dallas_time().date())
            
            notes = st.text_area("Notes (optional)")
            
            if st.form_submit_button("Add Application"):
                st.session_state.job_applications.append({
                    'id': datetime.now().timestamp(),
                    'company': company,
                    'position': position,
                    'status': status,
                    'date': date_applied.strftime('%Y-%m-%d'),
                    'notes': notes
                })
                save_data('job_applications', st.session_state.job_applications)
                st.success(f"Added application for {position} at {company}!")
                st.rerun()
    
    st.markdown("---")
    
    # Display applications
    st.subheader("📋 All Applications")
    
    if st.session_state.job_applications:
        sorted_jobs = sorted(st.session_state.job_applications, 
                           key=lambda x: x.get('date', ''), reverse=True)
        
        for idx, job in enumerate(sorted_jobs):
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.subheader(f"{job.get('company', 'Unknown Company')}")
                    st.write(f"**Position:** {job.get('position', 'N/A')}")
                    if job.get('notes'):
                        st.caption(job['notes'])
                
                with col2:
                    status = job.get('status', 'Applied')
                    status_emoji = {
                        'Applied': '🔵',
                        'Interview': '🟡',
                        'Offer': '🟢',
                        'Rejected': '🔴'
                    }
                    st.write(f"{status_emoji.get(status, '⚪')} {status}")
                    st.caption(f"📅 {job.get('date', 'N/A')}")
                
                with col3:
                    if st.button("🗑️ Delete", key=f"del_job_{idx}"):
                        st.session_state.job_applications.remove(job)
                        save_data('job_applications', st.session_state.job_applications)
                        st.rerun()
                
                st.markdown("---")
    else:
        st.info("No job applications yet. Add your first application above!")
    
    # Target companies
    st.subheader("🎯 Dream Companies")
    
    with st.expander("➕ Add Target Company"):
        with st.form("target_company"):
            company_name = st.text_input("Company Name")
            reason = st.text_area("Why this company?")
            
            if st.form_submit_button("Add"):
                st.session_state.target_companies.append({
                    'name': company_name,
                    'reason': reason,
                    'added': get_dallas_time().strftime('%Y-%m-%d')
                })
                save_data('target_companies', st.session_state.target_companies)
                st.rerun()
    
    if st.session_state.target_companies:
        for idx, company in enumerate(st.session_state.target_companies):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{company['name']}**")
                st.caption(company.get('reason', ''))
            with col2:
                if st.button("🗑️", key=f"del_target_{idx}"):
                    st.session_state.target_companies.remove(company)
                    save_data('target_companies', st.session_state.target_companies)
                    st.rerun()

def show_reading():
    """Display reading and vocabulary section"""
    st.title("📚 Reading & Vocabulary")
    
    tab1, tab2, tab3 = st.tabs(["📖 Vocabulary", "💻 Tech Books", "📕 Non-Tech Books"])
    
    with tab1:
        st.subheader("Daily Vocabulary (3 words/day)")
        
        # Add new word
        with st.expander("➕ Add New Word"):
            with st.form("new_vocab"):
                word = st.text_input("Word")
                definition = st.text_area("Definition")
                example = st.text_input("Example Sentence")
                
                if st.form_submit_button("Add Word"):
                    st.session_state.vocabulary_words.insert(0, {
                        'id': datetime.now().timestamp(),
                        'word': word,
                        'definition': definition,
                        'example': example,
                        'date': get_dallas_time().strftime('%Y-%m-%d')
                    })
                    save_data('vocabulary_words', st.session_state.vocabulary_words)
                    st.success(f"Added '{word}' to vocabulary!")
                    st.rerun()
        
        st.markdown("---")
        
        # Display today's words
        if st.session_state.vocabulary_words:
            st.subheader("🌟 Today's Words")
            for word in st.session_state.vocabulary_words[:3]:
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"### {word.get('word', 'Unknown')}")
                        st.write(word.get('definition', 'No definition'))
                        if word.get('example'):
                            st.caption(f"*\"{word['example']}\"*")
                        st.caption(f"Added: {word.get('date', 'Unknown')}")
                    with col2:
                        if st.button("🗑️", key=f"del_vocab_{word.get('id')}"):
                            st.session_state.vocabulary_words.remove(word)
                            save_data('vocabulary_words', st.session_state.vocabulary_words)
                            st.rerun()
                    st.markdown("---")
            
            # All words
            st.subheader(f"📚 All Vocabulary ({len(st.session_state.vocabulary_words)} words)")
            
            cols = st.columns(3)
            for idx, word in enumerate(st.session_state.vocabulary_words):
                with cols[idx % 3]:
                    st.markdown(f"**{word.get('word')}**")
                    st.caption(word.get('definition', '')[:50] + '...' if len(word.get('definition', '')) > 50 else word.get('definition', ''))
        else:
            st.info("No vocabulary words yet. Start learning!")
    
    with tab2:
        st.subheader("💻 Tech Books (75% focus)")
        st.info("Coming soon - Track your tech reading progress with detailed task breakdowns")
    
    with tab3:
        st.subheader("📕 Non-Tech Books (25% focus)")
        st.info("Coming soon - Track general reading with vocabulary focus")

def show_inventory():
    """Display inventory management with add/delete/edit"""
    st.title("📦 Inventory Management")
    
    # Add new item
    with st.expander("➕ Add New Inventory Item"):
        with st.form("new_inventory_item"):
            col1, col2 = st.columns(2)
            with col1:
                item_name = st.text_input("Item Name")
                item_id = st.text_input("Item ID (lowercase, no spaces)", value=item_name.lower().replace(' ', '_') if item_name else '')
            with col2:
                quantity = st.number_input("Initial Quantity", min_value=0, value=10)
                unit = st.selectbox("Unit Type", ["quantity", "lbs", "oz", "ml", "kg", "g"])
            
            threshold = st.number_input("Low Stock Threshold", min_value=0, value=5)
            
            if st.form_submit_button("Add Item"):
                if item_id and item_name:
                    add_inventory_item(item_id, item_name, quantity, unit, threshold)
                    st.success(f"Added {item_name} to inventory!")
                    st.rerun()
                else:
                    st.error("Please provide both item name and ID")
    
    st.markdown("---")
    
    # Display and edit inventory
    st.subheader("Current Inventory")
    
    if st.session_state.inventory:
        for item_id, item_data in st.session_state.inventory.items():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"**{item_data['name']}**")
                
                with col2:
                    new_qty = st.number_input(
                        "Quantity",
                        min_value=0,
                        value=item_data['quantity'],
                        key=f"qty_{item_id}",
                        label_visibility="collapsed"
                    )
                    if new_qty != item_data['quantity']:
                        update_inventory_item(item_id, 'quantity', new_qty)
                        st.rerun()
                
                with col3:
                    st.selectbox(
                        "Unit",
                        ["quantity", "lbs", "oz", "ml", "kg", "g"],
                        index=["quantity", "lbs", "oz", "ml", "kg", "g"].index(item_data['unit']),
                        key=f"unit_{item_id}",
                        label_visibility="collapsed",
                        on_change=lambda id=item_id: update_inventory_item(id, 'unit', st.session_state[f"unit_{id}"])
                    )
                
                with col4:
                    new_threshold = st.number_input(
                        "Threshold",
                        min_value=0,
                        value=item_data['threshold'],
                        key=f"threshold_{item_id}",
                        label_visibility="collapsed"
                    )
                    if new_threshold != item_data['threshold']:
                        update_inventory_item(item_id, 'threshold', new_threshold)
                        st.rerun()
                
                with col5:
                    if st.button("🗑️", key=f"del_inv_{item_id}"):
                        delete_inventory_item(item_id)
                        st.rerun()
                
                # Status indicator
                if item_data['quantity'] < item_data['threshold']:
                    st.error(f"⚠️ Low stock! Currently {item_data['quantity']} {item_data['unit']}, threshold is {item_data['threshold']} {item_data['unit']}")
                else:
                    st.success(f"✓ In stock: {item_data['quantity']} {item_data['unit']}")
                
                st.markdown("---")
    else:
        st.info("No inventory items yet. Add your first item above!")
    
    # Inventory chart
    st.markdown("---")
    st.subheader("📊 Inventory Visualization")
    fig = create_inventory_chart()
    st.plotly_chart(fig, use_container_width=True)

def show_recipes():
    """Display recipe management with add/delete"""
    st.title("🍳 Recipe Management")
    
    # Add new recipe
    with st.expander("➕ Add New Recipe"):
        with st.form("new_recipe"):
            recipe_name = st.text_input("Recipe Name")
            recipe_id = st.text_input("Recipe ID (lowercase, no spaces)", value=recipe_name.lower().replace(' ', '_') if recipe_name else '')
            
            st.write("**Ingredients:**")
            
            # Dynamic ingredient selection
            num_ingredients = st.number_input("Number of ingredients", min_value=1, max_value=10, value=3)
            
            ingredients = {}
            for i in range(num_ingredients):
                col1, col2 = st.columns(2)
                with col1:
                    ingredient_id = st.selectbox(f"Ingredient {i+1}", 
                                                list(st.session_state.inventory.keys()),
                                                key=f"ing_{i}")
                with col2:
                    amount = st.number_input(f"Amount", min_value=1, value=1, key=f"amt_{i}")
                
                if ingredient_id:
                    ingredients[ingredient_id] = amount
            
            if st.form_submit_button("Add Recipe"):
                if recipe_id and recipe_name and ingredients:
                    add_recipe(recipe_id, recipe_name, ingredients)
                    st.success(f"Added recipe: {recipe_name}!")
                    st.rerun()
                else:
                    st.error("Please provide recipe name, ID, and at least one ingredient")
    
    st.markdown("---")
    
    # Display recipes
    st.subheader("📋 Available Recipes")
    
    if st.session_state.recipes:
        for recipe_id, recipe in st.session_state.recipes.items():
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                # Check if recipe can be made
                can_make = all(
                    st.session_state.inventory.get(ing, {}).get('quantity', 0) >= amount
                    for ing, amount in recipe['ingredients'].items()
                )
                
                with col1:
                    st.subheader(recipe['name'])
                    
                    # Display ingredients
                    st.write("**Requires:**")
                    for ing_id, amount in recipe['ingredients'].items():
                        if ing_id in st.session_state.inventory:
                            ing_data = st.session_state.inventory[ing_id]
                            available = ing_data['quantity']
                            unit = ing_data['unit']
                            
                            if available >= amount:
                                st.write(f"✓ {amount} {unit} {ing_data['name']} (have {available})")
                            else:
                                st.write(f"✗ {amount} {unit} {ing_data['name']} (only have {available})")
                        else:
                            st.write(f"✗ {amount} {ing_id} (not in inventory)")
                
                with col2:
                    if can_make:
                        st.success("✓ Can Make")
                        if st.button("Cook This", key=f"cook_{recipe_id}"):
                            updates = update_inventory_from_recipe([recipe_id])
                            st.success(f"Cooked {recipe['name']}! Inventory updated.")
                            st.info("\n".join(updates))
                            st.rerun()
                    else:
                        st.error("✗ Insufficient")
                    
                    if st.button("🗑️ Delete", key=f"del_recipe_{recipe_id}"):
                        delete_recipe(recipe_id)
                        st.rerun()
                
                st.markdown("---")
    else:
        st.info("No recipes yet. Add your first recipe above!")

def show_commute():
    """Display commute tracking"""
    st.title("🚗 Commute Tracker")
    
    # Add commute entry
    with st.expander("➕ Add Commute Entry"):
        with st.form("new_commute"):
            col1, col2 = st.columns(2)
            
            with col1:
                commute_date = st.date_input("Date", value=get_dallas_time().date())
                start_time = st.time_input("Start Time")
                end_time = st.time_input("End Time")
            
            with col2:
                place = st.text_input("Place")
                auto_category = categorize_place(place) if place else "Other"
                st.info(f"Auto-detected category: {auto_category}")
                category = st.selectbox("Category (edit if needed)", 
                                       ["Work", "Restaurant", "Gas Station", "Grocery Store", 
                                        "Shopping", "Gym", "Home", "Recreation", "Education", 
                                        "Healthcare", "Other"],
                                       index=["Work", "Restaurant", "Gas Station", "Grocery Store", 
                                              "Shopping", "Gym", "Home", "Recreation", "Education", 
                                              "Healthcare", "Other"].index(auto_category))
            
            if st.form_submit_button("Add Entry"):
                if place:
                    entry = add_commute_entry(
                        commute_date.strftime('%Y-%m-%d'),
                        start_time.strftime('%H:%M'),
                        end_time.strftime('%H:%M'),
                        place,
                        category
                    )
                    st.success(f"Added commute to {place} ({entry['duration_minutes']} minutes)")
                    st.rerun()
                else:
                    st.error("Please provide a place")
    
    st.markdown("---")
    
    # Display today's commutes
    today = get_dallas_time().strftime('%Y-%m-%d')
    today_commutes = [c for c in st.session_state.commute_log if c['date'] == today]
    
    if today_commutes:
        st.subheader(f"📅 Today's Commutes ({len(today_commutes)} trips)")
        
        # Sort by start time
        today_commutes.sort(key=lambda x: x['start_time'])
        
        total_duration = sum(c['duration_minutes'] for c in today_commutes)
        st.metric("Total Time Commuting Today", f"{total_duration} minutes ({total_duration/60:.1f} hours)")
        
        # Create timeline
        for idx, entry in enumerate(today_commutes):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**{entry['start_time']} - {entry['end_time']}**")
                st.caption(f"{entry['duration_minutes']} minutes")
            
            with col2:
                st.write(f"📍 {entry['place']}")
                st.caption(f"Category: {entry['category']}")
            
            with col3:
                if st.button("🗑️", key=f"del_commute_{idx}"):
                    st.session_state.commute_log.remove(entry)
                    save_data('commute_log', st.session_state.commute_log)
                    st.rerun()
            
            st.markdown("---")
        
        # Category breakdown
        st.subheader("📊 Today's Places by Category")
        category_counts = {}
        for entry in today_commutes:
            cat = entry['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        fig = go.Figure(data=[go.Pie(
            labels=list(category_counts.keys()),
            values=list(category_counts.values()),
            hole=.3
        )])
        fig.update_layout(template='plotly_dark', height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No commutes logged for today yet!")
    
    # All commutes
    st.markdown("---")
    st.subheader(f"📜 All Commute History ({len(st.session_state.commute_log)} total entries)")
    
    if st.session_state.commute_log:
        # Show last 20 entries
        recent_commutes = sorted(st.session_state.commute_log, 
                                key=lambda x: (x['date'], x['start_time']), 
                                reverse=True)[:20]
        
        df = pd.DataFrame(recent_commutes)
        df = df[['date', 'start_time', 'end_time', 'place', 'category', 'duration_minutes']]
        df.columns = ['Date', 'Start', 'End', 'Place', 'Category', 'Duration (min)']
        
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No commute data yet!")

def show_data_collection():
    """Display data collection section"""
    st.title("📊 Data Collection")
    
    tab1, tab2 = st.tabs(["💰 Expenses", "🎯 Projects"])
    
    with tab1:
        st.subheader("Daily Expenses Tracker")
        
        with st.expander("➕ Add Expense"):
            with st.form("new_expense"):
                col1, col2 = st.columns(2)
                with col1:
                    category = st.selectbox("Category", 
                        ["Food", "Transport", "Entertainment", "Utilities", "Shopping", "Healthcare", "Other"])
                    amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
                with col2:
                    expense_date = st.date_input("Date", value=get_dallas_time().date())
                    notes = st.text_input("Notes")
                
                if st.form_submit_button("Add Expense"):
                    st.session_state.expenses.append({
                        'category': category,
                        'amount': amount,
                        'date': expense_date.strftime('%Y-%m-%d'),
                        'notes': notes,
                        'timestamp': datetime.now().isoformat()
                    })
                    save_data('expenses', st.session_state.expenses)
                    st.success(f"Added ${amount} {category} expense")
                    st.rerun()
        
        if st.session_state.expenses:
            total_spent = sum(e['amount'] for e in st.session_state.expenses)
            st.metric("Total Spent (All Time)", f"${total_spent:.2f}")
            
            # Recent expenses
            recent = sorted(st.session_state.expenses, key=lambda x: x['date'], reverse=True)[:10]
            for expense in recent:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{expense['category']}** - ${expense['amount']:.2f} on {expense['date']}")
                    if expense.get('notes'):
                        st.caption(expense['notes'])
                with col2:
                    if st.button("🗑️", key=f"del_exp_{expense.get('timestamp')}"):
                        st.session_state.expenses.remove(expense)
                        save_data('expenses', st.session_state.expenses)
                        st.rerun()
        else:
            st.info("No expenses tracked yet")
    
    with tab2:
        st.subheader("Personal Projects")
        
        with st.expander("➕ Add Project"):
            with st.form("new_project"):
                project_name = st.text_input("Project Name")
                project_desc = st.text_area("Description")
                project_status = st.selectbox("Status", ["Planning", "In Progress", "Completed", "On Hold"])
                
                if st.form_submit_button("Add Project"):
                    st.session_state.projects.append({
                        'name': project_name,
                        'description': project_desc,
                        'status': project_status,
                        'created': get_dallas_time().strftime('%Y-%m-%d'),
                        'id': datetime.now().timestamp()
                    })
                    save_data('projects', st.session_state.projects)
                    st.success(f"Added project: {project_name}")
                    st.rerun()
        
        if st.session_state.projects:
            for project in st.session_state.projects:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(project['name'])
                    st.write(project.get('description', ''))
                    st.caption(f"Status: {project['status']} | Created: {project.get('created', 'Unknown')}")
                with col2:
                    if st.button("🗑️", key=f"del_proj_{project.get('id')}"):
                        st.session_state.projects.remove(project)
                        save_data('projects', st.session_state.projects)
                        st.rerun()
                st.markdown("---")
        else:
            st.info("No projects yet")

def show_schedule():
    """Display daily and monthly schedule"""
    st.title("📅 Daily & Monthly Schedule")
    
    tab1, tab2, tab3 = st.tabs(["✅ Daily Tasks", "📅 Monthly Tasks", "🎯 Goals"])
    
    with tab1:
        st.subheader("Today's Tasks")
        
        with st.expander("➕ Add Daily Task"):
            with st.form("new_daily_task"):
                task_title = st.text_input("Task")
                task_time = st.time_input("Time")
                
                if st.form_submit_button("Add Task"):
                    st.session_state.daily_tasks.append({
                        'title': task_title,
                        'time': task_time.strftime('%H:%M'),
                        'completed': False,
                        'date': get_dallas_time().strftime('%Y-%m-%d'),
                        'id': datetime.now().timestamp()
                    })
                    save_data('daily_tasks', st.session_state.daily_tasks)
                    st.success(f"Added task: {task_title}")
                    st.rerun()
        
        # Show today's tasks
        today = get_dallas_time().strftime('%Y-%m-%d')
        today_tasks = [t for t in st.session_state.daily_tasks if t.get('date') == today]
        
        if today_tasks:
            for task in sorted(today_tasks, key=lambda x: x.get('time', '')):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    is_complete = task.get('completed', False)
                    if st.checkbox(task['title'], value=is_complete, key=f"task_{task['id']}"):
                        task['completed'] = True
                        save_data('daily_tasks', st.session_state.daily_tasks)
                    st.caption(f"⏰ {task.get('time', 'No time set')}")
                
                with col3:
                    if st.button("🗑️", key=f"del_daily_{task['id']}"):
                        st.session_state.daily_tasks.remove(task)
                        save_data('daily_tasks', st.session_state.daily_tasks)
                        st.rerun()
        else:
            st.info("No tasks for today")
    
    with tab2:
        st.subheader("Monthly Tasks")
        
        with st.expander("➕ Add Monthly Task"):
            with st.form("new_monthly_task"):
                task_title = st.text_input("Task")
                task_deadline = st.date_input("Deadline")
                
                if st.form_submit_button("Add Task"):
                    st.session_state.monthly_tasks.append({
                        'title': task_title,
                        'deadline': task_deadline.strftime('%Y-%m-%d'),
                        'completed': False,
                        'id': datetime.now().timestamp()
                    })
                    save_data('monthly_tasks', st.session_state.monthly_tasks)
                    st.success(f"Added monthly task: {task_title}")
                    st.rerun()
        
        if st.session_state.monthly_tasks:
            for task in sorted(st.session_state.monthly_tasks, key=lambda x: x.get('deadline', '')):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    is_complete = task.get('completed', False)
                    if st.checkbox(task['title'], value=is_complete, key=f"mtask_{task['id']}"):
                        task['completed'] = True
                        save_data('monthly_tasks', st.session_state.monthly_tasks)
                    st.caption(f"📅 Deadline: {task.get('deadline', 'No deadline')}")
                
                with col2:
                    if st.button("🗑️", key=f"del_monthly_{task['id']}"):
                        st.session_state.monthly_tasks.remove(task)
                        save_data('monthly_tasks', st.session_state.monthly_tasks)
                        st.rerun()
        else:
            st.info("No monthly tasks")
    
    with tab3:
        st.subheader("Goals")
        
        with st.expander("➕ Add Goal"):
            with st.form("new_goal"):
                goal_title = st.text_input("Goal")
                goal_desc = st.text_area("Description")
                
                if st.form_submit_button("Add Goal"):
                    st.session_state.goals.append({
                        'title': goal_title,
                        'description': goal_desc,
                        'completed': False,
                        'created': get_dallas_time().strftime('%Y-%m-%d'),
                        'id': datetime.now().timestamp()
                    })
                    save_data('goals', st.session_state.goals)
                    st.success(f"Added goal: {goal_title}")
                    st.rerun()
        
        if st.session_state.goals:
            for goal in st.session_state.goals:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    is_complete = goal.get('completed', False)
                    if st.checkbox(goal['title'], value=is_complete, key=f"goal_{goal['id']}"):
                        goal['completed'] = True
                        save_data('goals', st.session_state.goals)
                    st.caption(goal.get('description', ''))
                    st.caption(f"Created: {goal.get('created', 'Unknown')}")
                
                with col2:
                    if st.button("🗑️", key=f"del_goal_{goal['id']}"):
                        st.session_state.goals.remove(goal)
                        save_data('goals', st.session_state.goals)
                        st.rerun()
        else:
            st.info("No goals yet")

def show_ai_chat():
    """Display AI chat interface"""
    st.title("🤖 AI Assistant")
    st.caption("Ask questions, get insights, or use commands to update your dashboard")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.chat_message("user").write(message['content'])
        else:
            st.chat_message("assistant").write(message['content'])
    
    # Chat input
    user_input = st.chat_input("Message your AI assistant...")
    
    if user_input:
        # Add user message
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })
        
        # Get AI response
        with st.spinner("Thinking..."):
            response = chat_with_ai(user_input)
        
        # Add AI response
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': response
        })
        
        st.rerun()
    
    # Example commands
    with st.expander("💡 Example Commands"):
        st.markdown("""
        - **Cooking:** "I cooked alpha and beta"
        - **Inventory:** "Show my inventory status"
        - **Jobs:** "How many jobs have I applied to?"
        - **Vocabulary:** "How many words have I learned?"
        - **General:** Ask any question about your data!
        """)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# Main app
def main():
    init_session_state()
    
    # Render navigation
    render_navigation()
    
    # Render current page
    if st.session_state.current_page == 'Dashboard':
        show_dashboard()
    elif st.session_state.current_page == 'Jobs':
        show_jobs()
    elif st.session_state.current_page == 'Reading':
        show_reading()
    elif st.session_state.current_page == 'Inventory':
        show_inventory()
    elif st.session_state.current_page == 'Recipes':
        show_recipes()
    elif st.session_state.current_page == 'Data Collection':
        show_data_collection()
    elif st.session_state.current_page == 'Commute':
        show_commute()
    elif st.session_state.current_page == 'Schedule':
        show_schedule()
    elif st.session_state.current_page == 'AI Chat':
        show_ai_chat()

if __name__ == "__main__":
    main()
