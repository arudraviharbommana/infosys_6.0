#!/usr/bin/env python3
"""
Secure Environment Configuration for Resume Matcher
This script helps set up environment variables securely
"""

import os
import sys
import getpass
from pathlib import Path

def create_env_file():
    """Create .env file with user input"""
    backend_dir = Path(__file__).parent
    env_file = backend_dir / '.env'
    env_template = backend_dir / '.env.template'
    
    if env_file.exists():
        response = input("🔒 .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled.")
            return False
    
    print("🔧 Setting up environment variables...")
    print("📝 Please provide the following configuration:")
    
    # Required fields
    langsmith_key = getpass.getpass("🔑 LangSmith API Key: ")
    openai_key = getpass.getpass("🤖 OpenAI API Key: ")
    
    # Optional fields
    print("\n🌟 Optional configurations (press Enter to skip):")
    anthropic_key = getpass.getpass("🧠 Anthropic API Key (optional): ")
    google_key = getpass.getpass("🔍 Google API Key (optional): ")
    
    # Generate secret key
    import secrets
    secret_key = secrets.token_urlsafe(32)
    
    # Create .env content
    env_content = f"""# LangSmith Configuration (Required for LangGraph)
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY={langsmith_key}
LANGSMITH_PROJECT=resume-matcher-{secrets.token_hex(4)}

# OpenAI Configuration (Required for LLM)
OPENAI_API_KEY={openai_key}

# Optional: Alternative LLM Providers
{f'ANTHROPIC_API_KEY={anthropic_key}' if anthropic_key else '# ANTHROPIC_API_KEY=your_anthropic_api_key_here'}
{f'GOOGLE_API_KEY={google_key}' if google_key else '# GOOGLE_API_KEY=your_google_api_key_here'}

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY={secret_key}

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Security Settings
RATE_LIMIT_PER_MINUTE=60
MAX_FILE_SIZE_MB=10

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
"""
    
    # Write to .env file
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        # Set secure permissions (readable only by owner)
        os.chmod(env_file, 0o600)
        
        print(f"✅ Environment file created: {env_file}")
        print("🔒 File permissions set to 600 (owner read/write only)")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def validate_env():
    """Validate environment variables"""
    required_vars = [
        'LANGSMITH_API_KEY',
        'OPENAI_API_KEY',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def setup_logging():
    """Setup logging directory"""
    backend_dir = Path(__file__).parent
    logs_dir = backend_dir / 'logs'
    
    try:
        logs_dir.mkdir(exist_ok=True)
        print(f"✅ Logging directory created: {logs_dir}")
        return True
    except Exception as e:
        print(f"❌ Error creating logs directory: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Resume Matcher Backend Setup")
    print("=" * 40)
    
    # Load existing .env if available
    backend_dir = Path(__file__).parent
    env_file = backend_dir / '.env'
    
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("📁 Loaded existing .env file")
        except ImportError:
            print("⚠️ python-dotenv not installed. Run: pip install python-dotenv")
    
    # Setup steps
    steps = [
        ("Create environment file", create_env_file),
        ("Setup logging directory", setup_logging),
        ("Validate configuration", validate_env)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📚 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run the application: python app.py")
    print("3. Visit: http://localhost:5000")
    
    print("\n⚠️ Security Notes:")
    print("- Never commit your .env file to version control")
    print("- Keep your API keys secure and rotate them regularly")
    print("- Use environment variables in production")

if __name__ == "__main__":
    main()