#!/usr/bin/env python3
"""
Test script to verify PostgreSQL setup and database operations
"""

import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
sys.path.insert(0, '/Users/praachirasane/Desktop/VOTE4ALL 4')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vote4all.settings')
django.setup()

from django.db import connection
from voting.models import Party, Candidate, Voter, RegisteredUser

def test_database_connection():
    """Test PostgreSQL database connection"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ PostgreSQL connection successful!")
            print(f"   Database version: {version[0]}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_model_operations():
    """Test basic model operations"""
    try:
        # Test Party model
        party_count = Party.objects.count()
        print(f"✅ Parties in database: {party_count}")
        
        # Test Candidate model
        candidate_count = Candidate.objects.count()
        print(f"✅ Candidates in database: {candidate_count}")
        
        # Test Voter model
        voter_count = Voter.objects.count()
        print(f"✅ Voters in database: {voter_count}")
        
        # Test RegisteredUser model
        registered_count = RegisteredUser.objects.count()
        print(f"✅ Registered users in database: {registered_count}")
        
        # Show some sample data
        if party_count > 0:
            print("\n📋 Sample Parties:")
            for party in Party.objects.all()[:3]:
                print(f"   - {party.name}")
        
        if candidate_count > 0:
            print("\n📋 Sample Candidates:")
            for candidate in Candidate.objects.select_related('party').all()[:3]:
                print(f"   - {candidate.name} ({candidate.party.name}) - {candidate.constituency}")
        
        if voter_count > 0:
            print("\n📋 Sample Voters:")
            for voter in Voter.objects.select_related('user').all()[:3]:
                print(f"   - {voter.user.get_full_name()} (ID: {voter.voter_id}) - {voter.constituency}")
        
        return True
    except Exception as e:
        print(f"❌ Model operation failed: {e}")
        return False

def main():
    print("🔍 Testing PostgreSQL Setup for VOTE4ALL")
    print("=" * 50)
    
    # Test database connection
    if not test_database_connection():
        return
    
    print()
    
    # Test model operations
    if not test_model_operations():
        return
    
    print()
    print("🎉 All tests passed! Your PostgreSQL setup is working correctly.")
    print()
    print("📝 Next steps:")
    print("   1. Run: python3 manage.py runserver")
    print("   2. Visit: http://localhost:8000")
    print("   3. Register new users through the website")
    print("   4. Users will be automatically approved after phone verification")
    print()
    print("🔧 Admin access:")
    print("   - URL: http://localhost:8000/admin")
    print("   - Username: praachirasane")
    print("   - Password: [your admin password]")

if __name__ == "__main__":
    main()
