"""Dependency-free checks for the Claude Web marketplace payload.

Run with: python -m unittest discover -s tests/marketplace -v
No ARTEMIS imports, device, credentials, or pytest fixtures are needed.
"""

import ast
import json
from pathlib import Path
import re
import tempfile
import unittest
from shutil import copytree


ROOT = Path(__file__).resolve().parents[2]


class ClaudeMarketplaceTests(unittest.TestCase):
    def setUp(self):
        self.marketplace = json.loads(
            (ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
        )
        self.entry = self.marketplace["plugins"][0]
        self.plugin = ROOT / self.entry["source"]
        self.manifest = json.loads(
            (self.plugin / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
        )
        self.skills = self.plugin / self.manifest["skills"]

    def test_marketplace_identity_and_owner(self):
        self.assertEqual(self.marketplace["name"], "artemis-marketplace")
        self.assertEqual(self.marketplace["owner"]["name"], "osa822630-droid")
        self.assertEqual(len(self.marketplace["plugins"]), 1)

    def test_local_source_is_inside_repository(self):
        self.assertTrue(self.entry["source"].startswith("./"))
        self.assertTrue(self.plugin.resolve().is_relative_to(ROOT))
        self.assertTrue(self.plugin.is_dir())

    def test_plugin_metadata_matches_listing(self):
        self.assertEqual(self.manifest["name"], "artemis")
        self.assertEqual(self.manifest["name"], self.entry["name"])
        self.assertEqual(self.manifest["version"], self.entry["version"])
        self.assertRegex(self.manifest["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(self.manifest["license"], "Apache-2.0")
        self.assertTrue(self.manifest["description"])

    def test_skills_are_discoverable_with_required_frontmatter(self):
        self.assertTrue(self.manifest["skills"].startswith("./"))
        self.assertTrue(self.skills.resolve().is_relative_to(self.plugin.resolve()))
        skills = list(self.skills.glob("*/SKILL.md"))
        self.assertTrue(skills)
        for path in skills:
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"))
            metadata = text.split("---", 2)[1]
            name = re.search(r"^name: (.+)$", metadata, re.MULTILINE)
            description = re.search(r"^description: (.+)$", metadata, re.MULTILINE)
            self.assertIsNotNone(name)
            self.assertIsNotNone(description)
            self.assertEqual(name[1], path.parent.name)
            self.assertRegex(name[1], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertLessEqual(len(description[1]), 1024)

    def test_installed_skills_and_links_are_self_contained(self):
        # Simulate a client copying only the plugin source, without the repo.
        with tempfile.TemporaryDirectory() as directory:
            installed = copytree(self.plugin, Path(directory) / "artemis")
            for path in (installed / self.manifest["skills"]).rglob("*.md"):
                self.assertFalse(path.is_symlink())
                text = path.read_text(encoding="utf-8")
                for link in re.findall(r"\]\(([^)]+)\)", text):
                    if "://" in link or link.startswith("#"):
                        continue
                    target = (path.parent / link.split("#", 1)[0]).resolve()
                    self.assertTrue(target.is_relative_to(installed.resolve()), link)
                    self.assertTrue(target.is_file(), link)

    def test_no_implicit_local_execution_or_fake_mcp_endpoint(self):
        for key in ("mcpServers", "hooks", "commands"):
            self.assertNotIn(key, self.manifest)
            self.assertNotIn(key, self.entry)
        self.assertFalse(list(self.plugin.rglob(".mcp.json")))
        self.assertFalse((self.plugin / "hooks").exists())
        self.assertFalse((self.plugin / "commands").exists())

    def test_documented_tools_exist_in_server_without_importing_runtime(self):
        names = set()
        for path in (ROOT / "mcp_server/tools").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            names.update(
                node.name
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name.startswith("mobile_")
            )
        referenced = set()
        for path in self.skills.rglob("*.md"):
            referenced.update(re.findall(r"\bmobile_[a-z_]+\b", path.read_text(encoding="utf-8")))
        self.assertTrue(referenced)
        self.assertLessEqual(referenced, names)

    def test_skill_covers_unconnected_web_sessions_and_evidence(self):
        text = "\n".join(path.read_text(encoding="utf-8") for path in self.skills.rglob("*.md"))
        for expected in (
            "No ARTEMIS tools",
            "not run",
            "localhost",
            "Do not claim",
            "conversation_id",
            "background monitoring",
        ):
            self.assertIn(expected, text)

    def test_web_instructions_are_linked_and_use_fork(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/claude-web-marketplace.md", readme)
        guide = (ROOT / "docs/claude-web-marketplace.md").read_text(encoding="utf-8")
        self.assertIn("Add marketplace", guide)
        self.assertIn("https://github.com/osa822630-droid/artemis", guide)
        self.assertIn("artemis-marketplace", guide)
        self.assertIn("localhost", guide)


if __name__ == "__main__":
    unittest.main()
