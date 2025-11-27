# Secret Management

ApiLinker provides enterprise-grade secret management with support for multiple cloud secret storage providers. This feature enables you to securely store and retrieve API credentials without hardcoding them in configuration files.

## Supported Providers

- **HashiCorp Vault**: Enterprise secret management with KV v1/v2 support.
- **AWS Secrets Manager**: AWS native secret storage with automatic rotation.
- **Azure Key Vault**: Azure native secret management with managed identity support.
- **Google Secret Manager**: GCP native secret storage with workload identity.
- **Environment Variables**: Fallback for development.

## Configuration

Configure the secret provider in your YAML configuration:

```yaml
secrets:
  provider: vault  # or aws, azure, gcp, env
  vault:
    url: "http://localhost:8200"
    token: "hvs.CAESI..."
    mount_point: "secret"
    kv_version: 2
```

## Usage

Reference secrets using the `secret://` prefix in your source/target configuration:

```yaml
source:
  auth:
    type: api_key
    key: "secret://apilinker/source-api-key"
```

## Security Best Practices

1. **Use Managed Identities**: Prefer workload identity/IAM roles over static credentials.
2. **Enable Rotation**: Use automatic rotation for production secrets.
3. **Least Privilege**: Grant only necessary permissions.
4. **Never Commit Secrets**: Always use secret references.
