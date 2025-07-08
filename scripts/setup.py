#!/usr/bin/env python3
"""
Setup script for Argus AI Gateway development environment.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, check=True):
    """Run a shell command."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode == 0

def setup_python_env():
    """Setup Python environment."""
    print("🐍 Setting up Python environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install in development mode
    if not run_command("pip install -e .", check=False):
        print("⚠️  Failed to install in development mode, trying regular install...")
        run_command("pip install -r requirements.txt")
    
    return True

def setup_pre_commit():
    """Setup pre-commit hooks."""
    print("🔧 Setting up pre-commit hooks...")
    
    if shutil.which("pre-commit"):
        run_command("pre-commit install")
        print("✅ Pre-commit hooks installed")
    else:
        print("⚠️  pre-commit not found, skipping...")

def create_env_file():
    """Create .env file from example if it doesn't exist."""
    print("📝 Setting up environment file...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ Created .env from .env.example")
        else:
            # Create basic .env file
            with open(env_file, 'w') as f:
                f.write("# Argus AI Gateway Configuration\n")
                f.write("OPENROUTER_API_KEY=your_api_key_here\n")
                f.write("GUARD_LLM_MODEL=deepseek/deepseek-r1-distill-qwen-32b:free\n")
                f.write("LOG_LEVEL=INFO\n")
                f.write("YOUR_SITE_URL=http://localhost:8000\n")
                f.write("YOUR_SITE_NAME=Argus AI Gateway MVP\n")
            print("✅ Created basic .env file")
        
        print("⚠️  Please update .env with your actual API keys!")
    else:
        print("✅ .env file already exists")

def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    
    dirs = ["logs", "tests/data", "docs/diagrams"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def run_tests():
    """Run basic tests to verify setup."""
    print("🧪 Running basic tests...")
    
    # Run a simple import test
    try:
        from src.argus import ArgusGateway
        print("✅ Core imports working")
        
        # Test gateway initialization
        gateway = ArgusGateway()
        print("✅ Gateway initialization working")
        
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🛡️  Argus AI Gateway - Development Setup")
    print("=" * 50)
    
    # Change to project directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Setup steps
    steps = [
        ("Python Environment", setup_python_env),
        ("Environment File", create_env_file),
        ("Directories", create_directories),
        ("Pre-commit Hooks", setup_pre_commit),
        ("Basic Tests", run_tests),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}")
        print("-" * 30)
        
        try:
            success = step_func()
            if not success:
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} failed: {e}")
            failed_steps.append(step_name)
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Setup Summary")
    
    if failed_steps:
        print(f"⚠️  {len(failed_steps)} step(s) had issues:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease address these issues manually.")
    else:
        print("✅ All setup steps completed successfully!")
    
    print("\n🚀 Quick Start:")
    print("   1. Update .env with your OpenRouter API key")
    print("   2. Run CLI: python cli.py")
    print("   3. Run Web UI: python app.py")
    print("   4. Run tests: python -m pytest tests/")
    
    return len(failed_steps) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
