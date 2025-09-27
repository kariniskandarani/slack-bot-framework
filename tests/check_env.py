"""
Simple script to check if .env variables are read correctly.
Run this script to test your environment setup.
"""

import os
from dotenv import load_dotenv

def check_env_variables():
    """Simple function to check if .env variables are loaded correctly."""
    
    print("🔍 Checking .env file...")
    
    # Load .env file
    load_dotenv()
    
    # Check required variables
    required_vars = ['bot_user_oauth_token', 'signing_secret']
    
    print("\n📋 Checking required variables:")
    all_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Don't print the actual value for security
            print(f"   ✅ {var}: Found (length: {len(value)} chars)")
        else:
            print(f"   ❌ {var}: Missing or empty")
            all_present = False
    
    print(f"\n🎯 Result:")
    if all_present:
        print("   ✅ All environment variables are present!")
        print("   🚀 Your .env file is configured correctly.")
        
        # Test the validation function
        try:
            # Import here to avoid issues if variables are missing
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            
            # We can't import app directly because it runs validation on import
            # So let's just recreate the validation logic
            missing_vars = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if not missing_vars:
                print("   ✅ Environment validation would pass!")
            else:
                print(f"   ❌ Environment validation would fail: {missing_vars}")
                
        except Exception as e:
            print(f"   ⚠️  Could not test validation function: {e}")
    else:
        print("   ❌ Some environment variables are missing!")
        print("   💡 Make sure your .env file contains:")
        print("      bot_user_oauth_token=your_bot_token_here")
        print("      signing_secret=your_signing_secret_here")
    
    return all_present

if __name__ == "__main__":
    success = check_env_variables()
    exit(0 if success else 1)