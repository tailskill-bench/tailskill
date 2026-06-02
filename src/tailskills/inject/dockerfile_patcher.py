"""
dockerfile_patcher.py — Appends variant injection commands to a task's Dockerfile.
"""

from pathlib import Path


class DockerfilePatcher:
    """Patches a Dockerfile by appending variant injection commands at the end."""

    def __init__(self, dockerfile_path: str | Path):
        self.path = Path(dockerfile_path)
        if not self.path.exists():
            raise FileNotFoundError(f"Dockerfile not found: {self.path}")

    def append(self, commands: str, variant_id: str, description: str = ""):
        """
        Append injection commands to the Dockerfile.

        Args:
            commands: Shell commands to append (each line becomes a Dockerfile instruction)
            variant_id: Variant identifier for the comment block
            description: Human-readable description
        """
        with open(self.path, "r", encoding="utf-8") as f:
            content = f.read()

        # Ensure trailing newline
        if not content.endswith("\n"):
            content += "\n"

        # Build the patch block
        patch = f"""
# ============================================
# TailSkills Variant: {variant_id}
# {description.strip().replace(chr(10), ' ')}
# ============================================
{commands.strip()}
"""
        content += patch

        with open(self.path, "w", encoding="utf-8") as f:
            f.write(content)

    def has_variant_patch(self, variant_id: str) -> bool:
        """Check if a variant has already been applied."""
        with open(self.path, "r", encoding="utf-8") as f:
            return f"TailSkills Variant: {variant_id}" in f.read()
