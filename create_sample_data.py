import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vote4all.settings')
django.setup()

from django.contrib.auth.models import User
from voting.models import Party, Candidate, Voter, DigiLockerUser

def create_sample_data():
    # Create parties
    parties_data = [
        {'name': 'Bharatiya Janata Party', 'symbol_path': 'static/images/Political_parties_symbols/BJP.jpg'},
        {'name': 'Indian National Congress', 'symbol_path': 'static/images/Political_parties_symbols/INC.png'},
        {'name': 'Aam Aadmi Party', 'symbol_path': 'static/images/Political_parties_symbols/AAP.png'},
        {'name': 'All India Trinamool Congress', 'symbol_path': 'static/images/Political_parties_symbols/TMC.png'},
        {'name': 'Janata Dal (United)', 'symbol_path': 'static/images/Political_parties_symbols/JDU.png'},
        {'name': 'Shiv Sena', 'symbol_path': 'static/images/Political_parties_symbols/SS.jpg'},
    ]
    
    for party_data in parties_data:
        party, created = Party.objects.get_or_create(
            name=party_data['name'],
            defaults={'symbol': party_data['symbol_path']}
        )
        if created:
            print(f"Created party: {party.name}")
    
    # Create candidates
    candidates_data = [
        # Default Constituency candidates
        {'name': 'Narendra Modi', 'party': 'Bharatiya Janata Party', 'photo_path': 'static/images/Political_parties_candidates/Modi.jpg', 'constituency': 'Default Constituency'},
        {'name': 'Rahul Gandhi', 'party': 'Indian National Congress', 'photo_path': 'static/images/Political_parties_candidates/Gandhi.jpg', 'constituency': 'Default Constituency'},
        {'name': 'Arvind Kejriwal', 'party': 'Aam Aadmi Party', 'photo_path': 'static/images/Political_parties_candidates/Kejriwal.jpg', 'constituency': 'Default Constituency'},
        
        # Mumbai Central candidates
        {'name': 'Mamata Banerjee', 'party': 'All India Trinamool Congress', 'photo_path': 'static/images/Political_parties_candidates/Mamata.jpg', 'constituency': 'Mumbai Central'},
        {'name': 'Nitish Kumar', 'party': 'Janata Dal (United)', 'photo_path': 'static/images/Political_parties_candidates/Nitish.jpg', 'constituency': 'Mumbai Central'},
        
        # Delhi North candidates
        {'name': 'Uddhav Thackeray', 'party': 'Shiv Sena', 'photo_path': 'static/images/Political_parties_candidates/Udd.jpg', 'constituency': 'Delhi North'},
        {'name': 'Akhilesh Yadav', 'party': 'Bharatiya Janata Party', 'photo_path': 'static/images/Political_parties_candidates/Modi.jpg', 'constituency': 'Delhi North'},
        
        # Bangalore South candidates
        {'name': 'Priyanka Gandhi', 'party': 'Indian National Congress', 'photo_path': 'static/images/Political_parties_candidates/Gandhi.jpg', 'constituency': 'Bangalore South'},
        {'name': 'Manish Sisodia', 'party': 'Aam Aadmi Party', 'photo_path': 'static/images/Political_parties_candidates/Kejriwal.jpg', 'constituency': 'Bangalore South'},
        
        # Chennai Central candidates
        {'name': 'Tejashwi Yadav', 'party': 'Janata Dal (United)', 'photo_path': 'static/images/Political_parties_candidates/Nitish.jpg', 'constituency': 'Chennai Central'},
        {'name': 'Aditya Thackeray', 'party': 'Shiv Sena', 'photo_path': 'static/images/Political_parties_candidates/Udd.jpg', 'constituency': 'Chennai Central'},
    ]
    
    for candidate_data in candidates_data:
        try:
            party = Party.objects.get(name=candidate_data['party'])
            candidate, created = Candidate.objects.get_or_create(
                name=candidate_data['name'],
                party=party,
                constituency=candidate_data['constituency'],
                defaults={
                    'photo': candidate_data['photo_path']
                }
            )
            if created:
                print(f"Created candidate: {candidate.name}")
        except Party.DoesNotExist:
            print(f"Party not found: {candidate_data['party']}")
    
    # Create sample voters
    sample_voters = [
        # Regular test voters
        {'username': 'voter1', 'voter_id': 'ABC1234567', 'constituency': 'Default Constituency', 'phone': '9876543210'},
        {'username': 'voter2', 'voter_id': 'DEF9876543', 'constituency': 'Default Constituency', 'phone': '9876543211'},
        {'username': 'testvoter', 'voter_id': 'TEST123456', 'constituency': 'Default Constituency', 'phone': '9876543212'},
        
        # Specific test users for DigiLocker login (can be found by mobile/username/voter_id)
        {'username': 'digilocker_user', 'voter_id': 'DIGI123456', 'constituency': 'Mumbai Central', 'phone': '9123456789'},
        {'username': 'john_doe', 'voter_id': 'JOHN789012', 'constituency': 'Delhi North', 'phone': '9234567890'},
        
        # Additional DigiLocker test users (mobile number as voter ID for testing)
        {'username': '9123456789', 'voter_id': '9123456789', 'constituency': 'Mumbai Central', 'phone': '9123456789'},
        {'username': '9234567890', 'voter_id': '9234567890', 'constituency': 'Delhi North', 'phone': '9234567890'},
        
        # Aadhaar-style test users (12-digit numbers)
        {'username': 'aadhaar_user1', 'voter_id': '123456789012', 'constituency': 'Mumbai Central', 'phone': '9123456789'},
        {'username': 'aadhaar_user2', 'voter_id': '987654321098', 'constituency': 'Delhi North', 'phone': '9234567890'},
        
        # Specific test users for Voter ID login  
        {'username': 'voterid_user', 'voter_id': 'VOTE456789', 'constituency': 'Bangalore South', 'phone': '9345678901'},
        {'username': 'jane_smith', 'voter_id': 'JANE345678', 'constituency': 'Chennai Central', 'phone': '9456789012'},
    ]
    
    for voter_data in sample_voters:
        try:
            user, created = User.objects.get_or_create(
                username=voter_data['username'],
                defaults={'email': f"{voter_data['username']}@example.com"}
            )
            if created:
                user.set_password('password123')
                user.save()
                print(f"Created user: {user.username}")
            
            voter, created = Voter.objects.get_or_create(
                user=user,
                voter_id=voter_data['voter_id'],
                defaults={
                    'constituency': voter_data['constituency'],
                    'phone_number': voter_data.get('phone', ''),
                    'date_of_birth': None  # You can set specific dates if needed
                }
            )
            if created:
                print(f"Created voter: {voter.voter_id}")
        except Exception as e:
            print(f"Error creating voter {voter_data['username']}: {e}")

    # Create sample DigiLocker users
    digilocker_users_data = [
        {
            'full_name': 'Amit Sharma',
            'mobile_number': '9123456789',
            'date_of_birth': '1990-05-15',
            'gender': 'male',
            'security_pin': '123456',
            'aadhaar_number': '123456789012',
            'username': 'amit_sharma'
        },
        {
            'full_name': 'Priya Singh',
            'mobile_number': '9234567890',
            'date_of_birth': '1985-08-22',
            'gender': 'female',
            'security_pin': '654321',
            'aadhaar_number': '987654321098',
            'username': 'priya_singh'
        },
        {
            'full_name': 'Rajesh Kumar',
            'mobile_number': '9345678901',
            'date_of_birth': '1992-12-10',
            'gender': 'male',
            'security_pin': '111111',
            'aadhaar_number': None,
            'username': 'rajesh_kumar'
        },
        {
            'full_name': 'Sunita Devi',
            'mobile_number': '9456789012',
            'date_of_birth': '1988-03-18',
            'gender': 'female',
            'security_pin': '222222',
            'aadhaar_number': '456789012345',
            'username': None
        },
        {
            'full_name': 'Mobile Only User',
            'mobile_number': '9567890123',
            'date_of_birth': '1995-07-25',
            'gender': 'male',
            'security_pin': '333333',
            'aadhaar_number': None,
            'username': None
        }
    ]
    
    for user_data in digilocker_users_data:
        try:
            # Parse date string to date object
            dob_str = user_data['date_of_birth']
            from datetime import datetime
            date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            
            digilocker_user, created = DigiLockerUser.objects.get_or_create(
                mobile_number=user_data['mobile_number'],
                defaults={
                    'full_name': user_data['full_name'],
                    'date_of_birth': date_of_birth,
                    'gender': user_data['gender'],
                    'security_pin': user_data['security_pin'],
                    'aadhaar_number': user_data['aadhaar_number'],
                    'username': user_data['username'],
                    'is_verified': True
                }
            )
            
            if created:
                print(f"Created DigiLocker user: {digilocker_user.full_name}")
                
                # Try to link with existing voter if possible
                voter = None
                if user_data['aadhaar_number']:
                    voter = Voter.objects.filter(voter_id=user_data['aadhaar_number']).first()
                if not voter and user_data['mobile_number']:
                    voter = Voter.objects.filter(phone_number=user_data['mobile_number']).first()
                if not voter and user_data['username']:
                    voter = Voter.objects.filter(user__username=user_data['username']).first()
                
                if voter:
                    digilocker_user.linked_voter = voter
                    digilocker_user.save()
                    print(f"  → Linked to voter: {voter.voter_id}")
                    
        except Exception as e:
            print(f"Error creating DigiLocker user {user_data['full_name']}: {e}")

if __name__ == '__main__':
    create_sample_data()
    print("Sample data creation completed!")
    print("\n" + "="*60)
    print("TEST USER CREDENTIALS")
    print("="*60)
    print("\n🔐 FOR DIGILOCKER LOGIN:")
    print("   Mobile Tab: 9123456789 | PIN: 123456")
    print("   Mobile Tab: 9234567890 | PIN: 654321") 
    print("   Mobile Tab: 9345678901 | PIN: 111111")
    print("   Mobile Tab: 9456789012 | PIN: 222222")
    print("   Mobile Tab: 9567890123 | PIN: 333333")
    print("   Username Tab: amit_sharma | PIN: 123456")
    print("   Username Tab: priya_singh | PIN: 654321")
    print("   Username Tab: rajesh_kumar | PIN: 111111")
    print("   Aadhaar Tab: 123456789012 | PIN: 123456")
    print("   Aadhaar Tab: 987654321098 | PIN: 654321")
    print("   Aadhaar Tab: 456789012345 | PIN: 222222")
    
    print("\n📱 FOR DIGILOCKER SIGNUP:")
    print("   Try creating new accounts with any 10-digit mobile number")
    print("   Set any 6-digit PIN and fill required details")
    print("   Optional: Add 12-digit Aadhaar or custom username")
    
    print("\n🗳️  FOR VOTER ID LOGIN:")
    print("   Voter ID: VOTE456789 | Phone: 9345678901")
    print("   Voter ID: JANE345678 | Phone: 9456789012")
    print("   Voter ID: DIGI123456 | Phone: 9123456789")
    print("   Voter ID: JOHN789012 | Phone: 9234567890")
    
    print("\n📍 CONSTITUENCIES:")
    print("   9123456789, DIGI123456, 123456789012 → Mumbai Central")
    print("   9234567890, JOHN789012, 987654321098 → Delhi North") 
    print("   VOTE456789 → Bangalore South")
    print("   JANE345678 → Chennai Central")
    
    print("\n💡 All users have password: 'password123'")
    print("="*60)
