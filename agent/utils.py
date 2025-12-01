"""Utility functions for the business agent."""
import os
import subprocess
from typing import Optional, Dict


def get_repository_context() -> Dict[str, Optional[str]]:
    """
    Detect Git repository root and extract project name.

    Returns:
        Dictionary with 'project_name' and 'repository_path' keys.
        If not in a Git repository, returns 'global' project with None path.

    Examples:
        >>> get_repository_context()
        {'project_name': 'business-agent', 'repository_path': '/Users/.../business-agent'}

        >>> get_repository_context()  # Outside a repo
        {'project_name': 'global', 'repository_path': None}
    """
    try:
        # Try to find git root
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=2  # Prevent hanging
        )

        if result.returncode == 0:
            repo_path = result.stdout.strip()
            project_name = os.path.basename(repo_path)
            return {
                'project_name': project_name,
                'repository_path': repo_path
            }
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        # Git not available or command failed
        pass

    # Not in a git repo - return global context
    return {
        'project_name': 'global',
        'repository_path': None
    }


def get_project_name() -> str:
    """Get the current project name (repository name or 'global')."""
    context = get_repository_context()
    return context['project_name']


def get_repository_path() -> Optional[str]:
    """Get the current repository path, or None if not in a repository."""
    context = get_repository_context()
    return context['repository_path']
