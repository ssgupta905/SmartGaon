"""Verification script for project setup."""

import sys
from pathlib import Path


def verify_structure():
    """Verify project structure is correctly set up."""
    required_dirs = [
        "src",
        "tests",
        "tests/unit",
        "tests/property",
        "tests/integration",
        "fixtures"
    ]
    
    required_files = [
        "requirements.txt",
        ".env.template",
        ".gitignore",
        "pytest.ini",
        "README.md",
        "src/__init__.py",
        "src/config.py",
        "src/aws_client.py"
    ]
    
    print("Verifying project structure...")
    
    # Check directories
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print(f"✓ Directory exists: {dir_path}")
        else:
            print(f"✗ Missing directory: {dir_path}")
            return False
    
    # Check files
    for file_path in required_files:
        path = Path(file_path)
        if path.exists() and path.is_file():
            print(f"✓ File exists: {file_path}")
        else:
            print(f"✗ Missing file: {file_path}")
            return False
    
    return True


def verify_imports():
    """Verify core imports work correctly."""
    print("\nVerifying imports...")
    
    try:
        from src.config import settings
        print(f"✓ Config imported successfully")
        print(f"  - AWS Region: {settings.aws_region}")
        print(f"  - Supported Languages: {settings.supported_languages_list}")
        print(f"  - Demo Mode: {settings.demo_mode}")
    except Exception as e:
        print(f"✗ Failed to import config: {e}")
        return False
    
    try:
        from src.aws_client import aws_client
        print(f"✓ AWS client imported successfully")
    except Exception as e:
        print(f"✗ Failed to import AWS client: {e}")
        return False
    
    return True


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("GramSaarthi AI - Project Setup Verification")
    print("=" * 60)
    
    structure_ok = verify_structure()
    imports_ok = verify_imports()
    
    print("\n" + "=" * 60)
    if structure_ok and imports_ok:
        print("✓ All verification checks passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some verification checks failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
