#!/usr/bin/env python3
"""
Railway Deployment Script
Run this in Railway console after deployment to set up the database
"""

import os
import sys

def main():
    print("🚀 Railway Deployment Script")
    print("=" * 40)
    
    # Check environment
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        print(f"✅ Found DATABASE_URL: {database_url[:30]}...")
        print("🌐 This is a deployment environment")
        
        # Try to run the main app initialization
        try:
            print("\n📦 Initializing database through app...")
            from app import init_database
            if init_database():
                print("✅ Database initialized successfully!")
            else:
                print("❌ Database initialization failed")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("\n🔄 Trying alternative setup...")
            
            # Try to run setup_postgres.py
            try:
                from setup_postgres import create_postgres_tables
                if create_postgres_tables():
                    print("✅ PostgreSQL tables created successfully!")
                else:
                    print("❌ PostgreSQL setup failed")
            except Exception as e2:
                print(f"❌ PostgreSQL setup error: {e2}")
                print("\n💡 Try running manually:")
                print("   python setup_postgres.py")
    else:
        print("❌ No DATABASE_URL found")
        print("🔧 This appears to be a local environment")
        print("💡 Run: python setup_railway.py")
    
    print("\n" + "=" * 40)
    print("🎯 Next steps:")
    print("1. Check your app URL")
    print("2. Verify all pages load without errors")
    print("3. Check Railway logs for any issues")

if __name__ == "__main__":
    main()
