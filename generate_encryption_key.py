"""
Generate encryption key for federated biometric authentication
Run this once and add the key to your .env file or settings.py

IMPORTANT: Keep this key SECRET and NEVER commit it to version control!
"""

from cryptography.fernet import Fernet

def generate_encryption_key():
    """Generate a new Fernet encryption key"""
    key = Fernet.generate_key()
    return key.decode()

if __name__ == '__main__':
    key = generate_encryption_key()
    print("\n" + "="*70)
    print("FEDERATED LEARNING BIOMETRIC ENCRYPTION KEY")
    print("="*70)
    print("\nGenerated Encryption Key:")
    print(f"\n{key}\n")
    print("="*70)
    print("\nIMPORTANT INSTRUCTIONS:")
    print("1. Copy the key above")
    print("2. Add it to your .env file as:")
    print(f"   BIOMETRIC_ENCRYPTION_KEY={key}")
    print("3. Update vote4all/settings.py to use:")
    print("   BIOMETRIC_ENCRYPTION_KEY = os.getenv('BIOMETRIC_ENCRYPTION_KEY')")
    print("4. NEVER commit this key to version control!")
    print("5. Keep it secure - losing it means biometric data cannot be decrypted")
    print("="*70 + "\n")
    
    # Save to a .env.example file for reference
    with open('.env.example', 'a') as f:
        f.write(f"\n# Federated Learning Biometric Encryption Key\n")
        f.write(f"# Generated on: {__import__('datetime').datetime.now()}\n")
        f.write(f"BIOMETRIC_ENCRYPTION_KEY={key}\n")
    
    print("✓ Also saved to .env.example file (copy to .env for use)\n")
