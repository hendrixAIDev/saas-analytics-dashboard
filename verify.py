#!/usr/bin/env python3
"""
Verification script to check if the dashboard is properly set up.
Run this before deploying to catch common issues.
"""

import os
import sys
from pathlib import Path

def check_mark(condition, message):
    """Print check mark or X based on condition."""
    symbol = "✅" if condition else "❌"
    print(f"{symbol} {message}")
    return condition

def verify_files():
    """Verify all required files exist."""
    print("\n📁 Checking Files...")
    
    required_files = [
        "app.py",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "schema.sql",
        "seed_data.py",
        "README.md",
        "CUSTOMIZATION.md",
        "QUICKSTART.md",
        "utils/auth.py",
        "utils/database.py",
        "utils/charts.py",
        "utils/ai_insights.py",
        "assets/style.css"
    ]
    
    all_exist = True
    for file in required_files:
        exists = Path(file).exists()
        all_exist = all_exist and check_mark(exists, f"{file}")
    
    return all_exist

def verify_env():
    """Check if .env file is set up."""
    print("\n🔐 Checking Environment...")
    
    env_exists = Path(".env").exists()
    check_mark(env_exists, ".env file exists")
    
    if env_exists:
        with open(".env") as f:
            content = f.read()
            has_supabase_url = "SUPABASE_URL=" in content and "your_supabase" not in content
            has_supabase_key = "SUPABASE_KEY=" in content and "your_supabase" not in content
            has_claude_key = "ANTHROPIC_API_KEY=" in content and "your_anthropic" not in content
            
            check_mark(has_supabase_url, "SUPABASE_URL configured")
            check_mark(has_supabase_key, "SUPABASE_KEY configured")
            check_mark(has_claude_key, "ANTHROPIC_API_KEY configured")
            
            return has_supabase_url and has_supabase_key and has_claude_key
    else:
        print("   ⚠️  Copy .env.example to .env and configure")
        return False

def verify_dependencies():
    """Check if dependencies are installed."""
    print("\n📦 Checking Dependencies...")
    
    packages = [
        "streamlit",
        "supabase",
        "plotly",
        "pandas",
        "anthropic",
        "dotenv"
    ]
    
    all_installed = True
    for package in packages:
        try:
            __import__(package)
            check_mark(True, package)
        except ImportError:
            check_mark(False, f"{package} (run: pip install -r requirements.txt)")
            all_installed = False
    
    return all_installed

def verify_imports():
    """Check if custom modules can be imported."""
    print("\n🔧 Checking Custom Modules...")
    
    modules = [
        "utils.auth",
        "utils.database",
        "utils.charts",
        "utils.ai_insights"
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            check_mark(True, module)
        except Exception as e:
            check_mark(False, f"{module} ({str(e)})")
            all_ok = False
    
    return all_ok

def count_lines():
    """Count total lines of Python code."""
    print("\n📊 Code Statistics...")
    
    python_files = [
        "app.py",
        "seed_data.py",
        "utils/auth.py",
        "utils/database.py",
        "utils/charts.py",
        "utils/ai_insights.py"
    ]
    
    total_lines = 0
    for file in python_files:
        if Path(file).exists():
            with open(file) as f:
                lines = len(f.readlines())
                total_lines += lines
                print(f"   {file}: {lines} lines")
    
    print(f"\n   Total: {total_lines} lines")
    under_limit = total_lines < 1000
    check_mark(under_limit, f"Under 1000 line limit ({total_lines}/1000)")
    
    return under_limit

def verify_git():
    """Check git repository status."""
    print("\n🔀 Checking Git Repository...")
    
    is_git = Path(".git").exists()
    check_mark(is_git, "Git repository initialized")
    
    if is_git:
        import subprocess
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            is_clean = len(result.stdout.strip()) == 0
            check_mark(is_clean, "All changes committed")
            return is_clean
        except:
            return False
    return False

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("🔍 SaaS Analytics Dashboard - Verification Script")
    print("=" * 60)
    
    checks = [
        ("Files", verify_files()),
        ("Environment", verify_env()),
        ("Dependencies", verify_dependencies()),
        ("Modules", verify_imports()),
        ("Code Size", count_lines()),
        ("Git", verify_git())
    ]
    
    print("\n" + "=" * 60)
    print("📋 Summary")
    print("=" * 60)
    
    all_passed = all(result for _, result in checks)
    
    for name, result in checks:
        check_mark(result, name)
    
    if all_passed:
        print("\n✨ All checks passed! Ready to deploy.")
        print("\n🚀 Next steps:")
        print("   1. Run: python seed_data.py")
        print("   2. Run: streamlit run app.py")
        print("   3. Test all features")
        print("   4. Deploy using DEPLOYMENT.md")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
