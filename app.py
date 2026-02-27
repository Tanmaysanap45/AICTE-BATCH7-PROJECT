import streamlit as st
import google.generativeai as genai
import re

# 🔐 SECURE API CONFIGURATION
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Keeping gemini-2.5-flash as per your preference
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error("Missing API Key! Please add 'GEMINI_API_KEY' to your Streamlit Secrets.")
    st.stop()

st.set_page_config(page_title="Personalized AI Wellness", layout="wide", page_icon="💪🏻")

# 🎨 Theme Styling
st.markdown("""
<style>
    /* FIX: Targeted hiding of header background while keeping buttons visible */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
        color: white !important;
    }
    
    /* Hides the decoration line at the top */
    [data-testid="stDecoration"] {
        display: none !important;
    }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.4) !important;
        backdrop-filter: blur(15px);
    }
    
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }

    div.stButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        border: 1px solid #333333 !important;
        font-weight: bold !important;
        width: 100% !important;
        height: 50px !important;
        transition: all 0.3s ease-in-out !important;
    }

    div.stButton > button:hover {
        background-color: #222222 !important;
        border: 1px solid #ffffff !important;
    }

    .metric-container {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border-top: 5px solid #ff4b4b;
        text-align: center;
        margin-bottom: 20px;
        color: #1e293b;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        color: white;
        text-shadow: 2px 4px 8px rgba(0,0,0,0.2);
    }

    .stWidgetLabel p, .stTabs [data-baseweb="tab-list"] button p {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# 📋 Sidebar
with st.sidebar:
    st.header("👤 Your Profile")
    goal = st.selectbox("Goal", ["Weight Gain", "Weight Loss", "Muscle Gain", "Maintenance"])
    diet = st.selectbox("Dietary Habit", ["Keto", "Veg", "Non-Veg", "Vegan"])

    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", value=25)
        weight = st.number_input("Weight (kg)", value=80.0)
    with col2:
        height_ft = st.number_input("Height (ft)", value=6.0, step=0.1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])

    budget = st.select_slider("Weekly Budget Level", ["Low", "Medium", "High"])
    location = st.text_input("Country/Region", "")
    equipment = st.radio("Available Equipment", ["No Equipment", "Dumbbells", "Full Gym"])

    generate = st.button("Generate My Personalized Plan")

# 🏷️ Updated Headline
st.markdown("<h1 class='main-title'> AI-Powered Fitness & Nutrition Planner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color: white;'>Smart • Efficient • Accessible</p>", unsafe_allow_html=True)
st.divider()

# 🚀 Validation & Generation Logic
if generate:
    errors = []
    
    if age < 10 or age > 120:
        errors.append("Age must be between 10 and 120.")
    if weight <= 20 or weight > 300:
        errors.append("Please enter a realistic weight (20kg - 300kg).")
    if height_ft < 2.0 or height_ft > 8.5:
        errors.append("Please enter a realistic height (2ft - 8.5ft).")
    if not location.strip():
        errors.append("Please enter your Country/Region.")

    if errors:
        for error in errors:
            st.error(f"⚠️ {error}")
    else:
        # --- 📐 DYNAMIC CALCULATIONS ---
        height_m = height_ft * 0.3048
        height_cm = height_m * 100
        bmi = round(weight / (height_m ** 2), 1)
        status = "Healthy" if 18.5 <= bmi <= 24.9 else "Overweight" if bmi > 24.9 else "Underweight"

        if gender == "Male":
            bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) - 161
        
        tdee = bmr * 1.4

        if goal == "Weight Loss":
            daily_calories = int(tdee - 500)
        elif goal == "Weight Gain":
            daily_calories = int(tdee + 500)
        elif goal == "Muscle Gain":
            daily_calories = int(tdee + 300)
        else:
            daily_calories = int(tdee)

        with st.spinner("AI is crafting your plan..."):
            prompt = f"Professional fitness coach. Plan for: {age}yo {gender}, {weight}kg. BMI: {bmi}. Target: {daily_calories} cal. Goal: {goal}, Diet: {diet}, Budget: {budget}, Location: {location}, Equipment: {equipment}. Provide Health Analysis, Meal Plan, and Workout. Clean plain text, no markdown."

            try:
                response = model.generate_content(prompt)
                clean_text = re.sub(r'[*#`]', '', response.text)

                tab1, tab2 = st.tabs(["📊 Dashboard", "🤖 AI Strategy"])

                with tab1:
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown(f"<div class='metric-container'><h3>BMI</h3><h2>{bmi}</h2><p>{status}</p></div>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"<div class='metric-container'><h3>Daily Calories</h3><h2>{daily_calories}</h2><p>Target</p></div>", unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"<div class='metric-container'><h3>Goal</h3><h2>{goal}</h2></div>", unsafe_allow_html=True)

                    st.divider()
                    st.markdown("<h3 style='color: white;'>Macro Targets</h3>", unsafe_allow_html=True)
                    if diet == "Keto":
                        st.write("Fats 70%"); st.progress(0.7)
                        st.write("Protein 25%"); st.progress(0.25)
                        st.write("Carbs 5%"); st.progress(0.05)
                    else:
                        st.write("Protein 30%"); st.progress(0.3)
                        st.write("Carbs 40%"); st.progress(0.4)
                        st.write("Fats 30%"); st.progress(0.3)

                with tab2:
                    st.markdown(f"""
                    <div style='background-color: rgba(255, 255, 255, 0.98); padding: 30px; border-radius: 20px; border-left: 10px solid #007bff; color: #1e293b;'>
                    {clean_text.replace(chr(10), '<br>')}
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"AI service error: {str(e)}")

else:
    st.markdown("<div style='text-align: center; color: white; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 10px;'>👈 Enter your details in the sidebar and then click 'Generate My Personalized Plan'</div>", unsafe_allow_html=True)
