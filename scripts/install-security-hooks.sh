#!/bin/bash
# Ark Project - Security Hooks Installation
# Embodied Digital Organism - Sanctuary Security Setup
#
# This script installs security hooks and sets up proper file permissions

set -e

echo "🔒 Ark Project - Security Setup"
echo "==============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to create directory if it doesn't exist
create_dir() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        print_status $GREEN "✅ Created directory: $1"
    fi
}

# Function to set secure file permissions
set_secure_permissions() {
    local file=$1
    if [ -f "$file" ]; then
        chmod 600 "$file"
        print_status $GREEN "✅ Set secure permissions (600) for: $file"
    fi
}

# Function to install pre-commit hook
install_pre_commit_hook() {
    local hooks_dir=".git/hooks"
    local hook_file="$hooks_dir/pre-commit"
    local script_file="scripts/pre-commit-hook.sh"
    
    # Create hooks directory if it doesn't exist
    create_dir "$hooks_dir"
    
    # Copy pre-commit hook
    if [ -f "$script_file" ]; then
        cp "$script_file" "$hook_file"
        chmod +x "$hook_file"
        print_status $GREEN "✅ Installed pre-commit security hook"
    else
        print_status $RED "❌ Pre-commit hook script not found: $script_file"
        return 1
    fi
}

# Function to install pre-push hook
install_pre_push_hook() {
    local hooks_dir=".git/hooks"
    local hook_file="$hooks_dir/pre-push"
    
    cat > "$hook_file" << 'EOF'
#!/bin/bash
# Ark Project - Pre-push Security Check
# Additional security validation before pushing

set -e

echo "🔒 Ark Project - Pre-push Security Check"
echo "========================================"

# Run pre-commit hook as well
if [ -f ".git/hooks/pre-commit" ]; then
    .git/hooks/pre-commit
fi

# Additional checks for push
echo "✅ Pre-push security check completed"
EOF

    chmod +x "$hook_file"
    print_status $GREEN "✅ Installed pre-push security hook"
}

# Function to set up secrets file
setup_secrets_file() {
    local secrets_file="secrets.env"
    
    if [ ! -f "$secrets_file" ]; then
        print_status $YELLOW "⚠️  Secrets file $secrets_file not found"
        print_status $YELLOW "   Please create it manually with your secrets"
        return 1
    fi
    
    # Set secure permissions
    set_secure_permissions "$secrets_file"
    
    # Check if file is in .gitignore
    if [ -f ".gitignore" ]; then
        if grep -q "$secrets_file" ".gitignore"; then
            print_status $GREEN "✅ Secrets file is properly excluded in .gitignore"
        else
            print_status $RED "❌ CRITICAL: Secrets file not in .gitignore!"
            print_status $RED "   Add '$secrets_file' to .gitignore immediately"
        fi
    else
        print_status $RED "❌ .gitignore file not found!"
    fi
}

# Function to check for existing secrets in git history
check_git_history() {
    print_status $BLUE "🔍 Checking Git history for secrets..."
    
    # Check for common secret patterns in git history
    local secret_patterns=(
        "sk-[a-zA-Z0-9]{20,}"
        "pk_[a-zA-Z0-9]{20,}"
        "AIza[a-zA-Z0-9]{35}"
        "ghp_[a-zA-Z0-9]{36}"
        "gho_[a-zA-Z0-9]{36}"
        "ghu_[a-zA-Z0-9]{36}"
        "ghs_[a-zA-Z0-9]{36}"
        "ghr_[a-zA-Z0-9]{36}"
    )
    
    local secrets_found=false
    
    for pattern in "${secret_patterns[@]}"; do
        if git log --all --full-history -- "$pattern" >/dev/null 2>&1; then
            print_status $RED "🚨 CRITICAL: Secret pattern found in Git history: $pattern"
            secrets_found=true
        fi
    done
    
    if [ "$secrets_found" = true ]; then
        print_status $RED "❌ Secrets found in Git history!"
        print_status $RED "   Use 'git filter-repo' to remove them completely"
        print_status $RED "   Example: git filter-repo --invert-paths --path secrets.env"
        return 1
    else
        print_status $GREEN "✅ No secrets found in Git history"
    fi
}

# Function to create security documentation
create_security_docs() {
    local security_file="SECURITY.md"
    
    if [ ! -f "$security_file" ]; then
        cat > "$security_file" << 'EOF'
# Security Guidelines - Ark Project

## 🔒 Secret Management

### Secrets File
- All secrets are stored in `secrets.env`
- This file is excluded from Git via `.gitignore`
- File permissions should be 600 (owner read/write only)

### Adding New Secrets
1. Add the secret to `secrets.env`
2. Use the secret in code via `utils.secret_loader.get_secret()`
3. Never hardcode secrets in source code
4. Update this documentation if needed

### Emergency Procedures
If secrets are accidentally committed:
1. Immediately revoke the compromised secrets
2. Use `git filter-repo` to remove from history
3. Generate new secrets
4. Update all systems using the old secrets

## 🛡️ Security Checks

### Pre-commit Hook
- Automatically checks for secrets in staged files
- Validates file permissions
- Prevents committing sensitive data

### Pre-push Hook
- Additional security validation before pushing
- Runs pre-commit checks plus push-specific validations

## 🔐 Best Practices

1. **Never commit secrets** - Use environment variables
2. **Rotate secrets regularly** - Set up rotation schedule
3. **Monitor for leaks** - Use security scanning tools
4. **Limit access** - Only give secrets to those who need them
5. **Backup securely** - Store backup copies encrypted

## 🚨 Incident Response

1. **Immediate Action**
   - Revoke compromised secrets
   - Remove from Git history
   - Generate new secrets

2. **Investigation**
   - Determine scope of exposure
   - Identify affected systems
   - Document lessons learned

3. **Prevention**
   - Update security procedures
   - Enhance monitoring
   - Train team members

## 📞 Emergency Contacts

- Security Lead: [Add contact]
- System Administrator: [Add contact]
- Incident Response Team: [Add contact]

---
*Last updated: $(date)*
EOF

        print_status $GREEN "✅ Created security documentation: $security_file"
    fi
}

# Function to validate current setup
validate_setup() {
    print_status $BLUE "🔍 Validating security setup..."
    
    local validation_passed=true
    
    # Check if secrets file exists and has proper permissions
    if [ -f "secrets.env" ]; then
        local permissions=$(stat -c "%a" "secrets.env" 2>/dev/null || stat -f "%Lp" "secrets.env" 2>/dev/null)
        if [ "$permissions" != "600" ]; then
            print_status $RED "❌ Secrets file has insecure permissions: $permissions"
            validation_passed=false
        else
            print_status $GREEN "✅ Secrets file has secure permissions"
        fi
    else
        print_status $YELLOW "⚠️  Secrets file not found (create manually)"
    fi
    
    # Check if pre-commit hook is installed
    if [ -f ".git/hooks/pre-commit" ] && [ -x ".git/hooks/pre-commit" ]; then
        print_status $GREEN "✅ Pre-commit security hook installed"
    else
        print_status $RED "❌ Pre-commit security hook not installed"
        validation_passed=false
    fi
    
    # Check if .gitignore excludes secrets
    if [ -f ".gitignore" ] && grep -q "secrets.env" ".gitignore"; then
        print_status $GREEN "✅ Secrets file properly excluded in .gitignore"
    else
        print_status $RED "❌ Secrets file not excluded in .gitignore"
        validation_passed=false
    fi
    
    if [ "$validation_passed" = true ]; then
        print_status $GREEN "✅ Security setup validation passed"
    else
        print_status $RED "❌ Security setup validation failed"
        return 1
    fi
}

# Main installation function
main() {
    print_status $BLUE "🚀 Starting Ark Project security setup..."
    
    # Check if we're in a git repository
    if [ ! -d ".git" ]; then
        print_status $RED "❌ Not in a Git repository"
        print_status $RED "   Please run 'git init' first"
        exit 1
    fi
    
    # Install hooks
    install_pre_commit_hook
    install_pre_push_hook
    
    # Set up secrets file
    setup_secrets_file
    
    # Check Git history
    check_git_history
    
    # Create security documentation
    create_security_docs
    
    # Validate setup
    validate_setup
    
    print_status $GREEN "🎉 Security setup completed successfully!"
    print_status $GREEN "   Your Ark Project is now protected against secret leaks"
    
    echo ""
    print_status $BLUE "📋 Next steps:"
    print_status $BLUE "   1. Add your actual secrets to secrets.env"
    print_status $BLUE "   2. Test the security hooks with a test commit"
    print_status $BLUE "   3. Review SECURITY.md for best practices"
    print_status $BLUE "   4. Set up regular secret rotation"
}

# Run main function
main "$@" 