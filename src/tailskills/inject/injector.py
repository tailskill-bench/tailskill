"""
injector.py — Main orchestrator for variant task generation.

Usage:
    from tailskills.inject.injector import Injector
    injector = Injector(skillsbench_root="path/to/skillsbench", output_dir="generated-tasks")
    injector.generate("sales-pivot-analysis", "C1_nan_poison")
"""

import os
import shutil
from pathlib import Path

import yaml

from .dockerfile_patcher import DockerfilePatcher
from .test_augmentor import TestAugmentor


class Injector:
    """Orchestrates the generation of variant tasks from original SkillsBench tasks."""

    def __init__(self, skillsbench_root: str, output_dir: str, configs_dir: str | None = None):
        self.skillsbench_root = Path(skillsbench_root)
        self.output_dir = Path(output_dir)
        self.configs_dir = Path(configs_dir) if configs_dir else Path(__file__).parents[3] / "configs"

        self.tasks_dir = self.skillsbench_root / "tasks"
        self.variants_dir = self.configs_dir / "variants"

        # Load the task-variant matrix
        matrix_path = self.configs_dir / "task_variant_matrix.yaml"
        if matrix_path.exists():
            with open(matrix_path, "r", encoding="utf-8") as f:
                self.matrix = yaml.safe_load(f) or {}
        else:
            self.matrix = {}

    def generate(self, task_id: str, variant_id: str, force: bool = False) -> Path:
        """
        Generate a single variant task.

        Args:
            task_id: Original task ID (e.g. "sales-pivot-analysis")
            variant_id: Variant ID (e.g. "C1_nan_poison")
            force: If True, overwrite existing generated task

        Returns:
            Path to the generated variant task directory.
        """
        source_dir = self.tasks_dir / task_id
        if not source_dir.exists():
            raise FileNotFoundError(f"Original task not found: {source_dir}")

        # Load variant config
        variant_config = self._load_variant_config(variant_id)

        # Build output directory name: task_id--variant_id
        dest_name = f"{task_id}--{variant_id}"
        dest_dir = self.output_dir / dest_name

        if dest_dir.exists():
            if force:
                shutil.rmtree(dest_dir)
            else:
                raise FileExistsError(f"Variant task already exists: {dest_dir}. Use force=True to overwrite.")

        # Step 1: Copy original task directory
        print(f"[TailSkills] Copying {task_id} → {dest_name}")
        shutil.copytree(source_dir, dest_dir)

        # Step 2: Get task-specific params from matrix
        task_matrix = self._get_task_variant_params(task_id, variant_id)

        # Step 3: Copy the container-side injection script if needed
        injection_layer = variant_config.get("injection", {}).get("layer", "")
        if injection_layer == "data":
            self._copy_inject_script(dest_dir)

        # Step 4: Patch Dockerfile
        dockerfile_append = variant_config.get("dockerfile_append", "")
        if dockerfile_append:
            # Resolve template variables
            dockerfile_append = self._resolve_templates(dockerfile_append, task_matrix, variant_config)
            patcher = DockerfilePatcher(dest_dir / "environment" / "Dockerfile")
            patcher.append(dockerfile_append, variant_id, variant_config.get("description", ""))
            print(f"[TailSkills]   Dockerfile patched with {variant_id}")

        # Step 5: Add tail tests
        extra_test = variant_config.get("extra_test", "")
        if extra_test:
            augmentor = TestAugmentor(dest_dir / "tests")
            augmentor.add_tail_test(extra_test, variant_id)
            augmentor.patch_test_sh()
            print(f"[TailSkills]   Tail test added: {extra_test}")

        # Step 6: Update task.toml
        self._update_task_toml(dest_dir / "task.toml", variant_id, variant_config)
        print(f"[TailSkills]   task.toml updated with tail-variant tag")

        print(f"[TailSkills] DONE Generated: {dest_dir}")
        return dest_dir

    def generate_all_for_task(self, task_id: str, force: bool = False) -> list[Path]:
        """Generate all applicable variants for a given task."""
        task_entry = self.matrix.get("tasks", {}).get(task_id, {})
        applicable = task_entry.get("applicable_variants", [])

        results = []
        for variant_entry in applicable:
            if isinstance(variant_entry, dict):
                variant_id = list(variant_entry.keys())[0]
            else:
                variant_id = variant_entry
            try:
                path = self.generate(task_id, variant_id, force=force)
                results.append(path)
            except Exception as e:
                print(f"[TailSkills] ⚠️ Failed to generate {task_id}--{variant_id}: {e}")
        return results

    def generate_batch(self, force: bool = False) -> list[Path]:
        """Generate all variant tasks defined in the matrix."""
        all_results = []
        for task_id in self.matrix.get("tasks", {}):
            results = self.generate_all_for_task(task_id, force=force)
            all_results.extend(results)
        return all_results

    # ─── Private helpers ────────────────────────────────────────

    def _load_variant_config(self, variant_id: str) -> dict:
        config_path = self.variants_dir / f"{variant_id}.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Variant config not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _get_task_variant_params(self, task_id: str, variant_id: str) -> dict:
        """Get task-specific params for a variant from the matrix."""
        task_entry = self.matrix.get("tasks", {}).get(task_id, {})
        for v in task_entry.get("applicable_variants", []):
            if isinstance(v, dict) and variant_id in v:
                return v[variant_id]
        return {}

    def _copy_inject_script(self, dest_dir: Path):
        """Copy _tail_inject.py into the task's environment directory."""
        script_src = Path(__file__).parent / "_tail_inject.py"
        script_dst = dest_dir / "environment" / "_tail_inject.py"
        if script_src.exists():
            shutil.copy2(script_src, script_dst)

    def _resolve_templates(self, template: str, task_params: dict, variant_config: dict) -> str:
        """Resolve {placeholders} in Dockerfile append content."""
        merged = {**variant_config.get("injection", {}).get("params", {}), **task_params}
        for key, value in merged.items():
            template = template.replace(f"{{{key}}}", str(value))
        return template

    def _update_task_toml(self, toml_path: Path, variant_id: str, variant_config: dict):
        """Add tail-variant tags to task.toml."""
        with open(toml_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Simple tag injection — find the tags line and append
        tag = f'"tail-variant:{variant_id}"'
        category = variant_config.get("category", "unknown")

        if "tags = [" in content:
            content = content.replace("tags = [", f'tags = [{tag}, "tailskills", "category:{category}", ', 1)
        else:
            # If no tags line, add one in metadata section
            content = content.replace("[metadata]", f'[metadata]\ntags = [{tag}, "tailskills"]', 1)

        with open(toml_path, "w", encoding="utf-8") as f:
            f.write(content)
