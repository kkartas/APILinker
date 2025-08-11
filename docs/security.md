# Security Considerations

APILinker provides security features to ensure safe handling of API credentials and multi-user access. This document outlines security best practices and describes the available security features.

## Security Features

### Secure Credential Storage

APILinker provides optional encrypted storage for sensitive credentials (for development convenience; consider dedicated secret managers in production):

```python
# Configure secure credential storage
linker = ApiLinker(
    security_config={
        "master_password": "your-strong-password",  # Or use environment variable
        "credential_storage_path": "./credentials.enc"
    }
)

# Store credentials securely
linker.store_credential("github_api", {
    "token": "ghp_1234567890abcdefghijklmnopqrstuvwxyz",
    "expires_at": 1735689600  # Optional expiry timestamp
})

# Retrieve credentials
cred = linker.get_credential("github_api")
print(f"Token: {cred['token']}")
```

<!-- Custom request/response encryption is not supported. Use HTTPS and provider-recommended authentication. -->

### Multi-User Access Control

Set up role-based access control for multi-user environments:

```python
# Enable access control
linker = ApiLinker(
    security_config={
        "enable_access_control": True,
        "users": [
            {"username": "admin1", "role": "admin"},
            {"username": "operator1", "role": "operator"},
            {"username": "viewer1", "role": "viewer"}
        ]
    }
)

# Add users programmatically
user = linker.add_user("developer1", "developer")
print(f"API Key: {user['api_key']}")

# List users
users = linker.list_users()
```

### OAuth Enhancements

APILinker now supports additional OAuth flows:

- **PKCE Flow**: For mobile and single-page applications
- **Device Flow**: For devices with limited input capabilities

### Configuration File Security

When using configuration files, avoid including sensitive values directly. You have several options:

1. Use environment variable references as shown above
2. Keep separate configuration files for development and production
3. Use APILinker's secure credential storage
4. Store sensitive values in a secret management system

## OAuth Authentication Flows

### OAuth Client Credentials Flow

```yaml
auth:
  type: oauth2_client_credentials
  client_id: "your-client-id"
  client_secret: "${CLIENT_SECRET}"  # From environment variable
  token_url: "https://auth.example.com/oauth/token"
  scope: "read write"  # Optional
```

### OAuth PKCE Flow (for public clients)

For public clients that cannot securely store a client secret:

```python
from apilinker.core.auth import OAuth2PKCE

# Initialize auth config
pkce_config = auth_manager.configure_auth({
    "type": "oauth2_pkce",
    "client_id": "your-client-id",
    "redirect_uri": "http://localhost:8080/callback",
    "authorization_url": "https://auth.example.com/oauth/authorize",
    "token_url": "https://auth.example.com/oauth/token",
    "scope": "read write",  # Optional
    "storage_key": "my_oauth_pkce_creds"  # For secure storage
})

# Get authorization URL for user to visit
auth_url = auth_manager.get_pkce_authorization_url(pkce_config)
print(f"Visit this URL to authorize: {auth_url}")

# After receiving the authorization code from the redirect
auth_config = auth_manager.complete_pkce_flow(pkce_config, "authorization_code_from_redirect")

# Later, refresh the token when needed
auth_config = auth_manager.refresh_pkce_token(auth_config)
```

### OAuth Device Flow (for limited input devices)

For devices with limited input capabilities:

```python
from apilinker.core.auth import OAuth2DeviceFlow

# Initialize device flow
device_config = auth_manager.configure_auth({
    "type": "oauth2_device_flow",
    "client_id": "your-client-id",
    "device_authorization_url": "https://auth.example.com/oauth/device/code",
    "token_url": "https://auth.example.com/oauth/token",
    "storage_key": "my_device_flow_creds"  # For secure storage
})

# Start the device flow
device_config = auth_manager.start_device_flow(device_config)

# Show the user the verification code and URL
print(f"Please visit {device_config.verification_uri} and enter code: {device_config.user_code}")

# Poll for completion
import time
while True:
    completed, updated_config = auth_manager.poll_device_flow(device_config)
    if completed:
        print("Authorization complete!")
        device_config = updated_config
        break
    time.sleep(device_config.interval)  # Respect polling interval
```

### OAuth Token Refresh

When using OAuth, ApiLinker automatically handles token refreshing when tokens expire.

## Credential Management

### Environment Variables

Store API keys and tokens as environment variables rather than hardcoding them in your configuration files:

```yaml
auth:
  type: api_key
  header: X-API-Key
  key: ${MY_API_KEY}
```

In your Python code, you can set environment variables before running your script:

```python
import os
os.environ["MY_API_KEY"] = "your_api_key_here"  # Set this securely
```

### Secure Storage

For production environments, consider using:

- Environment variables set at the system or container level
- Secret management services like HashiCorp Vault or AWS Secrets Manager
- Encrypted configuration files with restricted access

## Authentication Methods

ApiLinker supports several authentication methods, each with its own security considerations:

### API Key Authentication

```yaml
auth:
  type: api_key
  header: X-API-Key  # Header name varies by API
  key: ${API_KEY}
```

**Security tips:**
- Rotate API keys regularly
- Use keys with the minimum required permissions
- Set IP restrictions on API keys when supported by the service

### Bearer Token Authentication

```yaml
auth:
  type: bearer
  token: ${BEARER_TOKEN}
```

**Security tips:**
- Use short-lived tokens when possible
- Implement token refresh logic for long-running processes
- Store refresh tokens with additional security measures

### Basic Authentication

```yaml
auth:
  type: basic
  username: ${API_USERNAME}
  password: ${API_PASSWORD}
```

**Security tips:**
- Only use over HTTPS connections
- Use application-specific passwords when available
- Avoid using your main account credentials

### OAuth 2.0

```yaml
auth:
  type: oauth2
  client_id: ${CLIENT_ID}
  client_secret: ${CLIENT_SECRET}
  token_url: "https://api.example.com/oauth/token"
  scope: "read write"
```

**Security tips:**
- Store client secrets securely
- Request only the scopes you need
- Implement proper token storage and refresh logic

## Network Security

### Request Timeouts

Set appropriate timeouts to prevent hanging connections:

```yaml
source:
  timeout: 30  # Timeout in seconds
```

## Data Protection

### HTTPS

Always use HTTPS for API endpoints to ensure data is encrypted in transit.

<!-- Built-in rate limiting is not provided by ApiLinker. Use provider-side limits and backoff/retry as needed. -->

## Audit Logging

Enable audit logging for security-relevant events:

```yaml
logging:
  level: INFO
  security_audit: true
  file: "apilinker_audit.log"
```

## Data Handling

### Sensitive Data Filtering

When logging API responses, sensitive data can be filtered:

```yaml
logging:
  filter_fields:
    - "password"
    - "token"
    - "secret"
    - "credit_card"
```

### Data Validation

Always validate data before processing:

```yaml
mapping:
  - source: "get_user"
    target: "create_profile"
    validation:
      required_fields: ["id", "email"]
      email_fields: ["email"]
```

## Best Practices for Custom Plugins

When developing custom plugins:

1. Validate all inputs to prevent injection attacks
2. Do not log sensitive information
3. Handle exceptions properly to avoid information leakage
4. Follow the principle of least privilege when accessing resources

## Access Control for Multi-User Environments

For environments where multiple users need access to APILinker, you can enable role-based access control:

```yaml
security:
  enable_access_control: true
  users:
    - username: "admin1"
      role: "admin"
      api_key: "optional-predefined-api-key"
    - username: "viewer1"
      role: "viewer"
```

### Available Roles

- `admin`: Full access to all operations
- `operator`: Can run syncs and view results
- `developer`: Can modify configurations but not run syncs
- `viewer`: Can only view configurations and results

### Permission Management

Each role has a predefined set of permissions:

| Permission | Admin | Operator | Developer | Viewer |
|------------|-------|----------|-----------|--------|
| view_config | ✅ | ✅ | ✅ | ✅ |
| edit_config | ✅ | ❌ | ✅ | ❌ |
| run_sync | ✅ | ✅ | ❌ | ❌ |
| view_results | ✅ | ✅ | ✅ | ✅ |
| manage_users | ✅ | ❌ | ❌ | ❌ |
| manage_credentials | ✅ | ❌ | ❌ | ❌ |
| view_logs | ✅ | ✅ | ✅ | ❌ |
| access_analytics | ✅ | ✅ | ❌ | ❌ |

## Logging

Avoid logging sensitive information like API keys, tokens, or personal data. The ApiLinker logger is configured to avoid logging sensitive data by default.

For enhanced security, consider using a separate log file with restricted permissions:

```yaml
logging:
  level: INFO
  file: "/secure/path/apilinker.log"
```

## Security Configuration Example

A complete security-focused configuration might look like:

```yaml
source:
  type: rest
  base_url: "https://api.example.com"
  auth:
    type: oauth2
    client_id: ${CLIENT_ID}
    client_secret: ${CLIENT_SECRET}
    token_url: "https://api.example.com/oauth/token"
    scope: "read"
  timeout: 30
  retry:
    max_attempts: 3
    backoff_factor: 2

logging:
  level: INFO
  security_audit: true
  filter_fields:
    - "password"
    - "token"
    - "secret"
```

Remember that security is an ongoing process. Regularly review and update your security practices, and stay informed about security updates for ApiLinker and its dependencies.
