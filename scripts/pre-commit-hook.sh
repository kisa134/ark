#!/bin/bash
# Ark Project - Pre-commit Security Hook
# Embodied Digital Organism - Sanctuary Security
#
# This hook prevents committing secrets and sensitive data
# Must be installed in .git/hooks/pre-commit

set -e

echo "🔒 Ark Project - Security Pre-commit Check"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if file contains secrets
check_file_for_secrets() {
    local file=$1
    local secrets_found=false
    
    # Patterns that indicate secrets
    local secret_patterns=(
        "api_key"
        "api_secret"
        "password"
        "token"
        "secret"
        "private_key"
        "private_key_id"
        "client_secret"
        "access_token"
        "refresh_token"
        "bearer_token"
        "auth_token"
        "session_key"
        "encryption_key"
        "master_key"
        "root_password"
        "admin_password"
        "database_password"
        "ssh_key"
        "private_key"
        "certificate"
        "pem"
        "p12"
        "pfx"
        "keystore"
        "jwt_secret"
        "signing_key"
        "encryption_key"
    )
    
    # Check each pattern
    for pattern in "${secret_patterns[@]}"; do
        if grep -i -q "$pattern" "$file"; then
            # Check if it's a real secret (not just a variable name)
            if grep -i -q "$pattern.*=" "$file" || grep -i -q "$pattern.*:" "$file"; then
                print_status $RED "🚨 SECURITY ALERT: Potential secret found in $file"
                print_status $RED "   Pattern: $pattern"
                secrets_found=true
            fi
        fi
    done
    
    # Check for actual secret values (base64, hex, etc.)
    if grep -q "sk-[a-zA-Z0-9]{20,}" "$file" || \
       grep -q "pk_[a-zA-Z0-9]{20,}" "$file" || \
       grep -q "AIza[a-zA-Z0-9]{35}" "$file" || \
       grep -q "ghp_[a-zA-Z0-9]{36}" "$file" || \
       grep -q "gho_[a-zA-Z0-9]{36}" "$file" || \
       grep -q "ghu_[a-zA-Z0-9]{36}" "$file" || \
       grep -q "ghs_[a-zA-Z0-9]{36}" "$file" || \
       grep -q "ghr_[a-zA-Z0-9]{36}" "$file"; then
        print_status $RED "🚨 CRITICAL: Actual secret value found in $file"
        secrets_found=true
    fi
    
    return $([ "$secrets_found" = true ] && echo 1 || echo 0)
}

# Function to check file permissions
check_file_permissions() {
    local file=$1
    
    # Check if file has insecure permissions
    local permissions=$(stat -c "%a" "$file" 2>/dev/null || stat -f "%Lp" "$file" 2>/dev/null)
    
    if [ "$permissions" != "600" ] && [ "$permissions" != "400" ]; then
        print_status $YELLOW "⚠️  Warning: $file has permissions $permissions (should be 600 or 400)"
    fi
}

# Function to check for secrets files
check_for_secrets_files() {
    local secrets_files=(
        "secrets.env"
        "secrets.private"
        ".env.secrets"
        ".env.private"
        ".secrets"
        ".private"
        "*.pem"
        "*.key"
        "*.crt"
        "*.p12"
        "*.pfx"
        "id_rsa*"
        "id_ed25519*"
        "*.pub"
    )
    
    for pattern in "${secrets_files[@]}"; do
        for file in $pattern; do
            if [ -f "$file" ]; then
                print_status $RED "🚨 CRITICAL: Secrets file $file is being committed!"
                print_status $RED "   This file should NEVER be committed to Git"
                return 1
            fi
        done
    done
}

# Function to check for hardcoded secrets
check_for_hardcoded_secrets() {
    local staged_files=$(git diff --cached --name-only)
    local secrets_found=false
    
    for file in $staged_files; do
        if [ -f "$file" ]; then
            # Skip binary files
            if file "$file" | grep -q "text"; then
                if check_file_for_secrets "$file"; then
                    secrets_found=true
                fi
            fi
        fi
    done
    
    return $([ "$secrets_found" = true ] && echo 1 || echo 0)
}

# Function to check for database files
check_for_database_files() {
    local db_files=(
        "*.db"
        "*.sqlite"
        "*.sqlite3"
        "data/ark_memory.db"
    )
    
    for pattern in "${db_files[@]}"; do
        for file in $pattern; do
            if [ -f "$file" ]; then
                print_status $YELLOW "⚠️  Warning: Database file $file is being committed"
                print_status $YELLOW "   Consider if this is necessary"
            fi
        done
    done
}

# Function to check for log files
check_for_log_files() {
    local log_files=(
        "*.log"
        "logs/"
        "log/"
    )
    
    for pattern in "${log_files[@]}"; do
        for file in $pattern; do
            if [ -f "$file" ] || [ -d "$file" ]; then
                print_status $YELLOW "⚠️  Warning: Log file/directory $file is being committed"
                print_status $YELLOW "   Logs should typically be excluded from version control"
            fi
        done
    done
}

# Main security checks
main() {
    local exit_code=0
    
    print_status $GREEN "🔍 Running security checks..."
    
    # Check for secrets files
    if check_for_secrets_files; then
        exit_code=1
    fi
    
    # Check for hardcoded secrets
    if check_for_hardcoded_secrets; then
        exit_code=1
    fi
    
    # Check for database files
    check_for_database_files
    
    # Check for log files
    check_for_log_files
    
    # Check file permissions
    local staged_files=$(git diff --cached --name-only)
    for file in $staged_files; do
        if [ -f "$file" ]; then
            check_file_permissions "$file"
        fi
    done
    
    # Final status
    if [ $exit_code -eq 0 ]; then
        print_status $GREEN "✅ Security check passed"
        print_status $GREEN "   No secrets or sensitive data detected"
    else
        print_status $RED "❌ Security check failed"
        print_status $RED "   Please remove secrets before committing"
        print_status $RED "   Use 'git reset HEAD' to unstage files"
    fi
    
    return $exit_code
}

# Run main function
main "$@" 