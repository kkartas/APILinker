"""
Secret Management Integration Examples

This script demonstrates how to use APILinker's secret management integration
with various providers (Vault, AWS, Azure, GCP).

Run with: python examples/secret_management_demo.py
"""

import os
import logging
from apilinker.core.secrets import (
    SecretManager,
    SecretManagerConfig,
    SecretProvider,
    RotationStrategy,
    VaultSecretProvider,
    AWSSecretsProvider,
    AzureKeyVaultProvider,
    GCPSecretProvider,
    SecretNotFoundError,
    SecretAccessError,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_vault_secrets():
    """Example: Using HashiCorp Vault for secret management"""
    print("\n=== HashiCorp Vault Example ===\n")

    try:
        config = SecretManagerConfig(
            provider=SecretProvider.VAULT,
            vault_config={
                "url": "http://localhost:8200",
                "token": os.environ.get("VAULT_TOKEN", "root"),
                "mount_point": "secret",
                "kv_version": 2,
                "cache_ttl_seconds": 300,
            },
            rotation_strategy=RotationStrategy.MANUAL,
        )

        secret_manager = SecretManager(config)

        # Store a secret
        logger.info("Storing API key in Vault...")
        secret_manager.set_secret(
            "apilinker/demo-api-key",
            {"key": "sk_test_1234567890", "environment": "development"},
            metadata={"tags": {"app": "apilinker", "env": "dev"}},
        )

        # Retrieve the secret
        logger.info("Retrieving API key from Vault...")
        secret_value = secret_manager.get_secret("apilinker/demo-api-key")
        logger.info(f"Retrieved: {secret_value}")

        # List secrets
        logger.info("Listing secrets with prefix 'apilinker/'...")
        secrets = secret_manager.list_secrets(prefix="apilinker/")
        for secret in secrets:
            logger.info(f"  - {secret.name} (version: {secret.version})")

        # Rotate secret
        logger.info("Rotating secret...")
        metadata = secret_manager.rotate_secret(
            "apilinker/demo-api-key",
            rotation_function=lambda: {
                "key": "sk_test_new_key",
                "environment": "development",
            },
        )
        logger.info(f"Rotated to version: {metadata.version}")

        # Clean up
        logger.info("Deleting secret...")
        secret_manager.delete_secret("apilinker/demo-api-key")

        print("\n✅ Vault example completed successfully!\n")

    except ImportError:
        print("❌ hvac package not installed. Install with: pip install hvac")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_aws_secrets():
    """Example: Using AWS Secrets Manager"""
    print("\n=== AWS Secrets Manager Example ===\n")

    try:
        config = SecretManagerConfig(
            provider=SecretProvider.AWS,
            aws_config={
                "region_name": "us-east-1",
                # Uses IAM role if running on EC2/ECS
                # Or uses AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY env vars
                "cache_ttl_seconds": 300,
            },
            rotation_strategy=RotationStrategy.AUTO,
        )

        secret_manager = SecretManager(config)

        # Store a secret
        logger.info("Storing database credentials in AWS Secrets Manager...")
        secret_manager.set_secret(
            "apilinker/demo-db-creds",
            {
                "username": "apilinker_user",
                "password": "demo_password_123",
                "host": "db.example.com",
                "port": 5432,
            },
        )

        # Retrieve the secret
        logger.info("Retrieving database credentials...")
        secret_value = secret_manager.get_secret("apilinker/demo-db-creds")
        logger.info(f"Retrieved username: {secret_value.get('username')}")

        # Clean up
        logger.info("Deleting secret...")
        secret_manager.delete_secret("apilinker/demo-db-creds")

        print("\n✅ AWS Secrets Manager example completed successfully!\n")

    except ImportError:
        print("❌ boto3 package not installed. Install with: pip install boto3")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_azure_keyvault():
    """Example: Using Azure Key Vault"""
    print("\n=== Azure Key Vault Example ===\n")

    try:
        vault_url = os.environ.get(
            "AZURE_VAULT_URL", "https://mykeyvault.vault.azure.net/"
        )

        config = SecretManagerConfig(
            provider=SecretProvider.AZURE,
            azure_config={
                "vault_url": vault_url,
                # Uses DefaultAzureCredential (managed identity, Azure CLI, etc.)
                "cache_ttl_seconds": 300,
            },
            rotation_strategy=RotationStrategy.MANUAL,
        )

        secret_manager = SecretManager(config)

        # Store a secret
        logger.info("Storing API token in Azure Key Vault...")
        secret_manager.set_secret(
            "apilinker-demo-token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            metadata={"tags": {"environment": "development", "app": "apilinker"}},
        )

        # Retrieve the secret
        logger.info("Retrieving API token...")
        secret_value = secret_manager.get_secret("apilinker-demo-token")
        logger.info(f"Retrieved: {secret_value[:20]}...")

        # Clean up
        logger.info("Deleting secret...")
        secret_manager.delete_secret("apilinker-demo-token")

        print("\n✅ Azure Key Vault example completed successfully!\n")

    except ImportError:
        print("❌ azure-keyvault-secrets package not installed.")
        print("Install with: pip install azure-keyvault-secrets azure-identity")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_gcp_secret_manager():
    """Example: Using Google Secret Manager"""
    print("\n=== Google Secret Manager Example ===\n")

    try:
        project_id = os.environ.get("GCP_PROJECT_ID", "my-project")

        config = SecretManagerConfig(
            provider=SecretProvider.GCP,
            gcp_config={
                "project_id": project_id,
                # Uses Application Default Credentials
                "cache_ttl_seconds": 300,
            },
            rotation_strategy=RotationStrategy.MANUAL,
        )

        secret_manager = SecretManager(config)

        # Store a secret
        logger.info("Storing OAuth credentials in Google Secret Manager...")
        secret_manager.set_secret(
            "apilinker-demo-oauth",
            {
                "client_id": "demo_client_id",
                "client_secret": "demo_client_secret",
                "redirect_uri": "https://app.example.com/callback",
            },
        )

        # Retrieve the secret
        logger.info("Retrieving OAuth credentials...")
        secret_value = secret_manager.get_secret("apilinker-demo-oauth")
        logger.info(f"Retrieved client_id: {secret_value.get('client_id')}")

        # Clean up
        logger.info("Deleting secret...")
        secret_manager.delete_secret("apilinker-demo-oauth")

        print("\n✅ Google Secret Manager example completed successfully!\n")

    except ImportError:
        print("❌ google-cloud-secret-manager package not installed.")
        print("Install with: pip install google-cloud-secret-manager")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_with_apilinker():
    """Example: Using secrets with APILinker"""
    print("\n=== APILinker Integration Example ===\n")

    from apilinker import ApiLinker

    # Create ApiLinker with secret management
    linker = ApiLinker(
        secret_manager_config={
            "provider": "env",  # Use environment variables as fallback
        },
        source_config={
            "type": "rest",
            "base_url": "https://api.example.com",
            "auth": {
                "type": "api_key",
                # This will try to get API_KEY from environment variable
                "api_key": "secret://API_KEY",
                "header": "X-API-Key",
            },
        },
        log_level="INFO",
    )

    logger.info("✅ APILinker configured with secret management!")
    logger.info("Secrets will be automatically resolved from the configured provider.")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("APILinker Secret Management Examples")
    print("=" * 60)

    # Note: These examples require the respective cloud provider credentials
    # and services to be set up. They will fail gracefully if not available.

    print("\n⚠️  Note: These examples require cloud provider credentials.")
    print(
        "Set up the appropriate environment variables or credentials before running.\n"
    )

    # Run examples
    example_with_apilinker()

    # Uncomment to run provider-specific examples:
    # example_vault_secrets()
    # example_aws_secrets()
    # example_azure_keyvault()
    # example_gcp_secret_manager()

    print("\n" + "=" * 60)
    print("For production use:")
    print("1. Use cloud provider managed identities (recommended)")
    print("2. Enable automatic rotation where supported")
    print("3. Follow least-privilege access patterns")
    print("4. Never commit secrets to version control")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
