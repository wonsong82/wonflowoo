"""Init command - Initialize Choisor project configuration

Full initialization workflow:
1. Validate project structure prerequisites
2. Create .choisor/ directory with configuration files
3. Discover available skills from .claude/skills/
4. Set up inter-stage contract validation
5. Generate initialization report
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..config import ConfigLoader, ProjectConfig


# Built-in templates with default values
TEMPLATES = {
    "spring-migration": {
        "name": "",
        "description": "Spring MVC to Spring Boot migration project",
        "feature": {
            "id_prefix": "FEAT-",
            "gap_suffix": "GAP",
            "skip_gap_features": True,
        },
        "domain": {
            "skip_domains": [],
            "priority_map": {
                "P0-Foundation": [],
                "P1-Hub": [],
                "P2-Core": [],
                "P3-Supporting": [],
            },
        },
        "paths": {
            "source_base": "",
            "target_base": "",
            "java_src_path": "src/main/java",
            "mapper_path": "src/main/resources/mapper",
            "java_package": "",
        },
    },
    "custom": {
        "name": "",
        "description": "",
        "feature": {
            "id_prefix": "FEAT-",
            "gap_suffix": "GAP",
            "skip_gap_features": True,
        },
        "domain": {
            "skip_domains": [],
            "priority_map": {},
        },
        "paths": {
            "source_base": "",
            "target_base": "",
            "java_src_path": "src/main/java",
            "mapper_path": "src/main/resources/mapper",
            "java_package": "",
        },
    },
    "hallain-tft": {
        "name": "hallain-tft",
        "description": "Hallain TFT Legacy Migration Project",
        "feature": {
            "id_prefix": "FEAT-",
            "gap_suffix": "GAP",
            "skip_gap_features": True,
        },
        "domain": {
            "skip_domains": [],
            "priority_map": {
                "P0-Foundation": ["CM"],
                "P1-Hub": ["PA"],
                "P2-Core": ["MM", "QM"],
                "P3-Supporting": ["RP"],
            },
        },
        "paths": {
            "source_base": "hallain",
            "target_base": "next-hallain",
            "java_src_path": "src/main/java",
            "mapper_path": "src/main/resources/mapper",
            "java_package": "com/hallain",
        },
    },
}

# Default config values
DEFAULT_CONFIG = {
    "provider": "anthropic",
    "max_sessions": 1,
    "max_allowed_phase": "phase4",
}


def validate_prerequisites(project_root: Path) -> Dict[str, Any]:
    """Validate project structure prerequisites.

    Returns:
        Validation result with status and details
    """
    result = {
        "valid": True,
        "checks": {},
        "errors": [],
        "warnings": [],
    }

    # Check .claude/ directory
    claude_dir = project_root / ".claude"
    result["checks"]["claude_dir"] = claude_dir.exists()
    if not claude_dir.exists():
        result["valid"] = False
        result["errors"].append("Claude Code not initialized. Run 'claude init' first.")

    # Check .claude/skills/ directory
    skills_dir = project_root / ".claude" / "skills"
    result["checks"]["skills_dir"] = skills_dir.exists()
    if not skills_dir.exists():
        result["valid"] = False
        result["errors"].append("Skills directory not found. Create .claude/skills/ first.")

    # Check .choisor/ directory (warning only)
    choisor_dir = project_root / ".choisor"
    result["checks"]["choisor_exists"] = choisor_dir.exists()
    if choisor_dir.exists():
        result["warnings"].append(".choisor/ already exists. Use --force to reinitialize.")

    return result


def discover_skills(project_root: Path) -> Dict[str, Any]:
    """Discover available skills from .claude/skills/.

    Returns:
        Skill discovery result with counts and details
    """
    skills_dir = project_root / ".claude" / "skills"
    if not skills_dir.exists():
        return {"count": 0, "skills": [], "stages": []}

    # Find all SKILL.md files matching s{stage}-{phase}-* pattern
    skill_pattern = re.compile(r"s(\d+)-(\d+)-([^/]+)")
    skills = []
    stages = set()

    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            match = skill_pattern.match(skill_dir.name)
            if match:
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    stage = int(match.group(1))
                    phase = int(match.group(2))
                    name = match.group(3)
                    skills.append({
                        "name": skill_dir.name,
                        "stage": stage,
                        "phase": phase,
                        "short_name": name,
                    })
                    stages.add(stage)

    return {
        "count": len(skills),
        "skills": sorted(skills, key=lambda x: (x["stage"], x["phase"])),
        "stages": sorted(stages),
    }


def check_contracts(project_root: Path) -> Dict[str, Any]:
    """Check for inter-stage contracts file.

    Returns:
        Contract check result
    """
    contracts_path = project_root / ".claude" / "skills" / "common" / "inter-stage-contracts.yaml"
    return {
        "found": contracts_path.exists(),
        "path": str(contracts_path) if contracts_path.exists() else None,
    }


def create_directory_structure(project_root: Path) -> Dict[str, Any]:
    """Create .choisor/ directory structure.

    Returns:
        Creation result with list of created paths
    """
    choisor_dir = project_root / ".choisor"
    created = []

    # Directories to create
    directories = [
        choisor_dir,
        choisor_dir / "tasks",
        choisor_dir / "sessions",
        choisor_dir / "instructions",
        choisor_dir / "logs" / "sessions",
        choisor_dir / "logs" / "instructions",
    ]

    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
        created.append(str(dir_path.relative_to(project_root)))

    # Create empty JSON files
    json_files = [
        (choisor_dir / "tasks" / "tasks.json", []),
        (choisor_dir / "sessions" / "sessions.json", []),
    ]

    for file_path, content in json_files:
        with open(file_path, "w") as f:
            json.dump(content, f, indent=2)
        created.append(str(file_path.relative_to(project_root)))

    return {"created": created}


def render_template(template_content: str, variables: Dict[str, Any]) -> str:
    """Render template with variable substitution.

    Args:
        template_content: Template string with {{variable}} placeholders
        variables: Dictionary of variable values

    Returns:
        Rendered string
    """
    result = template_content
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))
    return result


def load_template_file(template_name: str) -> Optional[str]:
    """Load template file content.

    Args:
        template_name: Template filename (e.g., "config.yaml.template")

    Returns:
        Template content or None if not found
    """
    # Look in choisor-init/templates/ directory
    template_paths = [
        Path(__file__).parent.parent.parent / "choisor-init" / "templates" / template_name,
        Path(__file__).parent.parent / "templates" / template_name,
    ]

    for template_path in template_paths:
        if template_path.exists():
            return template_path.read_text()

    return None


def create_config_file(
    project_root: Path,
    config_vars: Dict[str, Any]
) -> Path:
    """Create config.yaml from template.

    Args:
        project_root: Project root path
        config_vars: Configuration variables

    Returns:
        Path to created config file
    """
    template_content = load_template_file("config.yaml.template")

    if template_content:
        # Render template with variables
        content = render_template(template_content, config_vars)
    else:
        # Fallback to embedded template
        content = f"""# Choisor Configuration
assignment:
  enabled: true
  delay: null
  stale_timeout: 10

auto_commit:
  enabled: true
  commit_on_completion: true

limit_monitor:
  ignore_limit: true

daemon:
  refresh_interval: 10

provider: "{config_vars.get('provider', 'anthropic')}"
default_model: "claude-opus-4-5-20251101"

claude_code:
  max_sessions: {config_vars.get('max_sessions', 1)}
  max_output_tokens: 65536
  default_model: "claude-opus-4-5-20251101"
  default_model_bedrock: "global.anthropic.claude-opus-4-5-20251101-v1:0"

current:
  stage: "stage1"
  phase: "phase1"

phase_gate:
  max_allowed_phase: "{config_vars.get('max_allowed_phase', 'phase4')}"
  auto_to_max: true

parallel:
  enabled: true
  pairs:
    - ["s4-03", "s4-04"]
  max_parallel_sessions: 10

paths:
  skills_root: ".claude/skills"
  contracts_path: ".claude/skills/common/inter-stage-contracts.yaml"

work_scope:
  enabled_domains: null
  enabled_stages: null

priority:
  algorithm: "weighted_score"
  weights:
    dependency_ready: 0.5
    priority_score: 0.3
    estimated_duration: 0.2
"""

    config_path = project_root / ".choisor" / "config.yaml"
    config_path.write_text(content)
    return config_path


def create_workflow_file(
    project_root: Path,
    workflow_vars: Dict[str, Any]
) -> Path:
    """Create workflow.yaml from template.

    Args:
        project_root: Project root path
        workflow_vars: Workflow variables

    Returns:
        Path to created workflow file
    """
    template_content = load_template_file("workflow.yaml.template")

    if template_content:
        content = render_template(template_content, workflow_vars)
    else:
        # Fallback to minimal workflow
        content = f"""# Choisor Workflow Definition
name: "{workflow_vars.get('name', 'project')}-workflow"
version: "1.0.0"

progression:
  phase_gate:
    enabled: true
    strict_mode: true
"""

    workflow_path = project_root / ".choisor" / "workflow.yaml"
    workflow_path.write_text(content)
    return workflow_path


def create_readme(project_root: Path, init_result: Dict[str, Any]) -> Path:
    """Create README.md for .choisor/ directory.

    Args:
        project_root: Project root path
        init_result: Initialization result data

    Returns:
        Path to created README
    """
    timestamp = datetime.now().isoformat()
    skills_count = init_result.get("skills", {}).get("count", 0)
    template = init_result.get("template", "unknown")

    content = f"""# Choisor Configuration

Initialized: {timestamp}
Template: {template}
Skills discovered: {skills_count}

## Directory Structure

```
.choisor/
├── config.yaml           # Runtime configuration
├── project.yaml          # Project properties
├── workflow.yaml         # Workflow definitions
├── tasks/
│   └── tasks.json        # Task list and states
├── sessions/
│   └── sessions.json     # Session pool state
├── instructions/         # Instruction files for tasks
└── logs/
    ├── sessions/         # Session execution logs
    └── instructions/     # Instruction generation logs
```

## Commands

- `/choisor status` - Display project status
- `/choisor scan --stage N` - Scan for tasks
- `/choisor query --status pending` - Query tasks
- `/choisor manual-assign FEAT-XX-001` - Assign specific feature

## Configuration Files

- **config.yaml**: Runtime settings (sessions, phase gate, parallel execution)
- **project.yaml**: Project properties (name, paths, domains, stages)
- **workflow.yaml**: Workflow definitions (progression rules, dependencies)
"""

    readme_path = project_root / ".choisor" / "README.md"
    readme_path.write_text(content)
    return readme_path


def generate_init_report(
    project_root: Path,
    template: str,
    name: str,
    validation: Dict[str, Any],
    skills: Dict[str, Any],
    contracts: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate initialization report.

    Returns:
        Complete initialization report
    """
    return {
        "initialization_report": {
            "timestamp": datetime.now().isoformat(),
            "project": {
                "name": name,
                "template": template,
                "root": str(project_root),
            },
            "validation": {
                "claude_dir": validation["checks"].get("claude_dir", False),
                "skills_dir": validation["checks"].get("skills_dir", False),
            },
            "skills_discovered": {
                "count": skills["count"],
                "stages": skills["stages"],
            },
            "contracts": contracts,
            "status": "SUCCESS",
        }
    }


def handle_init(
    project_root: Path,
    template: str = "spring-migration",
    name: Optional[str] = None,
    source_base: Optional[str] = None,
    target_base: Optional[str] = None,
    java_package: Optional[str] = None,
    force: bool = False,
    provider: str = "anthropic",
    max_sessions: int = 1,
    max_allowed_phase: str = "phase4",
) -> Dict[str, Any]:
    """Initialize Choisor project configuration.

    Full initialization workflow:
    1. Validate prerequisites
    2. Create directory structure
    3. Generate configuration files
    4. Discover skills
    5. Check contracts
    6. Generate report

    Args:
        project_root: Project root path
        template: Template name
        name: Project name (defaults to directory name)
        source_base: Legacy source directory
        target_base: Generated code directory
        java_package: Java package path
        force: Overwrite existing configuration
        provider: API provider
        max_sessions: Maximum parallel sessions
        max_allowed_phase: Phase gate limit

    Returns:
        Result dictionary with status and report
    """
    print("\n=== Choisor Project Initialization ===\n")

    # Step 1: Validate prerequisites
    print("Validating project structure...")
    validation = validate_prerequisites(project_root)

    for check, passed in validation["checks"].items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check.replace('_', ' ')}")

    if not validation["valid"]:
        for error in validation["errors"]:
            print(f"\nError: {error}")
        return {
            "success": False,
            "errors": validation["errors"],
        }

    # Check for existing .choisor/
    if validation["checks"].get("choisor_exists") and not force:
        for warning in validation["warnings"]:
            print(f"\n⚠ {warning}")
        return {
            "success": False,
            "error": ".choisor/ already exists. Use --force to reinitialize.",
        }

    # Step 2: Validate template
    print(f"\nTemplate: {template}")
    if template not in TEMPLATES:
        available = ", ".join(TEMPLATES.keys())
        return {
            "success": False,
            "error": f"Unknown template: {template}. Available: {available}",
        }

    # Step 3: Prepare configuration
    template_data = TEMPLATES[template].copy()
    project_name = name or project_root.name
    template_data["name"] = project_name
    print(f"Project name: {project_name}")

    # Override paths if provided
    if source_base:
        template_data["paths"]["source_base"] = source_base
        print(f"Source base: {source_base}")
    if target_base:
        template_data["paths"]["target_base"] = target_base
        print(f"Target base: {target_base}")
    if java_package:
        template_data["paths"]["java_package"] = java_package
        print(f"Java package: {java_package}")

    # Step 4: Create directory structure
    print("\nCreating .choisor/ structure...")
    dir_result = create_directory_structure(project_root)
    for path in dir_result["created"][:5]:  # Show first 5
        print(f"  ✓ {path}")
    if len(dir_result["created"]) > 5:
        print(f"  ... and {len(dir_result['created']) - 5} more")

    # Step 5: Create configuration files
    loader = ConfigLoader(project_root)

    # Create project.yaml
    config = ProjectConfig(**template_data)
    loader.save_project(config)
    print(f"  ✓ project.yaml created")

    # Create config.yaml
    config_vars = {
        "provider": provider,
        "max_sessions": max_sessions,
        "max_allowed_phase": max_allowed_phase,
    }
    create_config_file(project_root, config_vars)
    print(f"  ✓ config.yaml created")

    # Create workflow.yaml
    workflow_vars = {"name": project_name}
    create_workflow_file(project_root, workflow_vars)
    print(f"  ✓ workflow.yaml created")

    # Step 6: Discover skills
    print("\nDiscovering skills...")
    skills = discover_skills(project_root)
    print(f"  Found {skills['count']} skills across {len(skills['stages'])} stages")

    # Step 7: Check contracts
    print("\nSetting up contracts...")
    contracts = check_contracts(project_root)
    if contracts["found"]:
        print(f"  ✓ inter-stage-contracts.yaml found")
    else:
        print(f"  ⚠ Contracts file not found (contract validation will be skipped)")

    # Step 8: Generate report and README
    report = generate_init_report(
        project_root, template, project_name,
        validation, skills, contracts
    )

    init_result = {
        "template": template,
        "skills": skills,
    }
    create_readme(project_root, init_result)
    print(f"  ✓ README.md created")

    # Final output
    print("\n=== Initialization Complete ===\n")
    print("Next steps:")
    print("  1. Review .choisor/project.yaml configuration")
    print("  2. Run '/choisor scan --stage 1' to discover tasks")
    print("  3. Run '/choisor status' to view project status")
    print()

    return {
        "success": True,
        "template": template,
        "name": project_name,
        "path": str(project_root / ".choisor"),
        "report": report,
    }


def handle_show_templates() -> Dict[str, Any]:
    """Show available templates.

    Returns:
        Dictionary with template information
    """
    print("\n=== Available Templates ===\n")

    for name, template in TEMPLATES.items():
        print(f"  {name}:")
        desc = template.get("description", "No description")
        print(f"    Description: {desc}")

        # Show default paths if set
        paths = template.get("paths", {})
        if paths.get("source_base"):
            print(f"    Source base: {paths['source_base']}")
        if paths.get("target_base"):
            print(f"    Target base: {paths['target_base']}")
        print()

    print("Usage:")
    print("  /choisor init --template <name>")
    print("  /choisor init --template spring-migration --name my-project")
    print()

    return {
        "success": True,
        "templates": list(TEMPLATES.keys()),
    }


def handle_validate_project(project_root: Path) -> Dict[str, Any]:
    """Validate existing project configuration.

    Args:
        project_root: Project root path

    Returns:
        Validation result
    """
    print("\n=== Validating Project Configuration ===\n")

    # Check prerequisites
    validation = validate_prerequisites(project_root)
    print("Prerequisites:")
    for check, passed in validation["checks"].items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check.replace('_', ' ')}")

    # Check configuration files
    print("\nConfiguration files:")
    config_files = [
        ".choisor/config.yaml",
        ".choisor/project.yaml",
        ".choisor/workflow.yaml",
    ]

    for config_file in config_files:
        path = project_root / config_file
        if path.exists():
            try:
                with open(path) as f:
                    yaml.safe_load(f)
                print(f"  ✓ {config_file} (valid YAML)")
            except yaml.YAMLError as e:
                print(f"  ✗ {config_file} (invalid YAML: {e})")
        else:
            print(f"  ✗ {config_file} (not found)")

    # Discover skills
    print("\nSkills:")
    skills = discover_skills(project_root)
    print(f"  Found {skills['count']} skills across stages: {skills['stages']}")

    # Check contracts
    print("\nContracts:")
    contracts = check_contracts(project_root)
    if contracts["found"]:
        print(f"  ✓ inter-stage-contracts.yaml found")
    else:
        print(f"  ⚠ Contracts file not found")

    print()

    return {
        "success": validation["valid"],
        "validation": validation,
        "skills": skills,
        "contracts": contracts,
    }
