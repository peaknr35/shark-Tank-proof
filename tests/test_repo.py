import json
import os
import re
import unittest

from _load import ROOT, SKILLS_DIR

SKILLS = ["shark-board", "signal", "burn-test", "truth-serum", "prove-it",
          "litmus", "dealbreaker", "ground-truth", "straight-talk", "reality-check", "kill-or-build",
          "receipts", "handshake", "first-dollar"]
ABOUT = ("Fourteen free Claude skills that test a business before you launch it and get you to the first real yes: "
         "a board that disagrees with you, a competitor scout, a simulated buyer panel, pricing, the offer, a CFO, "
         "marketing, brand, operations, a launch test, the plan, an evidence ledger, pitches and funding. Free, MIT.")


def frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (m.group(1) if m else ""), text


EM = chr(0x2014)  # built in code so this file does not trip its own check


def text_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for f in files:
            if f.endswith((".md", ".py", ".json", ".txt")) or f in ("LICENSE", ".gitignore"):
                yield os.path.join(base, f)


class Repo(unittest.TestCase):
    def test_fourteen_skill_folders(self):
        found = sorted(d for d in os.listdir(SKILLS_DIR) if os.path.isfile(os.path.join(SKILLS_DIR, d, "SKILL.md")))
        self.assertEqual(found, sorted(SKILLS))

    def test_frontmatter_name_and_description(self):
        for s in SKILLS:
            fm, text = frontmatter(os.path.join(SKILLS_DIR, s, "SKILL.md"))
            self.assertIn("name: %s\n" % s, fm + "\n", s)
            self.assertRegex(fm, r"description: ", s)
            self.assertGreater(len(fm), 300, "%s description is too thin" % s)
            self.assertGreater(len(text.splitlines()), 60, s)

    def test_tools_named_in_skills_exist(self):
        for s in SKILLS:
            _, text = frontmatter(os.path.join(SKILLS_DIR, s, "SKILL.md"))
            for tool in re.findall(r"\$\{CLAUDE_SKILL_DIR\}/([\w.\-/]+\.(?:py|md))", text):
                self.assertTrue(os.path.exists(os.path.normpath(os.path.join(SKILLS_DIR, s, tool))), "%s: %s" % (s, tool))

    def test_plugin_manifests(self):
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json")) as fh:
            plugin = json.load(fh)
        self.assertEqual(plugin["name"], "shark-tank-proof")
        self.assertEqual(plugin["description"], ABOUT)
        self.assertEqual(plugin["license"], "MIT")
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json")) as fh:
            market = json.load(fh)
        self.assertEqual(market["name"], "shark-tank-proof")
        self.assertEqual(market["plugins"][0]["name"], "shark-tank-proof")
        self.assertEqual(market["plugins"][0]["source"], "./")

    def test_readme(self):
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
            readme = " ".join(fh.read().split())
        self.assertTrue(readme.startswith("# Shark Tank Proof"))
        for line in (
            "**A board that bites before investors do.**",
            "Fourteen Claude skills that test a business before you launch it, then get you to the first real yes. "
            "Free, MIT, no signup, no API key, nothing to connect.",
            "/plugin install shark-tank-proof@shark-tank-proof",
            "## Fine print",
            "Built on the Founder skill by Jake Schincariol",
        ):
            self.assertIn(line, readme)
        for s in SKILLS:
            self.assertIn("`skills/%s`" % s, readme)

    def test_every_skill_reads_the_rules(self):
        for s in SKILLS:
            _, text = frontmatter(os.path.join(SKILLS_DIR, s, "SKILL.md"))
            self.assertRegex(text, r"\$\{CLAUDE_SKILL_DIR\}/(\.\./receipts/)?rules\.md", s)

    def test_examples_parse(self):
        for rel in ("burn-test/example.json", "truth-serum/customer.example.json"):
            with open(os.path.join(SKILLS_DIR, rel), encoding="utf-8") as fh:
                json.load(fh)

    def test_no_em_dashes(self):
        for path in text_files():
            with open(path, encoding="utf-8") as fh:
                self.assertNotIn(EM, fh.read(), os.path.relpath(path, ROOT))


if __name__ == "__main__":
    unittest.main()
