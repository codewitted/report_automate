#!/usr/bin/env python3
"""
Test script to verify the web interface is working correctly.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")
    try:
        from app import app
        print("  ✓ app module imported")
        
        from jira_client import JiraClient, JiraAPIError
        print("  ✓ jira_client module imported")
        
        from report_generator import ReportGenerator
        print("  ✓ report_generator module imported")
        
        from config_manager import ConfigManager
        print("  ✓ config_manager module imported")
        
        return True
    except Exception as e:
        print(f"  ✗ Import error: {e}")
        return False

def test_flask_routes():
    """Test that Flask routes are configured."""
    print("\nTesting Flask routes...")
    try:
        from app import app
        
        # Get all routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(str(rule))
        
        expected_routes = ['/', '/generate', '/download/<filename>', '/health']
        
        for route in expected_routes:
            # Check if route exists (with or without methods)
            route_exists = any(route in r for r in routes)
            if route_exists:
                print(f"  ✓ Route '{route}' configured")
            else:
                print(f"  ✗ Route '{route}' missing")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Route test error: {e}")
        return False

def test_template_exists():
    """Test that the template file exists."""
    print("\nTesting template files...")
    try:
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
        if os.path.exists(template_path):
            print(f"  ✓ Template file exists: {template_path}")
            return True
        else:
            print(f"  ✗ Template file missing: {template_path}")
            return False
    except Exception as e:
        print(f"  ✗ Template test error: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint."""
    print("\nTesting health endpoint...")
    try:
        from app import app
        
        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                print(f"  ✓ Health endpoint responding: {response.json}")
                return True
            else:
                print(f"  ✗ Health endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"  ✗ Health endpoint test error: {e}")
        return False

def test_index_page():
    """Test that the index page loads."""
    print("\nTesting index page...")
    try:
        from app import app
        
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print(f"  ✓ Index page loads successfully")
                return True
            else:
                print(f"  ✗ Index page failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"  ✗ Index page test error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Web Interface Test Suite")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Run tests
    all_tests_passed &= test_imports()
    all_tests_passed &= test_flask_routes()
    all_tests_passed &= test_template_exists()
    all_tests_passed &= test_health_endpoint()
    all_tests_passed &= test_index_page()
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("✅ All tests passed!")
        print("=" * 60)
        return 0
    else:
        print("❌ Some tests failed!")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
