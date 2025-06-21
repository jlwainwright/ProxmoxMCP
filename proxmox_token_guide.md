# Guide to Creating Proxmox API Tokens

## Overview
This guide explains how to create API tokens for Proxmox VE, which are required for secure authentication with the Proxmox MCP tool.

## Steps to Create a Proxmox API Token

1. **Log in to the Proxmox Web Interface**
   - Open a web browser and navigate to your Proxmox server at `https://192.168.0.200:8006`
   - Log in with your credentials (e.g., username: `root@pam`, password: your-password)

2. **Navigate to API Tokens**
   - Click on your datacenter in the server view
   - Select "Permissions" from the menu
   - Click on "API Tokens"

3. **Create a New Token**
   - Click the "Add" button
   - Select the user (e.g., `root@pam`)
   - Enter a token ID (e.g., `mcp-token`)
   - Decide whether to check "Privilege Separation" (usually leave unchecked for full access)
   - Click "Create"

4. **Save Your Token Information**
   - Proxmox will display the token value **ONCE**
   - Copy both the token ID and token value
   - Store them securely - you won't be able to retrieve the token value again

5. **Configure Proxmox MCP**
   - Create a configuration file based on the example:
   ```json
   {
       "proxmox": {
           "host": "192.168.0.200",
           "port": 8006,
           "verify_ssl": false,
           "service": "PVE"
       },
       "auth": {
           "user": "root@pam",
           "token_name": "mcp-token",
           "token_value": "your-generated-token-value"
       },
       "logging": {
           "level": "INFO",
           "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
           "file": "proxmox_mcp.log"
       }
   }
   ```

## Security Best Practices

1. **Use Dedicated API Tokens**: Create specific tokens for each application or service.
2. **Limit Token Privileges**: Use privilege separation when possible.
3. **Secure Storage**: Never store token values in plain text in code repositories.
4. **Regular Rotation**: Periodically rotate your API tokens.
5. **Audit Usage**: Regularly review which tokens exist and revoke unused ones.

## Using Environment Variables (Alternative)

Instead of storing tokens in a config file, you can use environment variables:

```bash
export PROXMOX_USER="root@pam"
export PROXMOX_TOKEN_NAME="mcp-token"
export PROXMOX_TOKEN_VALUE="your-generated-token-value"
export PROXMOX_MCP_CONFIG="/path/to/config.json"
```

Then run the MCP server which will use these environment variables for authentication.