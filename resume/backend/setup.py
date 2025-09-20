#!/usr/bin/env python3
"""
Setup script for Advanced Skill Matching Backend
Helps configure environment variables and test the setup
"""

import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install Python requirements."""
    print("📦 Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def setup_environment():
    """Setup environment variables."""
    print("\n🔧 Setting up environment variables...")
    
    env_file = Path(".env")
    example_file = Path(".env.example")
    
    if not env_file.exists():
        if example_file.exists():
            print("📋 Creating .env file from example...")
            with open(example_file, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ .env file created! Please edit it with your API keys.")
        else:
            print("❌ .env.example file not found!")
            return False
    else:
        print("✅ .env file already exists!")
    
    return True

def test_imports():
    """Test if all required packages can be imported."""
    print("\n🧪 Testing package imports...")
    
    packages = [
        "flask",
        "flask_cors", 
        "langchain",
        "langgraph",
        "langchain_openai",
        "langsmith",
        "openai",
        "fitz",  # PyMuPDF
        "rapidfuzz"
    ]
    
    failed_imports = []
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True

def check_api_keys():
    """Check if API keys are configured."""
    print("\n🔑 Checking API key configuration...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "LANGSMITH_API_KEY": os.getenv("LANGSMITH_API_KEY")
    }
    
    configured_keys = []
    missing_keys = []
    
    for key, value in api_keys.items():
        if value and value != "your-openai-api-key-here":
            configured_keys.append(key)
            print(f"✅ {key}: Configured")
        else:
            missing_keys.append(key)
            print(f"⚠️  {key}: Not configured")
    
    if missing_keys:
        print(f"\n⚠️  Missing API keys: {', '.join(missing_keys)}")
        print("Please edit the .env file to add your API keys.")
        return False
    else:
        print("\n✅ All API keys configured!")
        return True

def test_langchain_setup():
    """Test LangChain and LangGraph setup."""
    print("\n🤖 Testing LangChain/LangGraph setup...")
    
    try:
        from langchain_openai import ChatOpenAI
        from langgraph.prebuilt import create_react_agent
        from langchain_core.tools import tool
        
        print("✅ LangChain imports successful!")
        
        # Test tool definition
        @tool
        def test_tool(input_text: str) -> str:
            """A simple test tool."""
            return f"Processed: {input_text}"
        
        print("✅ Tool creation successful!")
        
        # Test if OpenAI key is available for agent creation
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your-openai-api-key-here":
            try:
                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
                agent = create_react_agent(llm, [test_tool])
                print("✅ Agent creation successful!")
                return True
            except Exception as e:
                print(f"⚠️  Agent creation failed: {e}")
                return False
        else:
            print("⚠️  OpenAI API key not configured - agent creation skipped")
            return True
            
    except Exception as e:
        print(f"❌ LangChain setup failed: {e}")
        return False

def run_health_check():
    """Run a basic health check of the application."""
    print("\n🏥 Running application health check...")
    
    try:
        # Import the app
        sys.path.append('.')
        from app import app, llm, agent
        
        print("✅ Flask app imported successfully!")
        
        # Test app creation
        with app.test_client() as client:
            response = client.get('/api/health')
            if response.status_code == 200:
                data = response.get_json()
                print("✅ Health endpoint working!")
                print(f"   - Status: {data.get('status')}")
                print(f"   - OpenAI enabled: {data.get('openai_enabled')}")
                print(f"   - LangSmith enabled: {data.get('langsmith_enabled')}")
                return True
            else:
                print(f"❌ Health check failed with status: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Advanced Skill Matching Backend Setup")
    print("=" * 50)
    
    # Change to the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    success = True
    
    # Step 1: Install requirements
    if not install_requirements():
        success = False
    
    # Step 2: Setup environment
    if not setup_environment():
        success = False
    
    # Step 3: Test imports
    if not test_imports():
        success = False
        return
    
    # Step 4: Check API keys
    if not check_api_keys():
        success = False
    
    # Step 5: Test LangChain setup
    if not test_langchain_setup():
        success = False
    
    # Step 6: Run health check
    if not run_health_check():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your actual API keys")
        print("2. Run: python app.py")
        print("3. Test the API at http://localhost:5001/api/health")
    else:
        print("❌ Setup completed with errors!")
        print("Please check the errors above and fix them before proceeding.")

if __name__ == "__main__":
    main()