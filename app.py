import streamlit as st
import logging
from src.database import DatabaseManager
from src.chatbot import LanguageLearningChatbot

def configure_logging():
    """Configure application-wide logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app_log.txt', mode='a')
        ]
    )

def main():
    # Configure logging
    configure_logging()
    logger = logging.getLogger(__name__)

    # Page configuration
    st.set_page_config(
        page_title="Language Learning Companion", 
        page_icon="🌍",
        layout="wide"
    )

    st.title("🌍 Language Learning Companion")

    # Enhanced sidebar configuration
    st.sidebar.header("🔧 System Configuration")
    
    # Database Configuration Inputs
    st.sidebar.subheader("💾 Database Connection")
    db_config = {
        "host": st.sidebar.text_input("Database Host", value="localhost", key="db_host"),
        "user": st.sidebar.text_input("Database Username", value="root", key="db_user"),
        "password": st.sidebar.text_input("Database Password", type="password", key="db_password"),
        "database": st.sidebar.text_input("Database Name", value="language_learning_db", key="db_name")
    }

    # AI Configuration
    st.sidebar.subheader("🤖 AI Configuration")
    gemini_api_key = st.sidebar.text_input(
        "Gemini API Key", 
        type="password", 
        key="gemini_api_key",
        help="Get your API key from Google AI Studio"
    )

    # Initialize components with error handling
    try:
        # Initialize Chatbot
        chatbot = LanguageLearningChatbot(api_key=gemini_api_key)
        
        # Initialize Database
        db_manager = DatabaseManager(**db_config)
    except Exception as e:
        st.error(f"Initialization Error: {e}")
        logger.error(f"System initialization failed: {e}")
        return

    # Language configuration
    languages = chatbot.SUPPORTED_LANGUAGES
    levels = ['Beginner', 'Intermediate', 'Advanced']

    # Main learning interface
    st.header("🚀 Start Your Language Learning Journey")

    # User input form with enhanced validation
    with st.form("language_form"):
        st.write("### 📝 Personal Learning Profile")
        name = st.text_input("Your Name", key="user_name", help="Enter your full name")
        native_lang = st.text_input("Native Language", key="native_language", help="What is your first language?")
        
        col1, col2 = st.columns(2)
        with col1:
            learn_lang = st.selectbox("Language to Learn", languages, key="learning_language")
        with col2:
            proficiency = st.selectbox("Proficiency Level", levels, key="proficiency_level")
        
        submit = st.form_submit_button("Start Learning")

    # Process form submission
    if submit:
        # Comprehensive validation
        if not all([name, native_lang, gemini_api_key]):
            st.warning("Please fill in all fields and provide a valid API key")
        else:
            try:
                # Save session to database
                session_id = db_manager.create_session(
                    name, learn_lang, native_lang, proficiency
                )
                
                # Generate conversation scenario
                conversation = chatbot.generate_conversation_scene(learn_lang, proficiency)
                
                # Display results
                st.success(f"Welcome, {name}! Let's learn {learn_lang}")
                st.subheader(f"{learn_lang} Learning Scenario")
                st.write(conversation)
            
            except Exception as e:
                st.error(f"Error processing your request: {e}")
                logger.error(f"Learning session error: {e}")

    # Sessions overview
    st.sidebar.subheader("📊 Learning Sessions")
    if st.sidebar.button("View Sessions"):
        sessions = db_manager.get_sessions(limit=50)
        st.dataframe(sessions)

if __name__ == "__main__":
    main()