import streamlit as st
import json
import os
from datetime import datetime, date
import anthropic
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Personal Command Center",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stat-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    h1, h2, h3 {
        color: #667eea;
    }
    .chat-message {
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
    }
    .assistant-message {
        background: rgba(255, 255, 255, 0.1);
        margin-right: 20%;
    }
</style>
""", unsafe_allow_html=True)

# Data directory
DATA_DIR = Path("dashboard_data")
DATA_DIR.mkdir(exist_ok=True)

# Recipe database
RECIPES = {
    'alpha': {'name': 'Alpha Breakfast', 'ingredients': {'a': 1, 'b': 1, 'e': 3}},
    'beta': {'name': 'Beta Lunch', 'ingredients': {'e': 2}},
    'gamma': {'name': 'Gamma Dinner', 'ingredients': {'c': 1, 'd': 2}},
    'omega': {'name': 'Omega Snack', 'ingredients': {'a': 2, 'b': 1}},
    'delta': {'name': 'Delta Meal', 'ingredients': {'c': 2, 'd': 1, 'e': 1}}
}

INGREDIENT_NAMES = {
    'a': 'Eggs',
    'b': 'Bread',
    'c': 'Rice',
    'd': 'Chicken',
    'e': 'Vegetables'
}

THRESHOLDS = {
    'a': 3,
    'b': 4,
    'c': 5,
    'd': 4,
    'e': 6
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
    except Exception as e:
        st.error(f"Error saving {filename}: {e}")

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if 'inventory' not in st.session_state:
        st.session_state.inventory = load_data('inventory', {'a': 5, 'b': 6, 'c': 3, 'd': 8, 'e': 10})
    
    if 'grocery_list' not in st.session_state:
        st.session_state.grocery_list = load_data('grocery_list', [])
    
    if 'job_applications' not in st.session_state:
        st.session_state.job_applications = load_data('job_applications', [])
    
    if 'vocabulary_words' not in st.session_state:
        st.session_state.vocabulary_words = load_data('vocabulary_words', [])
    
    if 'daily_schedule' not in st.session_state:
        st.session_state.daily_schedule = load_data('daily_schedule', [])
    
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
    
    if 'reading_tasks' not in st.session_state:
        st.session_state.reading_tasks = load_data('reading_tasks', [])

# Update inventory based on cooked recipes
def update_inventory(cooked_recipes):
    """Update inventory when recipes are cooked"""
    updates = []
    
    for recipe_name in cooked_recipes:
        recipe = RECIPES.get(recipe_name.lower())
        if recipe:
            for ingredient, amount in recipe['ingredients'].items():
                if ingredient in st.session_state.inventory:
                    old_value = st.session_state.inventory[ingredient]
                    st.session_state.inventory[ingredient] -= amount
                    new_value = st.session_state.inventory[ingredient]
                    updates.append(f"{INGREDIENT_NAMES[ingredient]}: {old_value} → {new_value}")
    
    # Save updated inventory
    save_data('inventory', st.session_state.inventory)
    
    # Check thresholds and update grocery list
    check_and_update_grocery_list()
    
    return updates

def check_and_update_grocery_list():
    """Check inventory thresholds and update grocery list"""
    for item, quantity in st.session_state.inventory.items():
        if quantity < THRESHOLDS[item]:
            # Check if item is already in grocery list
            if not any(g['item'] == item for g in st.session_state.grocery_list):
                st.session_state.grocery_list.append({
                    'item': item,
                    'name': INGREDIENT_NAMES[item],
                    'needed': THRESHOLDS[item] * 2 - quantity,
                    'added': datetime.now().strftime('%Y-%m-%d')
                })
                save_data('grocery_list', st.session_state.grocery_list)

# AI Chat function
def chat_with_ai(user_message):
    """Process chat message with AI"""
    
    # Check for cooking commands
    if 'cooked' in user_message.lower() or 'cook' in user_message.lower():
        words = user_message.lower().split()
        cooked_recipes = []
        
        for word in words:
            if word in RECIPES:
                cooked_recipes.append(word)
        
        if cooked_recipes:
            updates = update_inventory(cooked_recipes)
            recipe_names = [RECIPES[r]['name'] for r in cooked_recipes]
            return f"✅ Updated inventory! You cooked {', '.join(recipe_names)}.\n\n" + '\n'.join(updates)
    
    # Check for navigation commands
    nav_keywords = ['go to', 'show', 'open', 'navigate to']
    for keyword in nav_keywords:
        if keyword in user_message.lower():
            return "Navigation handled in sidebar! Use the menu on the left to switch between sections."
    
    # Use Anthropic API for general queries
    try:
        # You can set your API key as environment variable or directly here
        # For production, use: os.environ.get('ANTHROPIC_API_KEY')
        client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY', 'your-api-key-here'))
        
        context = f"""You are a helpful personal assistant for a productivity dashboard. Current context:
- Inventory: {json.dumps(st.session_state.inventory)}
- Job Applications: {len(st.session_state.job_applications)} total
- Goals: {len(st.session_state.goals)} active
- Vocabulary Words: {len(st.session_state.vocabulary_words)} learned

User query: {user_message}

Provide helpful, concise responses. For data requests, summarize what's available. For advice, be practical and actionable."""
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": context}
            ]
        )
        
        return message.content[0].text
    
    except Exception as e:
        return f"AI response error: {str(e)}\n\nTry commands like:\n- 'I cooked alpha and beta'\n- 'Show my inventory'\n- 'How many jobs have I applied to?'"

# Visualization functions
def create_inventory_chart():
    """Create inventory bar chart"""
    items = list(INGREDIENT_NAMES.values())
    quantities = [st.session_state.inventory[key] for key in INGREDIENT_NAMES.keys()]
    thresholds = [THRESHOLDS[key] for key in INGREDIENT_NAMES.keys()]
    
    fig = go.Figure()
    
    # Add bars
    fig.add_trace(go.Bar(
        x=items,
        y=quantities,
        name='Current Stock',
        marker_color=['rgb(239, 68, 68)' if q < t else 'rgb(16, 185, 129)' 
                      for q, t in zip(quantities, thresholds)],
        text=quantities,
        textposition='auto',
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
        xaxis_title='Ingredients',
        yaxis_title='Quantity (units)',
        template='plotly_dark',
        height=400,
        showlegend=True
    )
    
    return fig

def create_job_stats_chart():
    """Create job application statistics pie chart"""
    if not st.session_state.job_applications:
        return None
    
    status_counts = {}
    for job in st.session_state.job_applications:
        status = job.get('status', 'Applied')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    fig = go.Figure(data=[go.Pie(
        labels=list(status_counts.keys()),
        values=list(status_counts.values()),
        hole=.3,
        marker_colors=['#667eea', '#f59e0b', '#10b981', '#ef4444']
    )])
    
    fig.update_layout(
        title='Job Application Status Distribution',
        template='plotly_dark',
        height=350
    )
    
    return fig

# Main app
def main():
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("🎯 Command Center")
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigate",
            ["Dashboard", "Jobs", "Reading", "Inventory & Recipes", "Data Collection", "Schedule", "AI Chat"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.caption(f"📅 {datetime.now().strftime('%B %d, %Y')}")
        st.caption(f"⏰ {datetime.now().strftime('%I:%M %p')}")
    
    # Main content area
    if page == "Dashboard":
        show_dashboard()
    elif page == "Jobs":
        show_jobs()
    elif page == "Reading":
        show_reading()
    elif page == "Inventory & Recipes":
        show_inventory()
    elif page == "Data Collection":
        show_data_collection()
    elif page == "Schedule":
        show_schedule()
    elif page == "AI Chat":
        show_ai_chat()

def show_dashboard():
    """Display main dashboard"""
    st.title("🏠 Dashboard")
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 2rem;">📊</div>
            <div class="metric-value">{}</div>
            <div>Job Applications</div>
            <div style="font-size: 0.8rem; opacity: 0.7;">{} interviews</div>
        </div>
        """.format(
            len(st.session_state.job_applications),
            len([j for j in st.session_state.job_applications if j.get('status') == 'Interview'])
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 2rem;">📚</div>
            <div class="metric-value">{}</div>
            <div>Vocabulary Words</div>
            <div style="font-size: 0.8rem; opacity: 0.7;">Total learned</div>
        </div>
        """.format(len(st.session_state.vocabulary_words)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 2rem;">🛒</div>
            <div class="metric-value">{}</div>
            <div>Grocery Items</div>
            <div style="font-size: 0.8rem; opacity: 0.7;">To purchase</div>
        </div>
        """.format(len(st.session_state.grocery_list)), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 2rem;">🎯</div>
            <div class="metric-value">{}</div>
            <div>Active Goals</div>
            <div style="font-size: 0.8rem; opacity: 0.7;">In progress</div>
        </div>
        """.format(len(st.session_state.goals)), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Two column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Inventory Status")
        fig = create_inventory_chart()
        st.plotly_chart(fig, use_container_width=True)
        
        # Low stock warnings
        low_stock = [INGREDIENT_NAMES[k] for k, v in st.session_state.inventory.items() if v < THRESHOLDS[k]]
        if low_stock:
            st.warning(f"⚠️ Low stock: {', '.join(low_stock)}")
    
    with col2:
        st.subheader("🛒 Grocery List")
        if st.session_state.grocery_list:
            for item in st.session_state.grocery_list:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"**{item['name']}** - Need: {item['needed']} units")
                with col_b:
                    if st.button("✓", key=f"remove_{item['item']}"):
                        st.session_state.grocery_list = [g for g in st.session_state.grocery_list if g['item'] != item['item']]
                        save_data('grocery_list', st.session_state.grocery_list)
                        st.rerun()
        else:
            st.success("✨ All stocked up!")
        
        if st.button("➕ Add Custom Item"):
            st.session_state['add_grocery_item'] = True
        
        if st.session_state.get('add_grocery_item'):
            with st.form("add_grocery"):
                item_name = st.text_input("Item Name")
                quantity = st.number_input("Quantity Needed", min_value=1, value=1)
                if st.form_submit_button("Add"):
                    st.session_state.grocery_list.append({
                        'item': 'custom',
                        'name': item_name,
                        'needed': quantity,
                        'added': datetime.now().strftime('%Y-%m-%d')
                    })
                    save_data('grocery_list', st.session_state.grocery_list)
                    st.session_state['add_grocery_item'] = False
                    st.rerun()
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Add Job Application", use_container_width=True):
            st.switch_page = "Jobs"
    with col2:
        if st.button("📚 Add Vocabulary Word", use_container_width=True):
            st.switch_page = "Reading"
    with col3:
        if st.button("🤖 Open AI Chat", use_container_width=True):
            st.switch_page = "AI Chat"
    with col4:
        if st.button("📊 View Analytics", use_container_width=True):
            st.info("Coming soon - detailed analytics dashboard!")

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
    
    # Chart
    if st.session_state.job_applications:
        fig = create_job_stats_chart()
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
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
                date_applied = st.date_input("Date Applied", value=date.today())
            
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
        # Sort by date (most recent first)
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
                    status_color = {
                        'Applied': '🔵',
                        'Interview': '🟡',
                        'Offer': '🟢',
                        'Rejected': '🔴'
                    }
                    st.write(f"{status_color.get(status, '⚪')} {status}")
                    st.caption(f"📅 {job.get('date', 'N/A')}")
                
                with col3:
                    if st.button("🗑️ Delete", key=f"del_job_{idx}"):
                        st.session_state.job_applications.remove(job)
                        save_data('job_applications', st.session_state.job_applications)
                        st.rerun()
                
                st.markdown("---")
    else:
        st.info("No job applications yet. Add your first application above!")
    
    # Target companies section
    st.subheader("🎯 Dream Companies")
    
    with st.expander("➕ Add Target Company"):
        with st.form("target_company"):
            company_name = st.text_input("Company Name")
            reason = st.text_area("Why this company?")
            
            if st.form_submit_button("Add"):
                st.session_state.target_companies.append({
                    'name': company_name,
                    'reason': reason,
                    'added': datetime.now().strftime('%Y-%m-%d')
                })
                save_data('target_companies', st.session_state.target_companies)
                st.rerun()
    
    if st.session_state.target_companies:
        for company in st.session_state.target_companies:
            st.write(f"**{company['name']}**")
            st.caption(company.get('reason', ''))

def show_reading():
    """Display reading and vocabulary section"""
    st.title("📚 Reading & Vocabulary")
    
    # Tabs for different reading categories
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
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
                    save_data('vocabulary_words', st.session_state.vocabulary_words)
                    st.success(f"Added '{word}' to vocabulary!")
                    st.rerun()
        
        st.markdown("---")
        
        # Display today's words (first 3)
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
            
            # Display in grid
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
    """Display inventory and recipes"""
    st.title("📦 Inventory & Recipe Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Inventory")
        
        # Display inventory with edit capability
        for key, name in INGREDIENT_NAMES.items():
            col_a, col_b, col_c = st.columns([2, 2, 1])
            
            with col_a:
                st.write(f"**{name}**")
            
            with col_b:
                current_value = st.session_state.inventory[key]
                threshold = THRESHOLDS[key]
                
                # Progress bar
                percentage = min((current_value / (threshold * 2)) * 100, 100)
                color = "🟢" if current_value >= threshold else "🔴"
                st.write(f"{color} {current_value} units")
                st.progress(percentage / 100)
            
            with col_c:
                new_value = st.number_input(
                    "Update",
                    min_value=0,
                    value=current_value,
                    key=f"inv_{key}",
                    label_visibility="collapsed"
                )
                if new_value != current_value:
                    st.session_state.inventory[key] = new_value
                    save_data('inventory', st.session_state.inventory)
                    check_and_update_grocery_list()
                    st.rerun()
        
        # Manual save button
        if st.button("💾 Save All Changes"):
            save_data('inventory', st.session_state.inventory)
            check_and_update_grocery_list()
            st.success("Inventory saved!")
    
    with col2:
        st.subheader("📋 Available Recipes")
        
        for recipe_key, recipe in RECIPES.items():
            # Check if recipe can be made
            can_make = all(
                st.session_state.inventory.get(ing, 0) >= amount
                for ing, amount in recipe['ingredients'].items()
            )
            
            with st.container():
                col_a, col_b = st.columns([3, 1])
                
                with col_a:
                    st.write(f"**{recipe['name']}**")
                    ingredients_text = ", ".join([
                        f"{amount} {INGREDIENT_NAMES[ing]}"
                        for ing, amount in recipe['ingredients'].items()
                    ])
                    st.caption(f"Requires: {ingredients_text}")
                
                with col_b:
                    if can_make:
                        st.success("✓ Available")
                    else:
                        st.error("✗ Insufficient")
                
                st.markdown("---")
        
        st.info("💡 **Tip:** Use the AI Chat to update inventory!\nSay: 'I cooked alpha and beta'")
    
    # Inventory chart
    st.markdown("---")
    st.subheader("📊 Inventory Visualization")
    fig = create_inventory_chart()
    st.plotly_chart(fig, use_container_width=True)

def show_data_collection():
    """Display data collection section"""
    st.title("📊 Data Collection")
    
    tab1, tab2, tab3 = st.tabs(["💰 Expenses", "🚗 Commute", "🎯 Projects"])
    
    with tab1:
        st.subheader("Daily Expenses Tracker")
        
        with st.expander("➕ Add Expense"):
            with st.form("new_expense"):
                col1, col2 = st.columns(2)
                with col1:
                    category = st.selectbox("Category", 
                        ["Food", "Transport", "Entertainment", "Utilities", "Shopping", "Other"])
                    amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
                with col2:
                    expense_date = st.date_input("Date", value=date.today())
                    notes = st.text_input("Notes")
                
                if st.form_submit_button("Add Expense"):
                    st.session_state.expenses.append({
                        'category': category,
                        'amount': amount,
                        'date': expense_date.strftime('%Y-%m-%d'),
                        'notes': notes
                    })
                    save_data('expenses', st.session_state.expenses)
                    st.success(f"Added ${amount} {category} expense")
                    st.rerun()
        
        if st.session_state.expenses:
            # Summary statistics
            total_spent = sum(e['amount'] for e in st.session_state.expenses)
            st.metric("Total Spent", f"${total_spent:.2f}")
            
            # Show expenses
            for expense in sorted(st.session_state.expenses, key=lambda x: x['date'], reverse=True)[:10]:
                st.write(f"**{expense['category']}** - ${expense['amount']:.2f} on {expense['date']}")
                if expense.get('notes'):
                    st.caption(expense['notes'])
        else:
            st.info("No expenses tracked yet")
    
    with tab2:
        st.subheader("Daily Commute Log")
        st.info("Coming soon - Track your daily commute patterns and costs")
    
    with tab3:
        st.subheader("Personal Projects")
        st.info("Coming soon - Manage and track your personal projects")

def show_schedule():
    """Display daily schedule"""
    st.title("📅 Daily Schedule")
    
    tab1, tab2, tab3 = st.tabs(["🗓️ Today", "🐕 Pet Care", "🧹 Household"])
    
    with tab1:
        st.subheader("Today's Schedule")
        st.info("Coming soon - Manage your daily tasks and time blocks")
    
    with tab2:
        st.subheader("Pet Care Tracker")
        st.info("Coming soon - Track pet grooming, feeding, walks, and vet appointments")
    
    with tab3:
        st.subheader("Household Tasks")
        st.info("Coming soon - Weekly and monthly cleaning schedules")

def show_ai_chat():
    """Display AI chat interface"""
    st.title("🤖 AI Assistant")
    st.caption("Ask questions, get insights, or use voice commands to update your dashboard")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f'<div class="chat-message user-message">{message["content"]}</div>', 
                          unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message">{message["content"]}</div>', 
                          unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Message",
            placeholder="Try: 'I cooked alpha and beta' or 'Show my inventory status'",
            key="chat_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    if send_button and user_input:
        # Add user message
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })
        
        # Get AI response
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
        - **Shopping:** "What's on my grocery list?"
        """)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

if __name__ == "__main__":
    main()
