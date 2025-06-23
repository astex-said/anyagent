#!/usr/bin/env python3
"""
Publish AnyAgent to PyPI
"""
import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        sys.exit(1)


def main():
    print("🚀 Publishing AnyAgent Framework to PyPI")
    
    # Check if we're in the right directory
    if not os.path.exists("setup.py"):
        print("❌ setup.py not found. Run this from the project root.")
        sys.exit(1)
    
    # Clean previous builds
    run_command("rm -rf build/ dist/ *.egg-info/", "Cleaning previous builds")
    
    # Build the package
    run_command("python3 setup.py sdist bdist_wheel", "Building package")
    
    # Check the package
    run_command("python3 -m twine check dist/*", "Checking package")
    
    # Upload to TestPyPI first (optional)
    response = input("🤔 Upload to TestPyPI first? (y/n): ")
    if response.lower() == 'y':
        print("📦 Uploading to TestPyPI...")
        run_command("python3 -m twine upload --repository testpypi dist/*", "Uploading to TestPyPI")
        
        print("✅ Uploaded to TestPyPI!")
        print("🔗 Check: https://test.pypi.org/project/anyagent/")
        
        test_response = input("🧪 Test install from TestPyPI? (y/n): ")
        if test_response.lower() == 'y':
            run_command("pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ anyagent", "Testing install from TestPyPI")
    
    # Upload to production PyPI
    response = input("🚀 Upload to production PyPI? (y/n): ")
    if response.lower() == 'y':
        run_command("python3 -m twine upload dist/*", "Uploading to PyPI")
        
        print("🎉 AnyAgent Framework published to PyPI!")
        print("🔗 Check: https://pypi.org/project/anyagent/")
        print("📦 Install with: pip install anyagent")
    else:
        print("⏸️  Skipped production upload")
    
    print("✅ Done!")


if __name__ == "__main__":
    main()