"""Packaging and unpacking for .clawpack files."""

import os
import json
import tarfile
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field


class Manifest(BaseModel):
    """Lobster package manifest."""
    name: str = Field(..., description="Lobster name")
    namespace: str = Field(..., description="Namespace (username or organization)")
    version: str = Field(..., description="Version (semver)")
    description: str = Field(default="", description="Short description")
    author: str = Field(default="", description="Author name")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    files: List[str] = Field(default_factory=list, description="Files included in package")
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, data: str) -> "Manifest":
        """Load from JSON string."""
        return cls(**json.loads(data))


class PackageError(Exception):
    """Package operation error."""
    pass


REQUIRED_FILES = ["SOUL.md", "AGENTS.md", "IDENTITY.md"]
OPTIONAL_FILES = ["README.md", "LICENSE", ".clawignore"]


def validate_lobster_directory(path: Path) -> tuple[bool, List[str]]:
    """Validate a lobster directory has all required files.
    
    Returns:
        Tuple of (is_valid, missing_files)
    """
    missing = []
    for required in REQUIRED_FILES:
        if not (path / required).exists():
            missing.append(required)
    return len(missing) == 0, missing


def get_lobster_files(path: Path, ignore_patterns: Optional[List[str]] = None) -> List[Path]:
    """Get all files to include in package, respecting ignore patterns.
    
    Args:
        path: Lobster directory path
        ignore_patterns: List of glob patterns to ignore
    
    Returns:
        List of file paths to include
    """
    ignore_patterns = ignore_patterns or [
        "*.clawpack",
        "__pycache__",
        "*.pyc",
        ".git",
        ".gitignore",
        ".DS_Store",
        "node_modules",
        ".env",
        ".venv",
        "venv",
    ]
    
    files = []
    for item in path.rglob("*"):
        if item.is_file():
            # Check if file should be ignored
            relative = item.relative_to(path)
            should_ignore = False
            
            for pattern in ignore_patterns:
                if relative.match(pattern) or any(
                    part.match(pattern) for part in relative.parents
                ):
                    should_ignore = True
                    break
            
            if not should_ignore:
                files.append(relative)
    
    return sorted(files)


def create_manifest(
    path: Path,
    namespace: str,
    name: str,
    version: str,
    description: str = "",
    author: str = "",
    tags: Optional[List[str]] = None,
) -> Manifest:
    """Create manifest from lobster directory."""
    files = [str(f) for f in get_lobster_files(path)]
    
    return Manifest(
        name=name,
        namespace=namespace,
        version=version,
        description=description,
        author=author,
        tags=tags or [],
        files=files,
    )


def pack(
    source_path: Path,
    output_path: Optional[Path] = None,
    namespace: Optional[str] = None,
    name: Optional[str] = None,
    version: str = "0.1.0",
    description: str = "",
    author: str = "",
    tags: Optional[List[str]] = None,
) -> Path:
    """Pack a lobster directory into a .clawpack file.
    
    Args:
        source_path: Path to lobster directory
        output_path: Output file path (default: <name>-<version>.clawpack in parent dir)
        namespace: Namespace for the package
        name: Package name (default: directory name)
        version: Version string
        description: Package description
        author: Author name
        tags: List of tags
    
    Returns:
        Path to created package file
    
    Raises:
        PackageError: If validation fails or packaging error occurs
    """
    source_path = Path(source_path).resolve()
    
    if not source_path.exists():
        raise PackageError(f"Source path does not exist: {source_path}")
    
    if not source_path.is_dir():
        raise PackageError(f"Source path must be a directory: {source_path}")
    
    # Validate required files
    is_valid, missing = validate_lobster_directory(source_path)
    if not is_valid:
        raise PackageError(
            f"Missing required files: {', '.join(missing)}. "
            f"A valid lobster must include: {', '.join(REQUIRED_FILES)}"
        )
    
    # Determine name
    pkg_name = name or source_path.name
    
    # Determine output path
    if output_path is None:
        output_path = source_path.parent / f"{pkg_name}-{version}.clawpack"
    else:
        output_path = Path(output_path)
    
    # Create manifest
    manifest = create_manifest(
        path=source_path,
        namespace=namespace or "local",
        name=pkg_name,
        version=version,
        description=description,
        author=author,
        tags=tags,
    )
    
    # Create package
    try:
        with tarfile.open(output_path, "w:gz") as tar:
            # Add manifest
            manifest_json = manifest.to_json().encode("utf-8")
            import io
            manifest_info = tarfile.TarInfo(name="manifest.json")
            manifest_info.size = len(manifest_json)
            tar.addfile(manifest_info, io.BytesIO(manifest_json))
            
            # Add all files
            for file_path in get_lobster_files(source_path):
                full_path = source_path / file_path
                tar.add(full_path, arcname=str(file_path))
        
        return output_path
    except Exception as e:
        raise PackageError(f"Failed to create package: {e}")


def unpack(package_path: Path, output_dir: Optional[Path] = None) -> tuple[Path, Manifest]:
    """Unpack a .clawpack file.
    
    Args:
        package_path: Path to .clawpack file
        output_dir: Output directory (default: current directory)
    
    Returns:
        Tuple of (extracted_directory, manifest)
    
    Raises:
        PackageError: If unpacking fails
    """
    package_path = Path(package_path).resolve()
    
    if not package_path.exists():
        raise PackageError(f"Package file does not exist: {package_path}")
    
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir).resolve()
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with tarfile.open(package_path, "r:gz") as tar:
            # Extract manifest first
            manifest_member = tar.getmember("manifest.json")
            manifest_file = tar.extractfile(manifest_member)
            if manifest_file is None:
                raise PackageError("Could not read manifest.json from package")
            
            manifest = Manifest.from_json(manifest_file.read().decode("utf-8"))
            
            # Determine extract directory
            extract_dir = output_dir / f"{manifest.name}-{manifest.version}"
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract all files
            for member in tar.getmembers():
                if member.name == "manifest.json":
                    continue
                tar.extract(member, extract_dir)
            
            return extract_dir, manifest
    except tarfile.TarError as e:
        raise PackageError(f"Invalid package file: {e}")
    except Exception as e:
        raise PackageError(f"Failed to unpack: {e}")


def inspect(package_path: Path) -> Manifest:
    """Inspect a .clawpack file without extracting.
    
    Args:
        package_path: Path to .clawpack file
    
    Returns:
        Package manifest
    """
    package_path = Path(package_path).resolve()
    
    if not package_path.exists():
        raise PackageError(f"Package file does not exist: {package_path}")
    
    try:
        with tarfile.open(package_path, "r:gz") as tar:
            manifest_member = tar.getmember("manifest.json")
            manifest_file = tar.extractfile(manifest_member)
            if manifest_file is None:
                raise PackageError("Could not read manifest.json from package")
            
            return Manifest.from_json(manifest_file.read().decode("utf-8"))
    except Exception as e:
        raise PackageError(f"Failed to inspect package: {e}")


def init_lobster(
    path: Path,
    name: str,
    description: str = "",
    author: str = "",
) -> List[Path]:
    """Initialize a new lobster directory with template files.
    
    Args:
        path: Directory to initialize
        name: Lobster name
        description: Short description
        author: Author name
    
    Returns:
        List of created files
    """
    path = Path(path).resolve()
    path.mkdir(parents=True, exist_ok=True)
    
    created = []
    
    # SOUL.md - Core personality and behavior
    soul_content = f"""# {name} - SOUL

## Identity
{name} is an AI agent designed for specific tasks.

## Purpose
<!-- Describe what this agent is designed to do -->
{description}

## Personality Traits
- Professional and helpful
- Detail-oriented
- Adaptive to user needs

## Communication Style
- Clear and concise
- Uses appropriate technical terminology
- Provides context when helpful

## Capabilities
<!-- List the main capabilities of this agent -->
- Task 1
- Task 2
- Task 3

## Limitations
<!-- Describe what this agent should NOT do -->
- Cannot perform actions outside its scope
- Requires human oversight for critical decisions

## Created
Author: {author}
Date: {datetime.now().strftime("%Y-%m-%d")}
"""
    
    soul_path = path / "SOUL.md"
    soul_path.write_text(soul_content, encoding="utf-8")
    created.append(soul_path)
    
    # AGENTS.md - Technical configuration
    agents_content = f"""# {name} - AGENTS

## Model Configuration
```yaml
model: gpt-4
temperature: 0.7
max_tokens: 2000
```

## Tools
<!-- List tools this agent uses -->
```yaml
tools:
  - name: tool_name
    description: What this tool does
```

## Prompts
<!-- Define system and user prompts -->

### System Prompt
```
You are {name}, an AI assistant. {description}
```

### Context Rules
- Always verify information before acting
- Ask for clarification when needed
- Maintain professional tone

## Knowledge Base
<!-- Reference to knowledge files or external resources -->
- docs/
- data/

## Workflow
<!-- Describe the typical workflow -->
1. Understand user intent
2. Gather necessary context
3. Execute task
4. Validate results
"""
    
    agents_path = path / "AGENTS.md"
    agents_path.write_text(agents_content, encoding="utf-8")
    created.append(agents_path)
    
    # IDENTITY.md - Identity and branding
    identity_content = f"""# {name} - IDENTITY

## Display Name
{name}

## Description
{description or "A versatile AI agent for various tasks."}

## Version
0.1.0

## Author
{author or "Anonymous"}

## Tags
<!-- Categorization tags -->
- ai-agent
- assistant

## Icon
<!-- Optional: Path to icon file or emoji -->
🦞

## License
MIT

## Repository
<!-- Optional: Link to source repository -->

## Documentation
<!-- Optional: Link to documentation -->

## Support
<!-- Optional: Support contact or link -->
"""
    
    identity_path = path / "IDENTITY.md"
    identity_path.write_text(identity_content, encoding="utf-8")
    created.append(identity_path)
    
    # README.md - User documentation
    readme_content = f"""# {name}

{description}

## Overview

This is an OpenClaw "Lobster" - a configurable AI agent designed for specific tasks.

## Files

- `SOUL.md` - Core personality and behavior definition
- `AGENTS.md` - Technical configuration and tools
- `IDENTITY.md` - Identity metadata and branding

## Installation

```bash
claw pull <namespace>/{name}:<version>
```

## Usage

<!-- Describe how to use this agent -->

## Configuration

<!-- Describe configuration options -->

## License

See IDENTITY.md for license information.
"""
    
    readme_path = path / "README.md"
    readme_path.write_text(readme_content, encoding="utf-8")
    created.append(readme_path)
    
    return created
