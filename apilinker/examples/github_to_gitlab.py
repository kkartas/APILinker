"""
Example: Migrating issues from GitHub to GitLab using ApiLinker.

This script demonstrates how to use ApiLinker to fetch issues from a GitHub repository
and create corresponding issues in GitLab.

Prerequisites:
- A GitHub personal access token with repo scope
- A GitLab personal access token with api scope
- ApiLinker installed

Usage:
    python github_to_gitlab.py --config config.yaml

Example config (github_to_gitlab_config.yaml):
```yaml
source:
  type: rest
  base_url: https://api.github.com
  auth:
    type: bearer
    token: ${GITHUB_TOKEN}
  endpoints:
    list_issues:
      path: /repos/{owner}/{repo}/issues
      method: GET
      params:
        state: all
        per_page: 100
      pagination:
        page_param: page
        max_pages: 10
      headers:
        Accept: application/vnd.github.v3+json

target:
  type: rest
  base_url: https://gitlab.com/api/v4
  auth:
    type: bearer
    token: ${GITLAB_TOKEN}
  endpoints:
    create_issue:
      path: /projects/{project_id}/issues
      method: POST

mapping:
  - source: list_issues
    target: create_issue
    fields:
      - source: title
        target: title
      - source: body
        target: description
      - source: labels
        target: labels
        transform: github_labels_to_gitlab
      - source: state
        target: state
      - source: user.login
        target: custom_fields.github_user

schedule:
  type: once
  datetime: "2025-07-14T15:00:00"

logging:
  level: INFO
  file: github_to_gitlab.log
```
"""

import argparse
import os
import sys
from typing import Any, Dict, List

from apilinker import ApiLinker


def github_labels_to_gitlab(labels: List[Dict[str, Any]]) -> List[str]:
    """
    Convert GitHub label objects to GitLab label strings.

    Args:
        labels: List of GitHub label objects with name and color

    Returns:
        List of label strings for GitLab
    """
    if not labels:
        return []

    # Extract just the label names from GitHub labels
    return [label["name"] for label in labels]


def main():
    """Run the GitHub to GitLab issue migration."""
    parser = argparse.ArgumentParser(description="Migrate issues from GitHub to GitLab")
    parser.add_argument("--config", "-c", required=True, help="Path to config file")
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Dry run without creating issues",
    )
    parser.add_argument(
        "--github-repo",
        help="GitHub repository in format owner/repo",
    )
    parser.add_argument(
        "--gitlab-project",
        help="GitLab project ID",
    )

    args = parser.parse_args()

    # Check for required environment variables
    if "GITHUB_TOKEN" not in os.environ:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)

    if "GITLAB_TOKEN" not in os.environ:
        print("Error: GITLAB_TOKEN environment variable not set")
        sys.exit(1)

    # Initialize ApiLinker with config
    linker = ApiLinker(config_path=args.config)

    # Register custom transformer for GitHub labels
    linker.mapper.register_transformer(
        "github_labels_to_gitlab", github_labels_to_gitlab
    )

    # Override GitHub repository if specified
    if args.github_repo:
        owner, repo = args.github_repo.split("/")
        # Update the endpoint path with the provided repository
        linker.source.endpoints["list_issues"].path = f"/repos/{owner}/{repo}/issues"

    # Override GitLab project if specified
    if args.gitlab_project:
        # Update the endpoint path with the provided project ID
        project_id = args.gitlab_project
        linker.target.endpoints["create_issue"].path = f"/projects/{project_id}/issues"

    # Print summary
    github_repo = (
        linker.source.endpoints["list_issues"]
        .path.split("/repos/")[1]
        .split("/issues")[0]
    )
    gitlab_project = (
        linker.target.endpoints["create_issue"]
        .path.split("/projects/")[1]
        .split("/issues")[0]
    )

    print(
        (
            "Migrating issues from GitHub repository: "
            f"{github_repo} to GitLab project ID: {gitlab_project}"
        )
    )

    if args.dry_run:
        print("DRY RUN MODE - No issues will be created in GitLab")

        # Fetch issues from GitHub
        source_data = linker.source.fetch_data("list_issues")

        # Map data according to field mappings
        mapped_data = linker.mapper.map_data("list_issues", "create_issue", source_data)

        print(f"\nFound {len(source_data)} GitHub issues")
        print("\nSample issues that would be created:")

        for i, issue in enumerate(mapped_data[:3]):
            print(f"\n--- Issue {i+1} ---")
            print(f"Title: {issue['title']}")
            print(f"Labels: {', '.join(issue.get('labels', []))}")
            print(f"State: {issue.get('state', 'open')}")
            description = issue.get("description", "")
            print(
                f"Description: {description[:100]}..."
                if len(description) > 100
                else f"Description: {description}"
            )

        if len(mapped_data) > 3:
            print(f"\n...and {len(mapped_data) - 3} more issues")

    else:
        # Perform the actual sync
        result = linker.sync()

        if result.success:
            print(f"Successfully migrated {result.count} issues from GitHub to GitLab")
        else:
            print("Migration failed with errors:")
            for error in result.errors:
                print(f"- {error}")


if __name__ == "__main__":
    main()
