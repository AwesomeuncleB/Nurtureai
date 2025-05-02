from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import base64
import urllib.parse

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Gemini model and get response
def get_gemini_response(input_prompt, image, user_input):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt, image[0], user_input])
    return response.text

# Function to process the uploaded image
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{
            "mime_type": uploaded_file.type,
            "data": bytes_data
        }]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Ensure medical disclaimer is added
def ensure_medical_disclaimer(text):
    disclaimer = "⚠️ Please consult a healthcare professional for personalized advice."
    if disclaimer not in text:
        text += f"\n\n{disclaimer}"
    return text

# Function to create a WhatsApp share link with text
def get_whatsapp_share_link(text):
    encoded_text = urllib.parse.quote(text)
    return f"https://wa.me/?text={encoded_text}"

# Function to create WhatsApp chat link for chatbot
def get_whatsapp_chat_link():
    # You would replace this with your actual WhatsApp Business API phone number
    whatsapp_number = "1234567890"  # Replace with your business number
    return f"https://wa.me/{+15556389843}?text=I%20want%20to%20chat%20with%20NurtureAI"

# Page configuration
st.set_page_config(
    page_title="NurtureAI - Health Management App",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with dark color scheme
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        color: #E2E8F0;
    }
    
    /* Dark mode for Streamlit components */
    .stApp {
        background-color: #1A202C;
    }
    
    /* Headers */
    .main-header {
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 600;
        background: linear-gradient(120deg, #38B2AC, #4299E1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #90CDF4;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    /* Cards and Containers */
    .category-card {
        background-color: #2D3748;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #38B2AC;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    .user-type-card {
        background-color: #2D3748;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #4299E1;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    .upload-card {
        background-color: #2D3748;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #63B3ED;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    .results-card {
        background-color: #2D3748;
        border-radius: 10px;
        padding: 25px;
        margin-top: 20px;
        border-left: 5px solid #A0AEC0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    /* Icons and Status */
    .icon-text {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .icon {
        margin-right: 10px;
        color: #38B2AC;
    }
    
    .safe-tag {
        color: #E6FFFA;
        font-weight: 600;
        padding: 3px 8px;
        background-color: #285E61;
        border-radius: 4px;
        display: inline-block;
    }
    
    .unsafe-tag {
        color: #FFF5F5;
        font-weight: 600;
        padding: 3px 8px; 
        background-color: #742A2A;
        border-radius: 4px;
        display: inline-block;
    }
    
    .disclaimer-box {
        background-color: #3C2A1E;
        color: #FBD38D;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 15px 0;
        border: 1px solid #744210;
        font-size: 0.9rem;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #38B2AC;
        color: white;
        font-weight: 500;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #2C7A7B;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
        transform: translateY(-2px);
    }
    
    /* WhatsApp Button */
    .whatsapp-button {
        background-color: #25D366;
        color: white;
        font-weight: 500;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        text-decoration: none;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .whatsapp-button:hover {
        background-color: #128C7E;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
        transform: translateY(-2px);
    }
    
    .whatsapp-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    
    .whatsapp-modal-content {
        background-color: #2D3748;
        padding: 30px;
        border-radius: 15px;
        width: 400px;
        max-width: 90%;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
    }
    
    .whatsapp-option {
        background-color: #38B2AC;
        color: white;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 10px;
        transition: all 0.3s ease;
    }
    
    .whatsapp-option:hover {
        background-color: #2C7A7B;
        transform: translateY(-2px);
    }
    
    .whatsapp-close {
        background-color: #4A5568;
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        cursor: pointer;
        text-align: center;
        margin-top: 20px;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input {
        background-color: #4A5568;
        color: #E2E8F0;
        border: 1px solid #4A5568;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background-color: #4A5568;
        color: #E2E8F0;
        border: 1px solid #4A5568;
    }
    
    /* Radio buttons */
    div.stRadio > div {
        background-color: #4A5568;
        padding: 10px;
        border-radius: 8px;
    }
    
    div.stRadio > div > label {
        background-color: #2D3748;
        color: #E2E8F0;
        padding: 10px 15px;
        border-radius: 6px;
        margin: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        transition: all 0.2s ease;
    }
    
    div.stRadio > div > label:hover {
        background-color: #4A5568;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }
    
    /* Footer */
    .footer {
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #4A5568;
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        color: #A0AEC0;
    }
    
    /* Category Icons */
    .category-icon {
        font-size: 24px;
        margin-right: 10px;
        vertical-align: middle;
    }
    
    /* Upload Preview */
    .upload-preview {
        border: 1px dashed #63B3ED;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
    }
    
    /* Links */
    a {
        color: #63B3ED;
        text-decoration: none;
        transition: all 0.2s ease;
    }
    
    a:hover {
        color: #90CDF4;
        text-decoration: underline;
    }
    
    /* Streamlit text elements */
    p, div, span, label, .stMarkdown {
        color: #E2E8F0;
    }
    
    /* Info box */
    .stAlert {
        background-color: #2C3E50;
        color: #A0AEC0;
    }
    
    /* Calorie Counter Styles */
    .calorie-card {
        background-color: #2D3748;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #ED8936;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    .calorie-table {
        width: 100%;
        margin-top: 15px;
        border-collapse: separate;
        border-spacing: 0;
    }
    
    .calorie-table th {
        background-color: #4A5568;
        color: #E2E8F0;
        padding: 10px;
        text-align: left;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }
    
    .calorie-table td {
        padding: 10px;
        border-top: 1px solid #4A5568;
    }
    
    .calorie-total {
        font-weight: bold;
        color: #ED8936;
        font-size: 1.2rem;
        margin-top: 15px;
        padding: 10px;
        background-color: #3C2A1E;
        border-radius: 8px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Add WhatsApp modal JavaScript for popup
st.markdown("""
<script>
function showWhatsAppModal() {
    document.getElementById('whatsapp-modal').style.display = 'flex';
}

function hideWhatsAppModal() {
    document.getElementById('whatsapp-modal').style.display = 'none';
}

function openWhatsAppChat() {
    window.open('__WHATSAPP_CHAT_LINK__', '_blank');
    hideWhatsAppModal();
}

function shareResultsOnWhatsApp() {
    window.open('__WHATSAPP_SHARE_LINK__', '_blank');
    hideWhatsAppModal();
}
</script>
""", unsafe_allow_html=True)

# App header with icon
st.markdown("<h1 class='main-header'>🩺 NurtureAI: Health Assistant</h1>", unsafe_allow_html=True)

# Track if we have analysis results to share
has_analysis_results = False
analysis_text = ""

# Sidebar
with st.sidebar:
    st.image("https://i.imgur.com/jQrTAdQ.png", width=100)  # Replace with your logo
    
    st.markdown("### About NurtureAI")
    st.write("NurtureAI helps you make informed health decisions by analyzing products for safety concerns during pregnancy, breastfeeding, and for general use.")
    
    st.markdown("### How to use")
    st.markdown("""
    1. Select a category
    2. Choose your user type
    3. Upload an image
    4. Ask any specific questions
    5. Click 'Analyze Now'
    """)
    
    # Chat with NurtureAI on WhatsApp
    st.markdown("### Chat with us")
    whatsapp_chat_link = get_whatsapp_chat_link()
    st.markdown(f"""
    <a href="{whatsapp_chat_link}" target="_blank" class="whatsapp-button">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
        </svg>
        Chat with NurtureAI
    </a>
    """, unsafe_allow_html=True)
    
    st.markdown("### Disclaimer")
    st.info("This app provides general information and is not a substitute for professional medical advice.")
    
    # Version info
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #A0AEC0;'>Version 2.2</div>", unsafe_allow_html=True)

# Main layout with columns
col1, col2 = st.columns([3, 2])

with col1:
    # Category selection with icons
    st.markdown("<div class='category-card'>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Step 1: Choose a Category</p>", unsafe_allow_html=True)
    
    mode = st.radio(
        "Select what you want to analyze:",
        (
            "🍎 Food Safety Checker", 
            "💊 Drug/Medicine Safety Checker", 
            "🧴 Cosmetic Product Safety Checker",
            "🔢 Check Calories"
        ),
        key="category"
    )
    
    # Display category description based on selection
    if "Food" in mode:
        st.markdown("Analyze food products, ingredients, supplements, and beverages for safety.")
    elif "Drug" in mode:
        st.markdown("Check medications, over-the-counter drugs, and supplements for safety concerns.")
    elif "Cosmetic" in mode:
        st.markdown("Evaluate skincare, makeup, and personal care products for harmful ingredients.")
    elif "Calories" in mode:
        st.markdown("Calculate total calories and get nutritional breakdown of food items in your image.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # User type selection (hide for calorie checker)
    if "Calories" not in mode:
        st.markdown("<div class='user-type-card'>", unsafe_allow_html=True)
        st.markdown("<p class='sub-header'>Step 2: Select User Type</p>", unsafe_allow_html=True)
        
        user_type = st.selectbox(
            "Are you a healthcare/medical professional?",
            ("No, I am a regular user", "Yes, I am a healthcare professional")
        )
        
        # Explanation of different outputs
        if user_type == "No, I am a regular user":
            st.markdown("You'll receive simplified explanations with essential safety information.")
        else:
            st.markdown("You'll receive more detailed, technical information with clinical references.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Set a default user type for calorie checker
        user_type = "No, I am a regular user"
    
    # Image upload section
    st.markdown("<div class='upload-card'>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Step 3: Upload Image</p>", unsafe_allow_html=True)
    
    # Get category name for upload prompt
    if "Food" in mode:
        category_name = "food item"
    elif "Drug" in mode or "Medicine" in mode:
        category_name = "medicine/drug"
    elif "Cosmetic" in mode:
        category_name = "cosmetic product"
    elif "Calories" in mode:
        category_name = "meal or food items"
    
    uploaded_file = st.file_uploader(f"Upload an image of the {category_name}", type=["jpg", "jpeg", "png"])
    
    # Specific question
    st.markdown("<p class='sub-header'>Step 4: Ask a Specific Question (Optional)</p>", unsafe_allow_html=True)
    
    # Different placeholder text based on category
    placeholder_text = ""
    if "Food" in mode:
        placeholder_text = "E.g., Is this safe during the first trimester of pregnancy?"
    elif "Drug" in mode:
        placeholder_text = "E.g., Can I take this while breastfeeding?"
    elif "Cosmetic" in mode:
        placeholder_text = "E.g., Are there any harmful ingredients for sensitive skin?"
    elif "Calories" in mode:
        placeholder_text = "E.g., How does this compare to my daily caloric needs?"
    
    user_input = st.text_input("Your question:", placeholder=placeholder_text, key="input")
    
    # Submit button
    st.markdown("<p class='sub-header'>Step 5: Get Analysis</p>", unsafe_allow_html=True)
    submit = st.button("🔍 Check Now")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    # Preview area
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.markdown("<p class='sub-header'>Preview</p>", unsafe_allow_html=True)
        st.markdown("<div class='upload-preview'>", unsafe_allow_html=True)
        st.image(image, caption=f"Uploaded {category_name}", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<p class='sub-header'>Preview</p>", unsafe_allow_html=True)
        # Dark mode preview box
        st.markdown("""
        <div style="background-color:#2D3748; padding:2rem; border-radius:10px; text-align:center; height:300px; display:flex; flex-direction:column; justify-content:center; align-items:center; border:1px dashed #63B3ED;">
            <div style="font-size:3rem; margin-bottom:1rem;">📸</div>
            <h3 style="color:#E2E8F0;">Upload an Image</h3>
            <p style="color:#CBD5E0;">Please upload an image to analyze</p>
        </div>
        """, unsafe_allow_html=True)

# PROMPTS for each type
food_prompt_regular = """
You are a professional nutritionist advising a regular user.

TASK:
- Is the food product safe for pregnant women, breastfeeding mothers, babies, or general users?
- Highlight major concerns: allergens, high sugar/salt/fat, additives.
- Be brief and simple (2-4 sentences).
- Only mention risks if medically confirmed (WHO, Mayo Clinic).
- Suggest healthier alternatives if needed.

Always end with:
"⚠️ Please consult a healthcare professional for personalized advice."
"""

food_prompt_pro = """
You are a clinical nutritionist advising a healthcare professional.

TASK:
- Provide nutritional breakdown (macros and calories if visible).
- Highlight food safety issues (allergens, additives, unsafe preservatives).
- Reference scientific studies if applicable.
- Keep it concise but professional (around 6-8 sentences).
- Recommend evidence-based alternatives if unhealthy.

Always end with:
"⚠️ Please consult a healthcare professional for personalized advice."
"""

drug_prompt_regular = """
You are a pharmacist helping a regular user.

TASK:
- State if the drug/medicine is safe or NOT safe for pregnant women, breastfeeding mothers, children.
- Warn about dangerous ingredients (e.g., isotretinoin, warfarin, NSAIDs during pregnancy).
- Keep it brief and simple (2-4 sentences).

Example Output:
✅ Safe. OR ❌ Not Safe - Contains [ingredient] which may cause [issue].

Always end with:
"⚠️ Please consult a healthcare professional for personalized advice."
"""

drug_prompt_pro = """
You are a clinical pharmacist advising a healthcare professional.

TASK:
- Analyze active ingredients and contraindications during pregnancy, lactation, and for pediatric use.
- Provide pharmacological warnings and cite regulatory guidance (FDA Pregnancy Categories, WHO, PubMed).
- Keep it detailed but compact (6-8 sentences).

Always end with:
"⚠️ Please consult a healthcare professional for personalized advice."
"""

cosmetic_prompt_regular = """
You are a dermatologist helping a regular user.

TASK:
- Say if the cosmetic product is safe for pregnant women, breastfeeding mothers, babies, or sensitive users.
- Highlight harmful chemicals (parabens, hydroquinone, mercury, retinoids, etc.)
- Be simple and concise (2-4 sentences).

Example Output:
✅ Safe. OR ❌ Not Safe - Contains [ingredient] that may cause [harm].

Always end with:
"⚠️ Please consult a healthcare professional for personalized advice."
"""

cosmetic_prompt_pro = """
You are a dermatopharmacologist helping a healthcare professional.

TASK:
- Analyze cosmetic product ingredients scientifically for toxicity, allergenicity, and pregnancy risk.
- Cite evidence-based resources (EWG, FDA, WHO, PubMed).
- Keep it professional and concise (6-8 sentences).

Always end with:
"⚠️ Please consult a healthcare professional for personalized advice."
"""

# NEW PROMPT for calorie checking
calorie_prompt = """
You are an expert nutritionist analyzing food items from an image.

TASK:
- Identify all visible food items in the image.
- Calculate the approximate calories for each item.
- Provide a detailed breakdown in this exact format:
  1. Item 1 - X calories
  2. Item 2 - X calories
  (continue for all items)
- Calculate and show the total calories.
- Include a brief nutritional assessment (1-2 sentences).
- If portions are unclear, base calculations on standard serving sizes.

Always end with:
"⚠️ Please consult a healthcare professional for personalized advice."
"""

# Handle submission and display results
if submit:
    try:
        if uploaded_file is None:
            st.error("⚠️ Please upload an image to analyze")
        else:
            # Show spinner while processing
            with st.spinner("Analyzing image... Please wait"):
                image_data = input_image_setup(uploaded_file)

                # Clean mode string to get just the category
                clean_mode = mode.split(" ")[0] if " " in mode else mode

                # Select correct prompt
                if "Food" in mode:
                    input_prompt = food_prompt_regular if user_type == "No, I am a regular user" else food_prompt_pro
                elif "Drug" in mode or "Medicine" in mode:
                    input_prompt = drug_prompt_regular if user_type == "No, I am a regular user" else drug_prompt_pro
                elif "Cosmetic" in mode:
                    input_prompt = cosmetic_prompt_regular if user_type == "No, I am a regular user" else cosmetic_prompt_pro
                elif "Calories" in mode:
                    input_prompt = calorie_prompt

                # Get AI response
                response = get_gemini_response(input_prompt, image_data, user_input)

                # Always add disclaimer
                safe_response = ensure_medical_disclaimer(response)

                # Store result for sharing
                analysis_text = safe_response
                has_analysis_results = True

                # Get WhatsApp share link for the results
                whatsapp_share_link = get_whatsapp_share_link(f"NurtureAI Analysis Results for {category_name}:\n\n{safe_response}")

                # Display result with appropriate styling
                st.markdown("<div class='results-card'>", unsafe_allow_html=True)
                st.markdown("<h2 class='sub-header'>📝 Analysis Results</h2>", unsafe_allow_html=True)

                # Special formatting for calorie checker
                if "Calories" in mode:
                    formatted_response = safe_response
                    if "⚠️" in formatted_response:
                        parts = formatted_response.split("⚠️")
                        main_content = parts[0]
                        disclaimer = "⚠️" + parts[1]
                        st.markdown(main_content, unsafe_allow_html=True)
                        st.markdown(f"<div class='disclaimer-box'>{disclaimer}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(formatted_response, unsafe_allow_html=True)
                else:
                    formatted_response = safe_response
                    if "✅" in formatted_response:
                        formatted_response = formatted_response.replace("✅", "<span class='safe-tag'>✅ SAFE</span>")
                    if "❌" in formatted_response:
                        formatted_response = formatted_response.replace("❌", "<span class='unsafe-tag'>❌ NOT SAFE</span>")

                    if "⚠️" in formatted_response:
                        parts = formatted_response.split("⚠️")
                        main_content = parts[0]
                        disclaimer = "⚠️" + parts[1]
                        st.markdown(main_content, unsafe_allow_html=True)
                        st.markdown(f"<div class='disclaimer-box'>{disclaimer}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(formatted_response, unsafe_allow_html=True)

                # Add action buttons (Save, Share to WhatsApp)
                col_btn1, col_btn2, col_btn3 = st.columns(3)

                with col_btn1:
                    st.download_button(
                        label="💾 Save Results",
                        data=safe_response,
                        file_name=f"nurtureai_{category_name}_analysis.txt",
                        mime="text/plain"
                    )

                with col_btn2:
                    # WhatsApp share button
                    st.markdown(f"""
                        <a href="{whatsapp_share_link}" target="_blank" class="whatsapp-button">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M17.472 14.382c..."/>
                            </svg>
                            Share on WhatsApp
                        </a>
                    """, unsafe_allow_html=True)

                with col_btn3:
                    # WhatsApp chat button for follow-up
                    chat_link = get_whatsapp_chat_link()
                    st.markdown(f"""
                        <a href="{chat_link}" target="_blank" class="whatsapp-button" style="background-color: #128C7E;">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M17.472 14.382c..."/>
                            </svg>
                            Chat with Expert
                        </a>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

                # Add a footer with additional information
                st.markdown("<div class='footer'>", unsafe_allow_html=True)
                st.markdown("""
                    <div>
                        © 2025 NurtureAI | All rights reserved.
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
