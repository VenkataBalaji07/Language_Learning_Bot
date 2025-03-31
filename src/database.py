import mysql.connector
import pandas as pd
import streamlit as st
import logging
from datetime import datetime

class DatabaseManager:
    def __init__(self, host='localhost', user='root', password='Tulasi', database='language_learning_db'):
        """
        Enhanced database connection initialization with comprehensive logging
        
        Args:
            host (str): Database host
            user (str): Database username
            password (str): Database password
            database (str): Database name
        """
        # Configure advanced logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('database_log.txt', mode='a')
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Connection parameters validation
        if not all([host, user, database]):
            self.logger.error("Invalid database connection parameters")
            st.error("Database connection parameters are incomplete")
            self.connection = None
            self.cursor = None
            return

        try:
            # Establish connection with timeout
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                connection_timeout=10  # 10 seconds timeout
            )
            self.cursor = self.connection.cursor(dictionary=True)
            
            # Create tables if not exists
            self._create_tables()
            
            self.logger.info(f"Successfully connected to database: {database}")
            
        except mysql.connector.Error as err:
            error_msg = f"Database Connection Error: {err}"
            self.logger.error(error_msg)
            st.error(error_msg)
            self.connection = None
            self.cursor = None

    def _create_tables(self):
        """
        Robust table creation with comprehensive error handling
        """
        if not self.connection:
            return

        try:
            # Updated table creation SQL to match the insert query
            create_sessions_table = '''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_name VARCHAR(100) NOT NULL,
                learning_language VARCHAR(50) NOT NULL,
                native_language VARCHAR(50) NOT NULL,
                proficiency_level VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_duration INT DEFAULT 0
            )
            '''
            
            self.cursor.execute(create_sessions_table)
            self.connection.commit()
            self.logger.info("Tables created/verified successfully")
            
        except mysql.connector.Error as err:
            error_msg = f"Error creating tables: {err}"
            self.logger.error(error_msg)
            st.error(error_msg)

    def create_session(self, user_name, learning_language, native_language, proficiency_level):
        """
        Enhanced session creation with comprehensive validation
        """
        if not self.connection:
            st.error("No active database connection")
            return None
        
        # Robust input validation
        if not all([user_name, learning_language, native_language, proficiency_level]):
            st.error("All fields are required for session creation")
            return None
        
        try:
            query = '''
            INSERT INTO user_sessions 
            (user_name, learning_language, native_language, proficiency_level) 
            VALUES (%s, %s, %s, %s)
            '''
            values = (user_name, learning_language, native_language, proficiency_level)
            
            self.cursor.execute(query, values)
            self.connection.commit()
            
            session_id = self.cursor.lastrowid
            self.logger.info(f"Session created for {user_name} with ID: {session_id}")
            return session_id
        
        except mysql.connector.Error as err:
            error_msg = f"Session Creation Error: {err}"
            self.logger.error(error_msg)
            st.error(error_msg)
            return None

    def get_sessions(self, limit=100):
        """
        Retrieve learning sessions with optional limit and error handling
        """
        if not self.connection:
            st.error("No active database connection")
            return pd.DataFrame()
        
        try:
            query = "SELECT * FROM user_sessions ORDER BY created_at DESC LIMIT %s"
            self.cursor.execute(query, (limit,))
            sessions = self.cursor.fetchall()
            
            return pd.DataFrame(sessions)
        
        except mysql.connector.Error as err:
            error_msg = f"Sessions Retrieval Error: {err}"
            self.logger.error(error_msg)
            st.error(error_msg)
            return pd.DataFrame()

    def close_connection(self):
        """
        Advanced method to safely close database connection
        """
        try:
            if self.connection and self.connection.is_connected():
                self.cursor.close()
                self.connection.close()
                self.logger.info("Database connection closed successfully")
        except Exception as e:
            error_msg = f"Error closing database connection: {e}"
            self.logger.error(error_msg)