#!/usr/bin/env python3
"""
Create GitHub Repository for ARK Project
Creates a new repository for self-evolution
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.secret_loader import get_secret
import requests
import json

def create_github_repository():
    """Create GitHub repository for ARK project"""
    print("🚀 Creating GitHub Repository for ARK Project...")
    
    token = get_secret('GITHUB_FINE_TOKEN')
    if not token:
        print("❌ GitHub token not found!")
        return False
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    }
    
    # Repository configuration
    repo_data = {
        "name": "ark",
        "description": "ARK Project - Autonomous Digital Organism with Self-Evolution Capabilities",
        "homepage": "https://ark-project.org",
        "private": False,
        "has_issues": True,
        "has_wiki": True,
        "has_downloads": True,
        "auto_init": False,
        "gitignore_template": "Python",
        "license_template": "mit"
    }
    
    try:
        response = requests.post('https://api.github.com/user/repos', 
                               headers=headers, 
                               data=json.dumps(repo_data))
        
        if response.status_code == 201:
            repo_info = response.json()
            print("✅ Repository created successfully!")
            print(f"   Name: {repo_info['name']}")
            print(f"   Full Name: {repo_info['full_name']}")
            print(f"   URL: {repo_info['html_url']}")
            print(f"   Clone URL: {repo_info['clone_url']}")
            
            # Update secrets.env with new repository URL
            repo_url = repo_info['clone_url']
            update_secrets_file(repo_url)
            
            return True
        else:
            print(f"❌ Failed to create repository: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating repository: {e}")
        return False

def update_secrets_file(repo_url):
    """Update secrets.env with new repository URL"""
    try:
        # Read current secrets.env
        with open('secrets.env', 'r') as f:
            content = f.read()
        
        # Replace GIT_REPO_URL
        if 'GIT_REPO_URL=' in content:
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith('GIT_REPO_URL='):
                    new_lines.append(f'GIT_REPO_URL={repo_url}')
                else:
                    new_lines.append(line)
            content = '\n'.join(new_lines)
        else:
            content += f'\nGIT_REPO_URL={repo_url}\n'
        
        # Write back to secrets.env
        with open('secrets.env', 'w') as f:
            f.write(content)
        
        print(f"✅ Updated secrets.env with repository URL: {repo_url}")
        
    except Exception as e:
        print(f"❌ Error updating secrets.env: {e}")

def setup_local_repository():
    """Setup local git repository and push to GitHub"""
    print("\n🔧 Setting up local repository...")
    
    try:
        # Initialize git if not already done
        if not os.path.exists('.git'):
            os.system('git init')
            print("✅ Git repository initialized")
        
        # Add all files
        os.system('git add .')
        print("✅ Files added to git")
        
        # Create initial commit
        os.system('git commit -m "Initial commit: ARK Project v2.8"')
        print("✅ Initial commit created")
        
        # Add remote and push
        repo_url = get_secret('GIT_REPO_URL')
        if repo_url:
            os.system(f'git remote add origin {repo_url}')
            os.system('git branch -M main')
            os.system('git push -u origin main')
            print("✅ Repository pushed to GitHub")
            return True
        else:
            print("❌ Repository URL not found in secrets")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up local repository: {e}")
        return False

def main():
    """Main function"""
    print("🚀 ARK Project GitHub Repository Setup")
    print("=" * 50)
    
    # Check if repository already exists
    token = get_secret('GITHUB_FINE_TOKEN')
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get('https://api.github.com/repos/kisa134/ark', headers=headers)
        if response.status_code == 200:
            print("✅ Repository already exists!")
            repo_info = response.json()
            print(f"   URL: {repo_info['html_url']}")
            
            # Update secrets with existing repository
            update_secrets_file(repo_info['clone_url'])
            
            # Setup local repository
            setup_local_repository()
            return True
        else:
            # Create new repository
            if create_github_repository():
                setup_local_repository()
                return True
            else:
                return False
                
    except Exception as e:
        print(f"❌ Error checking repository: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 