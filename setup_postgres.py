import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

def create_postgres_tables():
    """Create PostgreSQL tables for Railway deployment"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("DATABASE_URL environment variable not found!")
        print("Make sure you have set up PostgreSQL in Railway")
        return False
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("Connected to PostgreSQL successfully!")
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        ''')
        
        # Create categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                color VARCHAR(7) NOT NULL
            )
        ''')
        
        # Create blogs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blogs (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                likes INTEGER DEFAULT 0,
                dislikes INTEGER DEFAULT 0,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Create reviews table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id SERIAL PRIMARY KEY,
                blog_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (blog_id) REFERENCES blogs (id)
            )
        ''')
        
        # Create contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create visitors table for tracking page visits
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visitors (
                id SERIAL PRIMARY KEY,
                page TEXT NOT NULL,
                ip_address VARCHAR(45),
                user_agent TEXT,
                visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default admin user
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING', ('Hari', 'Life@123'))
        
        # Insert default categories with random colors
        default_categories = [
            ('Technology', '#3B82F6'),
            ('Lifestyle', '#10B981'),
            ('Travel', '#F59E0B'),
            ('Food', '#EF4444'),
            ('Health', '#8B5CF6')
        ]
        
        for name, color in default_categories:
            cursor.execute('INSERT INTO categories (name, color) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING', (name, color))
        
        conn.commit()
        conn.close()
        
        print("PostgreSQL tables created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating PostgreSQL tables: {e}")
        return False

if __name__ == '__main__':
    create_postgres_tables()
