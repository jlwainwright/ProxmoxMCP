#!/bin/bash
# ProxmoxMCP Security Validation Script
# Checks configuration for common security issues

set -e

echo "🔒 ProxmoxMCP Security Validation"
echo "================================="
echo ""

CONFIG_FILE="config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ CRITICAL: config.json not found"
    echo "   Please ensure you have a configuration file in the current directory"
    exit 1
fi

echo "📁 Found configuration file: $CONFIG_FILE"
echo ""

# Check if jq is available for JSON parsing
if ! command -v jq &> /dev/null; then
    echo "⚠️  WARNING: jq not found, using basic text parsing"
    USE_JQ=false
else
    USE_JQ=true
fi

ISSUES_FOUND=0

echo "🔍 Checking for security issues..."
echo ""

# Check 1: Placeholder values
echo "1. Checking for placeholder values..."
if grep -q "CHANGE-THIS\|your-token\|example\|placeholder" "$CONFIG_FILE"; then
    echo "   ❌ CRITICAL: Placeholder values detected"
    echo "   Found: $(grep -o 'CHANGE-THIS[^"]*\|your-token[^"]*\|example[^"]*\|placeholder[^"]*' "$CONFIG_FILE" | head -3)"
    echo "   Action: Replace all placeholder values with actual configuration"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo "   ✅ No placeholder values found"
fi
echo ""

# Check 2: SSL verification
echo "2. Checking SSL verification settings..."
if $USE_JQ; then
    VERIFY_SSL=$(jq -r '.proxmox.verify_ssl' "$CONFIG_FILE")
    if [ "$VERIFY_SSL" = "false" ]; then
        echo "   ❌ CRITICAL: SSL verification disabled"
        echo "   Action: Set 'verify_ssl: true' in proxmox configuration"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo "   ✅ SSL verification enabled"
    fi
else
    if grep -q '"verify_ssl".*false' "$CONFIG_FILE"; then
        echo "   ❌ CRITICAL: SSL verification disabled"
        echo "   Action: Set 'verify_ssl: true' in proxmox configuration"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo "   ✅ SSL verification appears to be enabled"
    fi
fi
echo ""

# Check 3: Network binding
echo "3. Checking network binding configuration..."
if grep -q '"host".*"0\.0\.0\.0"' "$CONFIG_FILE"; then
    echo "   ⚠️  WARNING: Binding to all interfaces (0.0.0.0)"
    echo "   Recommendation: Use 127.0.0.1 or specific IP address"
    echo "   Risk: Exposes service to network attacks"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo "   ✅ Not binding to all interfaces"
fi
echo ""

# Check 4: Root user usage
echo "4. Checking for root user usage..."
if grep -q '"user".*"root@' "$CONFIG_FILE"; then
    echo "   ⚠️  WARNING: Using root user account"
    echo "   Recommendation: Create dedicated service account"
    echo "   Risk: Excessive privileges if compromised"
else
    echo "   ✅ Not using root user account"
fi
echo ""

# Check 5: JWT secret strength (if OAuth enabled)
echo "5. Checking JWT secret key strength..."
if $USE_JQ; then
    AUTH_ENABLED=$(jq -r '.authorization.enabled' "$CONFIG_FILE")
    if [ "$AUTH_ENABLED" = "true" ]; then
        SECRET_KEY=$(jq -r '.authorization.secret_key' "$CONFIG_FILE")
        if [ ${#SECRET_KEY} -lt 32 ]; then
            echo "   ❌ CRITICAL: JWT secret key too short (${#SECRET_KEY} characters)"
            echo "   Action: Generate secret key with at least 32 characters"
            ISSUES_FOUND=$((ISSUES_FOUND + 1))
        else
            echo "   ✅ JWT secret key meets minimum length requirement"
        fi
    else
        echo "   ℹ️  OAuth authorization disabled, skipping JWT secret check"
    fi
else
    if grep -q '"enabled".*true' "$CONFIG_FILE" && grep -q '"secret_key"' "$CONFIG_FILE"; then
        echo "   ⚠️  Cannot verify JWT secret strength without jq"
        echo "   Action: Ensure secret key is at least 32 characters"
    else
        echo "   ℹ️  OAuth authorization appears disabled"
    fi
fi
echo ""

# Check 6: Token expiry settings
echo "6. Checking token expiry configuration..."
if $USE_JQ; then
    AUTH_ENABLED=$(jq -r '.authorization.enabled' "$CONFIG_FILE")
    if [ "$AUTH_ENABLED" = "true" ]; then
        TOKEN_EXPIRY=$(jq -r '.authorization.token_expiry' "$CONFIG_FILE")
        if [ "$TOKEN_EXPIRY" -gt 14400 ]; then  # 4 hours
            echo "   ⚠️  WARNING: Token expiry too long (${TOKEN_EXPIRY} seconds)"
            echo "   Recommendation: Use 3600 seconds (1 hour) or less"
        else
            echo "   ✅ Token expiry within recommended range"
        fi
    fi
else
    echo "   ℹ️  Cannot verify token expiry without jq"
fi
echo ""

# Check 7: Logging configuration
echo "7. Checking logging configuration..."
if grep -q '"file".*null' "$CONFIG_FILE"; then
    echo "   ⚠️  WARNING: File logging disabled"
    echo "   Recommendation: Enable file logging for security monitoring"
else
    echo "   ✅ File logging appears to be configured"
fi
echo ""

# Summary
echo "🎯 Security Validation Summary"
echo "=============================="
if [ $ISSUES_FOUND -eq 0 ]; then
    echo "✅ No critical security issues detected"
    echo "   Your configuration appears to follow security best practices"
    echo ""
    echo "📋 Final checklist:"
    echo "   - Ensure Proxmox server has valid SSL certificate"
    echo "   - Verify API token has appropriate permissions only"
    echo "   - Configure firewall rules for network access"
    echo "   - Monitor logs for security events"
    echo "   - Set up token rotation schedule"
elif [ $ISSUES_FOUND -eq 1 ]; then
    echo "⚠️  1 security issue found"
    echo "   Please address the issue above before production deployment"
else
    echo "❌ $ISSUES_FOUND security issues found"
    echo "   Please address all issues above before production deployment"
fi

echo ""
echo "📖 For complete security guidance, see:"
echo "   https://github.com/canvrno/ProxmoxMCP/blob/main/SECURITY.md"

if [ $ISSUES_FOUND -gt 0 ]; then
    exit 1
fi

exit 0