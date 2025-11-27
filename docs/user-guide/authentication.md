# Authentication

ApiLinker supports a wide range of authentication methods to connect to various APIs.

## Supported Methods

### API Key

```yaml
auth:
  type: api_key
  key: your_key
  header: X-API-Key
```

### Bearer Token

```yaml
auth:
  type: bearer
  token: your_token
```

### Basic Auth

```yaml
auth:
  type: basic
  username: user
  password: pass
```

### OAuth2

ApiLinker supports Client Credentials flow and other OAuth2 patterns.

```yaml
auth:
  type: oauth2_client_credentials
  client_id: id
  client_secret: secret
  token_url: https://auth.example.com/token
```
