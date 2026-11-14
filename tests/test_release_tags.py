"""tools/release_tags.py: which RELEASES.md entries get a tag, and on which
commit (14 Nov 2026)."""
import os, subprocess, sys, tempfile, shutil, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import release_tags as R


class Entries(unittest.TestCase):
    def test_ids_titles_and_skips(self):
        text = "\n".join(["# Releases", "## 2026-11-14-7: the ledger (tag pending)", "## 2026-11-14: a pause",
                          "## 2026-11-12 (tag pending): no id", "## 2026-11-13-2: one", "## 2026-11-13-2: two"])
        found, skipped = R.entries(text)
        self.assertEqual([(r, t) for r, t, _ in found], [("2026-11-14-7", "the ledger"), ("2026-11-14", "a pause")])
        self.assertEqual(len(skipped), 3)


class Commits(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(); self.cwd = os.getcwd(); os.chdir(self.dir)
        for c in (["init", "-q", "-b", "main"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            subprocess.run(["git", *c], check=True)

    def tearDown(self):
        os.chdir(self.cwd); shutil.rmtree(self.dir)

    def commit(self, text, msg):
        with open("RELEASES.md", "w") as f: f.write(text)
        subprocess.run(["git", "add", "RELEASES.md"], check=True)
        subprocess.run(["git", "commit", "-q", "-m", msg], check=True)
        return R.git("rev-parse", "HEAD").strip()

    def test_tag_lands_on_the_commit_that_added_the_entry(self):
        a = self.commit("# R\n## 2026-11-13: first\n", "a")
        b = self.commit("# R\n## 2026-11-14: second (tag pending)\n## 2026-11-13: first\n", "b")
        self.commit("# R\n## 2026-11-14: second (tag pending)\n## 2026-11-13: first\nmore\n", "c")
        subprocess.run(["git", "tag", "release-2026-11-13", a], check=True)
        todo, _ = R.plan()
        self.assertEqual(todo, [("release-2026-11-14", b, "second")])


if __name__ == "__main__":
    unittest.main()
