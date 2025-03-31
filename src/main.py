import os
import mysql.connector
import groq  # Import Groq API client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Manually fetch and validate API key
api_key = "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"
if not api_key:
    raise ValueError("❌ GROQ_API_KEY is missing! Please set it in the environment variables or .env file.")

try:
    groq_client = groq.Client(api_key=api_key)  # Initialize Groq API Client
except Exception as e:
    raise RuntimeError(f"❌ Failed to initialize Groq API client: {e}")

class DatabaseManager:
    def __init__(self):
        try:
            # Database connection configuration
            self.connection_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'user': os.getenv('DB_USER', 'root'),  # Default to 'root' if not set
                'password': os.getenv('DB_PASSWORD', 'Balu@SQL1234'),  # Default password
                'database': os.getenv('DB_NAME', 'language_learning_db'),
                'auth_plugin': 'mysql_native_password'  # Ensure correct authentication
            }

            print("\n📡 Attempting to connect with:")
            print(f"   🔹 Host: {self.connection_config['host']}")
            print(f"   🔹 User: {self.connection_config['user']}")
            print(f"   🔹 Database: {self.connection_config['database']}")

            self.connection = mysql.connector.connect(**self.connection_config)
            self.cursor = self.connection.cursor(dictionary=True)

            self.create_tables()
            print("✅ Database connection successful!\n")

        except mysql.connector.Error as err:
            print("❌ MySQL Connection Error:", err)
            raise

    def create_tables(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_name VARCHAR(100),
                    learning_language VARCHAR(50),
                    native_language VARCHAR(50),
                    proficiency_level VARCHAR(20)
                )
            ''')

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS language_mistakes (
                    mistake_id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id INT,
                    mistake_type VARCHAR(50),
                    mistake_description TEXT,
                    correction TEXT,
                    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id)
                )
            ''')
            self.connection.commit()
            print("✅ Tables ensured in the database.")

        except mysql.connector.Error as err:
            print("❌ Error creating tables:", err)
            raise

    def close_connection(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("🔴 Database connection closed.")

class LanguageLearningChatbot:
    def generate_response(self, prompt):
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",  # Using Mixtral model
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Error generating response from Groq API: {e}")
            return "Sorry, I'm having trouble responding right now."

def main():
    chatbot = LanguageLearningChatbot()

    try:
        print("\n🗣️ Starting Language Learning Session...")
        prompt = "Hello, how can I improve my Spanish?"
        bot_response = chatbot.generate_response(prompt)
        print(f"\n🤖 Bot: {bot_response}\n")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == '__main__':
    main()
