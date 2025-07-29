"""
SelfCompiler - Autonomous Code Evolution System
Implements full Git integration with GitHub Fine-grained Personal Access Token
"""

import os
import time
import logging
import subprocess
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path
import git
from git import Repo, GitCommandError

from config import config
from utils.secret_loader import get_secret, get_secret_required


class GitHubAPI:
    """GitHub API integration using Fine-grained Personal Access Token"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.token = get_secret_required("GITHUB_FINE_TOKEN")
        self.username = get_secret("GIT_USERNAME", "ark-agent")
        self.email = get_secret("GIT_EMAIL", "ark-agent@ark-project.org")
        self.repo_url = get_secret("GIT_REPO_URL", "https://github.com/your-org/ark-project")
        
        # Extract owner and repo from URL
        self.owner, self.repo = self._parse_repo_url()
        
        # GitHub API headers
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ARK-Agent/2.6"
        }
        
        self.api_base = "https://api.github.com"
        
    def _parse_repo_url(self) -> tuple:
        """Parse repository URL to extract owner and repo name"""
        try:
            # Handle both HTTPS and SSH URLs
            if self.repo_url.startswith("https://"):
                parts = self.repo_url.replace("https://github.com/", "").split("/")
            elif self.repo_url.startswith("git@github.com:"):
                parts = self.repo_url.replace("git@github.com:", "").split("/")
            else:
                raise ValueError(f"Unsupported repository URL format: {self.repo_url}")
            
            if len(parts) >= 2:
                owner = parts[0]
                repo = parts[1].replace(".git", "")
                return owner, repo
            else:
                raise ValueError(f"Invalid repository URL: {self.repo_url}")
                
        except Exception as e:
            self.logger.error(f"Failed to parse repository URL: {e}")
            return "your-org", "ark-project"
    
    def create_pull_request(self, title: str, description: str, base_branch: str = "main", head_branch: str = None) -> Dict[str, Any]:
        """Create pull request using GitHub API"""
        try:
            if not head_branch:
                head_branch = f"evolution-{int(time.time())}"
            
            # API endpoint for creating PR
            url = f"{self.api_base}/repos/{self.owner}/{self.repo}/pulls"
            
            payload = {
                "title": title,
                "body": description,
                "head": head_branch,
                "base": base_branch,
                "draft": False
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 201:
                pr_data = response.json()
                pr_info = {
                    "number": pr_data["number"],
                    "title": pr_data["title"],
                    "url": pr_data["html_url"],
                    "api_url": pr_data["url"],
                    "state": pr_data["state"],
                    "head_branch": pr_data["head"]["ref"],
                    "base_branch": pr_data["base"]["ref"],
                    "created_at": pr_data["created_at"],
                    "status": "created"
                }
                
                self.logger.info(f"Created PR #{pr_data['number']}: {title}")
                return pr_info
            else:
                error_msg = f"Failed to create PR: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            self.logger.error(f"GitHub API PR creation failed: {e}")
            raise
    
    def merge_pull_request(self, pr_number: int, merge_method: str = "squash") -> Dict[str, Any]:
        """Merge pull request using GitHub API"""
        try:
            url = f"{self.api_base}/repos/{self.owner}/{self.repo}/pulls/{pr_number}/merge"
            
            payload = {
                "merge_method": merge_method,
                "commit_title": f"Merge PR #{pr_number}",
                "commit_message": f"Automated merge of PR #{pr_number} by ARK Agent"
            }
            
            response = requests.put(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                merge_data = response.json()
                merge_info = {
                    "pr_number": pr_number,
                    "sha": merge_data["sha"],
                    "merged": merge_data["merged"],
                    "message": merge_data["message"],
                    "status": "merged"
                }
                
                self.logger.info(f"Merged PR #{pr_number}")
                return merge_info
            else:
                error_msg = f"Failed to merge PR #{pr_number}: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            self.logger.error(f"GitHub API PR merge failed: {e}")
            raise
    
    def close_pull_request(self, pr_number: int) -> Dict[str, Any]:
        """Close pull request using GitHub API"""
        try:
            url = f"{self.api_base}/repos/{self.owner}/{self.repo}/pulls/{pr_number}"
            
            payload = {
                "state": "closed"
            }
            
            response = requests.patch(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                close_info = {
                    "pr_number": pr_number,
                    "state": "closed",
                    "status": "closed"
                }
                
                self.logger.info(f"Closed PR #{pr_number}")
                return close_info
            else:
                error_msg = f"Failed to close PR #{pr_number}: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            self.logger.error(f"GitHub API PR close failed: {e}")
            raise
    
    def get_pull_request(self, pr_number: int) -> Dict[str, Any]:
        """Get pull request information"""
        try:
            url = f"{self.api_base}/repos/{self.owner}/{self.repo}/pulls/{pr_number}"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Failed to get PR #{pr_number}: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            self.logger.error(f"GitHub API get PR failed: {e}")
            raise
    
    def list_pull_requests(self, state: str = "open") -> List[Dict[str, Any]]:
        """List pull requests"""
        try:
            url = f"{self.api_base}/repos/{self.owner}/{self.repo}/pulls"
            params = {"state": state}
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Failed to list PRs: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            self.logger.error(f"GitHub API list PRs failed: {e}")
            raise
    
    def create_issue(self, title: str, body: str, labels: List[str] = None) -> Dict[str, Any]:
        """Create issue using GitHub API"""
        try:
            url = f"{self.api_base}/repos/{self.owner}/{self.repo}/issues"
            
            payload = {
                "title": title,
                "body": body
            }
            
            if labels:
                payload["labels"] = labels
            
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 201:
                issue_data = response.json()
                issue_info = {
                    "number": issue_data["number"],
                    "title": issue_data["title"],
                    "url": issue_data["html_url"],
                    "state": issue_data["state"],
                    "created_at": issue_data["created_at"],
                    "status": "created"
                }
                
                self.logger.info(f"Created issue #{issue_data['number']}: {title}")
                return issue_info
            else:
                error_msg = f"Failed to create issue: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            self.logger.error(f"GitHub API issue creation failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test GitHub API connection"""
        try:
            url = f"{self.api_base}/user"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                user_data = response.json()
                self.logger.info(f"GitHub API connection successful for user: {user_data.get('login', 'unknown')}")
                return True
            else:
                self.logger.error(f"GitHub API connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"GitHub API connection test failed: {e}")
            return False


class SelfCompiler:
    """
    SelfCompiler - Autonomous Code Evolution System
    Implements full Git integration for self-modification with GitHub Fine-grained Personal Access Token
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self._repo: Optional[Repo] = None
        self._git: Optional[git.Git] = None
        self._repo_path: Optional[str] = None
        self._github_api: Optional[GitHubAPI] = None
        
        # Statistics tracking
        self._stats = {
            "commits_created": 0,
            "branches_created": 0,
            "files_modified": 0,
            "last_commit_time": 0,
            "evolution_cycles": 0,
            "rollbacks_performed": 0,
            "prs_created": 0,
            "prs_merged": 0
        }
        
        # Change history for audit
        self._change_history: List[Dict[str, Any]] = []
        
        # Evolution tracking
        self._evolution_cycles: List[Dict[str, Any]] = []
        
    def initialize(self, repo_path: str, use_github_token: bool = True):
        """
        Initialize Git repository connection with GitHub Fine-grained Personal Access Token
        
        Args:
            repo_path: Path to Git repository
            use_github_token: Use GitHub token instead of SSH key
        """
        try:
            self._repo_path = repo_path
            
            # Initialize GitPython repository
            if not os.path.exists(repo_path):
                raise RuntimeError(f"Repository path does not exist: {repo_path}")
            
            self._repo = Repo(repo_path)
            self._git = self._repo.git
            
            if use_github_token:
                # Initialize GitHub API
                self._github_api = GitHubAPI()
                
                # Test GitHub API connection
                if not self._github_api.test_connection():
                    raise RuntimeError("GitHub API connection failed")
                
                # Configure Git to use token authentication
                self._configure_github_token_auth()
                
                self.logger.info("GitHub Fine-grained Personal Access Token configured successfully")
            else:
                # Use SSH key authentication (legacy mode)
                deploy_key_path = get_secret("ARK_DEPLOY_KEY_PATH")
                if deploy_key_path and os.path.exists(deploy_key_path):
                    ssh_command = f'ssh -i {deploy_key_path} -o StrictHostKeyChecking=no'
                    self._git.config('core.sshCommand', ssh_command)
                    self.logger.info(f"SSH key configured: {deploy_key_path}")
                else:
                    self.logger.warning("SSH deploy key not found, using default SSH configuration")
            
            # Verify repository status
            self._verify_repository_status()
            
            self._is_initialized = True
            self.logger.info(f"SelfCompiler initialized for repository: {repo_path}")
            
        except Exception as e:
            self.logger.error(f"SelfCompiler initialization failed: {e}")
            raise
    
    def _configure_github_token_auth(self):
        """Configure Git to use GitHub token authentication"""
        try:
            # Get GitHub token
            token = get_secret_required("GITHUB_FINE_TOKEN")
            username = get_secret("GIT_USERNAME", "ark-agent")
            email = get_secret("GIT_EMAIL", "ark-agent@ark-project.org")
            
            # Configure Git user
            self._git.config('user.name', username)
            self._git.config('user.email', email)
            
            # Configure credential helper to use token
            self._git.config('credential.helper', 'store')
            
            # Store credentials (this will be handled by GitPython)
            # The token will be used automatically for HTTPS operations
            
            self.logger.info("GitHub token authentication configured")
            
        except Exception as e:
            self.logger.error(f"Failed to configure GitHub token authentication: {e}")
            raise
    
    def _verify_repository_status(self):
        """Verify repository is in clean state and properly configured"""
        try:
            # Check if repository is clean
            if self._repo.is_dirty():
                self.logger.warning("Repository has uncommitted changes")
            
            # Check remote configuration
            if not self._repo.remotes:
                self.logger.warning("No remote repositories configured")
            
            # Check current branch
            current_branch = self._repo.active_branch.name
            self.logger.info(f"Current branch: {current_branch}")
            
        except Exception as e:
            self.logger.error(f"Repository verification failed: {e}")
            raise
    
    def create_branch(self, branch_name: str, base_branch: str = "main") -> Dict[str, Any]:
        """
        Create new branch for evolution
        
        Args:
            branch_name: Name of new branch
            base_branch: Base branch to branch from
            
        Returns:
            Branch information
        """
        if not self._is_initialized:
            raise RuntimeError("SelfCompiler not initialized")
        
        try:
            # Check if base branch exists
            if base_branch not in [b.name for b in self._repo.branches]:
                raise ValueError(f"Base branch '{base_branch}' does not exist")
            
            # Check if branch already exists
            if branch_name in [b.name for b in self._repo.branches]:
                self.logger.warning(f"Branch '{branch_name}' already exists")
                return self._get_branch_info(branch_name)
            
            # Create new branch
            base_branch_ref = self._repo.heads[base_branch]
            new_branch = self._repo.create_head(branch_name, base_branch_ref)
            
            # Switch to new branch
            new_branch.checkout()
            
            branch_info = {
                "name": branch_name,
                "base": base_branch,
                "created_at": time.time(),
                "status": "created",
                "commit_hash": new_branch.commit.hexsha
            }
            
            self._stats["branches_created"] += 1
            self.logger.info(f"Created branch: {branch_name} from {base_branch}")
            
            # Log to audit trail
            self._log_evolution_event("branch_created", branch_info)
            
            return branch_info
            
        except Exception as e:
            self.logger.error(f"Branch creation failed: {e}")
            raise
    
    def commit_changes(self, message: str, files: List[str] = None) -> Dict[str, Any]:
        """
        Commit changes with comprehensive audit logging
        
        Args:
            message: Commit message
            files: List of files to commit (None for all changes)
            
        Returns:
            Commit information
        """
        if not self._is_initialized:
            raise RuntimeError("SelfCompiler not initialized")
        
        try:
            # Get current status
            status = self._repo.git.status('--porcelain')
            if not status.strip():
                self.logger.warning("No changes to commit")
                return {"status": "no_changes"}
            
            # Add files to index
            if files:
                for file_path in files:
                    if os.path.exists(file_path):
                        self._repo.index.add([file_path])
            else:
                self._repo.index.add('*')
            
            # Create commit
            commit = self._repo.index.commit(message)
            
            commit_info = {
                "message": message,
                "files": files or [],
                "timestamp": time.time(),
                "hash": commit.hexsha,
                "author": f"{commit.author.name} <{commit.author.email}>",
                "status": "committed",
                "diff": self._get_commit_diff(commit)
            }
            
            self._stats["commits_created"] += 1
            self._stats["last_commit_time"] = commit_info["timestamp"]
            
            # Log to audit trail
            self._log_evolution_event("commit_created", commit_info)
            
            self.logger.info(f"Created commit: {message} ({commit.hexsha[:8]})")
            return commit_info
            
        except Exception as e:
            self.logger.error(f"Commit creation failed: {e}")
            raise
    
    def push_changes(self, branch_name: str = None, remote: str = "origin") -> Dict[str, Any]:
        """
        Push changes to remote repository using GitHub token
        
        Args:
            branch_name: Branch to push (None for current)
            remote: Remote repository name
            
        Returns:
            Push information
        """
        if not self._is_initialized:
            raise RuntimeError("SelfCompiler not initialized")
        
        try:
            current_branch = self._repo.active_branch.name
            target_branch = branch_name or current_branch
            
            # Check if remote exists
            if remote not in [r.name for r in self._repo.remotes]:
                raise ValueError(f"Remote '{remote}' does not exist")
            
            # Push changes using token authentication
            push_result = self._repo.remotes[remote].push(target_branch)
            
            push_info = {
                "branch": target_branch,
                "remote": remote,
                "timestamp": time.time(),
                "status": "pushed",
                "push_result": str(push_result),
                "auth_method": "github_token"
            }
            
            self.logger.info(f"Pushed changes to {remote}/{target_branch} using GitHub token")
            
            # Log to audit trail
            self._log_evolution_event("changes_pushed", push_info)
            
            return push_info
            
        except GitCommandError as e:
            self.logger.error(f"Push failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Push operation failed: {e}")
            raise
    
    def create_pull_request(self, title: str, description: str, base_branch: str = "main") -> Dict[str, Any]:
        """
        Create pull request using GitHub API
        
        Args:
            title: PR title
            description: PR description
            base_branch: Base branch for PR
            
        Returns:
            PR information
        """
        if not self._is_initialized:
            raise RuntimeError("SelfCompiler not initialized")
        
        if not self._github_api:
            raise RuntimeError("GitHub API not available")
        
        try:
            current_branch = self._repo.active_branch.name
            
            # Create PR using GitHub API
            pr_info = self._github_api.create_pull_request(
                title=title,
                description=description,
                base_branch=base_branch,
                head_branch=current_branch
            )
            
            self._stats["prs_created"] += 1
            
            # Log to audit trail
            self._log_evolution_event("pr_created", pr_info)
            
            return pr_info
            
        except Exception as e:
            self.logger.error(f"PR creation failed: {e}")
            raise
    
    def merge_pull_request(self, pr_number: int, merge_method: str = "squash") -> Dict[str, Any]:
        """
        Merge pull request using GitHub API
        
        Args:
            pr_number: Pull request number
            merge_method: Merge method (squash, merge, rebase)
            
        Returns:
            Merge information
        """
        if not self._is_initialized:
            raise RuntimeError("SelfCompiler not initialized")
        
        if not self._github_api:
            raise RuntimeError("GitHub API not available")
        
        try:
            # Merge PR using GitHub API
            merge_info = self._github_api.merge_pull_request(pr_number, merge_method)
            
            self._stats["prs_merged"] += 1
            
            # Log to audit trail
            self._log_evolution_event("pr_merged", merge_info)
            
            return merge_info
            
        except Exception as e:
            self.logger.error(f"PR merge failed: {e}")
            raise
    
    def close_pull_request(self, pr_number: int) -> Dict[str, Any]:
        """
        Close pull request using GitHub API
        
        Args:
            pr_number: Pull request number
            
        Returns:
            Close information
        """
        if not self._is_initialized:
            raise RuntimeError("SelfCompiler not initialized")
        
        if not self._github_api:
            raise RuntimeError("GitHub API not available")
        
        try:
            # Close PR using GitHub API
            close_info = self._github_api.close_pull_request(pr_number)
            
            # Log to audit trail
            self._log_evolution_event("pr_closed", close_info)
            
            return close_info
            
        except Exception as e:
            self.logger.error(f"PR close failed: {e}")
            raise
    
    def get_pull_request_status(self, pr_number: int) -> Dict[str, Any]:
        """
        Get pull request status
        
        Args:
            pr_number: Pull request number
            
        Returns:
            PR status information
        """
        if not self._is_initialized:
            raise RuntimeError("SelfCompiler not initialized")
        
        if not self._github_api:
            raise RuntimeError("GitHub API not available")
        
        try:
            return self._github_api.get_pull_request(pr_number)
        except Exception as e:
            self.logger.error(f"Failed to get PR status: {e}")
            raise
    
    def list_pull_requests(self, state: str = "open") -> List[Dict[str, Any]]:
        """
        List pull requests
        
        Args:
            state: PR state (open, closed, all)
            
        Returns:
            List of PR information
        """
        if not self._is_initialized:
            raise RuntimeError("SelfCompiler not initialized")
        
        if not self._github_api:
            raise RuntimeError("GitHub API not available")
        
        try:
            return self._github_api.list_pull_requests(state)
        except Exception as e:
            self.logger.error(f"Failed to list PRs: {e}")
            raise
    
    def create_issue(self, title: str, body: str, labels: List[str] = None) -> Dict[str, Any]:
        """
        Create issue using GitHub API
        
        Args:
            title: Issue title
            body: Issue description
            labels: List of labels
            
        Returns:
            Issue information
        """
        if not self._is_initialized:
            raise RuntimeError("SelfCompiler not initialized")
        
        if not self._github_api:
            raise RuntimeError("GitHub API not available")
        
        try:
            return self._github_api.create_issue(title, body, labels)
        except Exception as e:
            self.logger.error(f"Issue creation failed: {e}")
            raise
    
    def rollback_to_commit(self, commit_hash: str) -> Dict[str, Any]:
        """
        Rollback to specific commit
        
        Args:
            commit_hash: Target commit hash
            
        Returns:
            Rollback information
        """
        if not self._is_initialized:
            raise RuntimeError("SelfCompiler not initialized")
        
        try:
            # Verify commit exists
            try:
                target_commit = self._repo.commit(commit_hash)
            except Exception:
                raise ValueError(f"Commit {commit_hash} not found")
            
            # Create backup branch before rollback
            backup_branch_name = f"backup-{int(time.time())}"
            backup_branch = self._repo.create_head(backup_branch_name)
            
            # Reset to target commit
            self._repo.head.reset(commit=target_commit, index=True, working_tree=True)
            
            rollback_info = {
                "target_commit": commit_hash,
                "backup_branch": backup_branch_name,
                "timestamp": time.time(),
                "status": "rolled_back",
                "current_commit": self._repo.head.commit.hexsha
            }
            
            self._stats["rollbacks_performed"] += 1
            
            self.logger.info(f"Rolled back to commit: {commit_hash}")
            self._log_evolution_event("rollback_performed", rollback_info)
            
            return rollback_info
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            raise
    
    def modify_file(self, file_path: str, content: str, operation: str = "write") -> Dict[str, Any]:
        """
        Modify file with backup and validation
        
        Args:
            file_path: Path to file
            content: New content
            operation: Operation type (write, append, replace)
            
        Returns:
            Modification information
        """
        if not self._is_initialized:
            raise RuntimeError("SelfCompiler not initialized")
        
        try:
            # Create backup
            backup_path = f"{file_path}.backup.{int(time.time())}"
            if os.path.exists(file_path):
                import shutil
                shutil.copy2(file_path, backup_path)
            
            # Apply modification
            if operation == "write":
                with open(file_path, 'w') as f:
                    f.write(content)
            elif operation == "append":
                with open(file_path, 'a') as f:
                    f.write(content)
            elif operation == "replace":
                # This would require more complex logic for pattern replacement
                with open(file_path, 'w') as f:
                    f.write(content)
            
            # Validate Python files
            if file_path.endswith('.py'):
                try:
                    with open(file_path, 'r') as f:
                        compile(f.read(), file_path, 'exec')
                except SyntaxError as e:
                    # Restore backup on syntax error
                    if os.path.exists(backup_path):
                        shutil.copy2(backup_path, file_path)
                    raise ValueError(f"Python syntax error in {file_path}: {e}")
            
            modification_info = {
                "file_path": file_path,
                "operation": operation,
                "timestamp": time.time(),
                "status": "modified",
                "backup_created": os.path.exists(backup_path),
                "backup_path": backup_path if os.path.exists(backup_path) else None
            }
            
            self._stats["files_modified"] += 1
            
            # Log to audit trail
            self._log_evolution_event("file_modified", modification_info)
            
            self.logger.info(f"Modified file: {file_path}")
            return modification_info
            
        except Exception as e:
            self.logger.error(f"File modification failed: {e}")
            raise
    
    def _get_commit_diff(self, commit) -> str:
        """Get diff for commit"""
        try:
            if commit.parents:
                return self._repo.git.diff(commit.parents[0].hexsha, commit.hexsha)
            else:
                return self._repo.git.diff('4b825dc642cb6eb9a060e54bf8d69288fbee4904', commit.hexsha)
        except Exception:
            return "Diff not available"
    
    def _get_branch_info(self, branch_name: str) -> Dict[str, Any]:
        """Get information about branch"""
        try:
            branch = self._repo.heads[branch_name]
            return {
                "name": branch_name,
                "commit_hash": branch.commit.hexsha,
                "is_active": branch.name == self._repo.active_branch.name
            }
        except Exception:
            return {"name": branch_name, "status": "not_found"}
    
    def _log_evolution_event(self, event_type: str, data: Dict[str, Any]):
        """Log evolution event to audit trail"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": time.time(),
            "evolution_cycle": self._stats["evolution_cycles"]
        }
        
        self._change_history.append(event)
        
        # Also log to consciousness monitor
        try:
            from evaluation.consciousness_monitor import ConsciousnessMonitor
            monitor = ConsciousnessMonitor()
            monitor.log_evolution_event(event)
        except Exception as e:
            self.logger.warning(f"Failed to log to consciousness monitor: {e}")
    
    def get_change_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get change history for audit"""
        return self._change_history[-limit:]
    
    def get_compiler_stats(self) -> Dict[str, Any]:
        """Get compiler statistics"""
        return {
            "initialized": self._is_initialized,
            "repo_path": self._repo_path,
            "github_api_available": self._github_api is not None,
            "commits_created": self._stats["commits_created"],
            "branches_created": self._stats["branches_created"],
            "files_modified": self._stats["files_modified"],
            "last_commit_time": self._stats["last_commit_time"],
            "evolution_cycles": self._stats["evolution_cycles"],
            "rollbacks_performed": self._stats["rollbacks_performed"],
            "prs_created": self._stats["prs_created"],
            "prs_merged": self._stats["prs_merged"],
            "change_history_size": len(self._change_history)
        }
    
    def get_compiler_status(self) -> Dict[str, Any]:
        """Get compiler status"""
        return {
            "active": self._is_initialized,
            "repo_configured": bool(self._repo_path),
            "github_api_available": self._github_api is not None,
            "git_available": self._repo is not None,
            "stats": self.get_compiler_stats(),
            "capabilities": [
                "create_branch",
                "commit_changes", 
                "push_changes",
                "create_pull_request",
                "merge_pull_request",
                "close_pull_request",
                "create_issue",
                "rollback_to_commit",
                "modify_file",
                "self_evolution"
            ]
        }
    
    def backup_current_state(self) -> str:
        """Create backup of current state"""
        try:
            if not self._is_initialized:
                raise RuntimeError("SelfCompiler not initialized")
            
            # Create backup branch
            backup_branch_name = f"backup-{int(time.time())}"
            backup_branch = self._repo.create_head(backup_branch_name)
            
            backup_info = {
                "timestamp": time.time(),
                "type": "state_backup",
                "branch_name": backup_branch_name,
                "commit_hash": backup_branch.commit.hexsha,
                "description": "Automatic state backup"
            }
            
            self._log_evolution_event("backup_created", backup_info)
            self.logger.info(f"Created backup: {backup_branch_name}")
            
            return backup_branch_name
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            raise
    
    def rollback_to_backup(self, backup_id: str) -> bool:
        """
        Rollback to backup
        
        Args:
            backup_id: Backup branch name
            
        Returns:
            True if rollback successful
        """
        try:
            if not self._is_initialized:
                raise RuntimeError("SelfCompiler not initialized")
            
            # Check if backup branch exists
            if backup_id not in [b.name for b in self._repo.branches]:
                raise ValueError(f"Backup branch '{backup_id}' not found")
            
            # Rollback to backup
            backup_branch = self._repo.heads[backup_id]
            self._repo.head.reset(commit=backup_branch.commit, index=True, working_tree=True)
            
            rollback_info = {
                "backup_id": backup_id,
                "timestamp": time.time(),
                "status": "rolled_back_to_backup"
            }
            
            self._log_evolution_event("backup_rollback", rollback_info)
            self.logger.info(f"Rolled back to backup: {backup_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Backup rollback failed: {e}")
            return False 