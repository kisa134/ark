#!/usr/bin/env python3
"""
Test GitHub Integration for ARK Agent
Tests all GitHub API operations for self-evolution
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.secret_loader import get_secret
import requests
import json
from datetime import datetime

def test_github_token():
    """Test GitHub token authentication"""
    print("🔑 Testing GitHub Token Authentication...")
    
    token = get_secret('GITHUB_FINE_TOKEN')
    if not token:
        print("❌ GitHub token not found!")
        return False
    
    # Test GitHub API authentication
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get('https://api.github.com/user', headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ GitHub authentication successful!")
            print(f"   User: {user_data.get('login', 'Unknown')}")
            print(f"   Name: {user_data.get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ GitHub authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing GitHub authentication: {e}")
        return False

def test_repository_access():
    """Test repository access"""
    print("\n📁 Testing Repository Access...")
    
    token = get_secret('GITHUB_FINE_TOKEN')
    repo_url = get_secret('GIT_REPO_URL', 'https://github.com/your-org/ark-project')
    
    # Extract owner and repo from URL
    if 'github.com' in repo_url:
        parts = repo_url.replace('https://github.com/', '').split('/')
        if len(parts) >= 2:
            owner = parts[0]
            repo = parts[1].replace('.git', '')
        else:
            print("❌ Invalid repository URL format")
            return False
    else:
        print("❌ Repository URL not configured")
        return False
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get(f'https://api.github.com/repos/{owner}/{repo}', headers=headers)
        if response.status_code == 200:
            repo_data = response.json()
            print(f"✅ Repository access successful!")
            print(f"   Repository: {repo_data.get('full_name', 'Unknown')}")
            print(f"   Description: {repo_data.get('description', 'No description')}")
            print(f"   Private: {repo_data.get('private', False)}")
            return True
        else:
            print(f"❌ Repository access failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing repository access: {e}")
        return False

def test_branch_operations():
    """Test branch operations"""
    print("\n🌿 Testing Branch Operations...")
    
    token = get_secret('GITHUB_FINE_TOKEN')
    repo_url = get_secret('GIT_REPO_URL', 'https://github.com/your-org/ark-project')
    
    # Extract owner and repo from URL
    if 'github.com' in repo_url:
        parts = repo_url.replace('https://github.com/', '').split('/')
        if len(parts) >= 2:
            owner = parts[0]
            repo = parts[1].replace('.git', '')
        else:
            print("❌ Invalid repository URL format")
            return False
    else:
        print("❌ Repository URL not configured")
        return False
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # Get default branch
        response = requests.get(f'https://api.github.com/repos/{owner}/{repo}', headers=headers)
        if response.status_code == 200:
            repo_data = response.json()
            default_branch = repo_data.get('default_branch', 'main')
            print(f"✅ Default branch: {default_branch}")
            
            # Get branches
            response = requests.get(f'https://api.github.com/repos/{owner}/{repo}/branches', headers=headers)
            if response.status_code == 200:
                branches = response.json()
                print(f"✅ Found {len(branches)} branches")
                for branch in branches[:5]:  # Show first 5 branches
                    print(f"   - {branch['name']}")
                return True
            else:
                print(f"❌ Failed to get branches: {response.status_code}")
                return False
        else:
            print(f"❌ Failed to get repository info: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing branch operations: {e}")
        return False

def test_issue_operations():
    """Test issue operations"""
    print("\n📝 Testing Issue Operations...")
    
    token = get_secret('GITHUB_FINE_TOKEN')
    repo_url = get_secret('GIT_REPO_URL', 'https://github.com/your-org/ark-project')
    
    # Extract owner and repo from URL
    if 'github.com' in repo_url:
        parts = repo_url.replace('https://github.com/', '').split('/')
        if len(parts) >= 2:
            owner = parts[0]
            repo = parts[1].replace('.git', '')
        else:
            print("❌ Invalid repository URL format")
            return False
    else:
        print("❌ Repository URL not configured")
        return False
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # Get issues
        response = requests.get(f'https://api.github.com/repos/{owner}/{repo}/issues', headers=headers)
        if response.status_code == 200:
            issues = response.json()
            print(f"✅ Found {len(issues)} issues")
            return True
        else:
            print(f"❌ Failed to get issues: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing issue operations: {e}")
        return False

def main():
    """Run all GitHub integration tests"""
    print("🚀 ARK Agent GitHub Integration Test")
    print("=" * 50)
    
    tests = [
        test_github_token,
        test_repository_access,
        test_branch_operations,
        test_issue_operations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All GitHub integration tests passed!")
        print("✅ ARK Agent is ready for self-evolution")
        return True
    else:
        print("⚠️ Some tests failed. Please check configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 