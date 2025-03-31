import os
import streamlit as st
import google.generativeai as genai
import logging

class LanguageLearningChatbot:
    SUPPORTED_LANGUAGES = [
        'Spanish', 'French', 'German', 
        'Italian', 'Portuguese', 'Chinese'
    ]

    def __init__(self, api_key=None):
        """
        Initialize chatbot with flexible API key management
        
        Args:
            api_key (str, optional): API key for Gemini
        """
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Priority for API key retrieval
        # 1. Passed parameter
        # 2. Streamlit secrets
        # 3. Environment variable
        # 4. User input
        if not api_key:
            # Check Streamlit secrets
            api_key = st.secrets.get("GEMINI_API_KEY") if hasattr(st.secrets, 'GEMINI_API_KEY') else None
        
        if not api_key:
            # Check environment variables
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            # Prompt user for API key with warning
            api_key = st.sidebar.text_input(
                "Enter Gemini API Key", 
                type="password", 
                help="API keys are sensitive. Use environment variables or Streamlit secrets for production."
            )
        
        # Debug and safety checks
        if not api_key:
            st.warning("No API key provided. Some functionalities will be limited.")
            self.model = None
            return

        try:
            # Configure generative AI
            genai.configure(api_key=api_key)
            
            # Model initialization with fallback mechanism
            model_names = [
                'gemini-1.5-pro-latest', 
                'gemini-1.5-flash-latest', 
                'gemini-pro'
            ]
            
            self.model = None
            for model_name in model_names:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    # Test model with a simple prompt
                    self.model.generate_content("Test connection")
                    st.success(f"Successfully initialized with model: {model_name}")
                    break
                except Exception as model_error:
                    self.logger.warning(f"Model {model_name} initialization failed: {model_error}")
            
            if not self.model:
                st.error("Could not initialize any Gemini model. Please check your API key.")
        
        except Exception as e:
            self.logger.error(f"Comprehensive Error initializing AI: {e}")
            st.error(f"Initialization Error: {e}")
            self.model = None

    def generate_conversation_scene(self, learning_language, proficiency_level):
        """
        Generate a contextual conversation scene with robust error handling
        
        Args:
            learning_language (str): Target language for learning
            proficiency_level (str): User's current language proficiency level
        
        Returns:
            str: Generated conversation scene or error message
        """
        if not self.model:
            st.warning("AI model not initialized. Please check your API key.")
            return "AI model not initialized. Please verify your Gemini API key."
        
        prompt = f"""
        Create a realistic conversation scenario in {learning_language} 
        for a {proficiency_level} language learner. 
        Provide:
        1. Scenario Context
        2. Dialogue Example (3-4 exchanges)
        3. Language Learning Objectives
        4. Key Vocabulary to Learn

        Scenario should be engaging and practical for language learning.
        Format:
        Scenario Context: [Brief description]
        Dialogue:
        Person A: [Dialogue in {learning_language}]
        Person B: [Response in {learning_language}]
        Learning Objectives:
        - [Objective 1]
        - [Objective 2]
        Key Vocabulary:
        - [Word/Phrase]: [Meaning]
        """
        
        try:
            generation_config = {
                'temperature': 0.7,
                'max_output_tokens': 600
            }
            
            response = self.model.generate_content(
                prompt, 
                generation_config=generation_config
            )
            
            # Enhanced error checking
            if not response or not response.text:
                st.warning("Unable to generate conversation. Please try again.")
                return "Unable to generate conversation. Please retry."
            
            return response.text
        
        except Exception as e:
            error_message = f"Error generating conversation: {str(e)}"
            self.logger.error(error_message)
            st.error(error_message)
            return error_message

    def analyze_user_input(self, user_input, learning_language):
        """
        Analyze user input for language learning with comprehensive feedback
        
        Args:
            user_input (str): User's input in the learning language
            learning_language (str): Target language being learned
        
        Returns:
            str: Detailed language learning analysis
        """
        if not self.model:
            st.warning("AI model not initialized. Please check your API key.")
            return "AI model not initialized. Please verify your Gemini API key."
        
        prompt = f"""
        Comprehensive Language Learning Analysis for {learning_language}:
        Input Sentence: {user_input}
        
        Provide a detailed analysis:
        1. Grammatical Corrections
        2. Detailed Error Explanations
        3. Suggested Improvements
        4. Corrected Sentence Version
        5. Language Learning Tips
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = f"Error analyzing input: {e}"
            self.logger.error(error_msg)
            st.error(error_msg)
            return f"Unable to analyze input. Please try again. Error: {e}"