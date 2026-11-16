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

    def test_a_word_id_is_an_id(self):
        found, skipped = R.entries("## 2026-11-16-comp3: the cap replayed (tag pending)\n## 2026-11-15-span-held: held")
        self.assertEqual([r for r, _, _ in found], ["2026-11-16-comp3", "2026-11-15-span-held"])
        self.assertEqual(skipped, [])


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

    def test_a_renumbered_entry_is_tagged_on_the_commit_it_names(self):
        a = self.commit("# R\n## 2026-11-13: first\n", "a")
        self.commit("# R\n## 2026-11-13-2: first\n\n**Shipped in:** " + a[:9] + "\n", "renumber")
        todo, _ = R.plan()
        self.assertEqual(todo, [("release-2026-11-13-2", a, "first")])


class Unique(unittest.TestCase):
    def test_no_release_id_is_used_twice_since_tagging_began(self):
        # 16 Nov 2026 (QA): three ids used twice on 15 Nov left three releases untagged.
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(here, "RELEASES.md"), encoding="utf-8") as f:
            ids = [m.group(1) for m in map(R.HEADER.match, f.read().splitlines()) if m and m.group(1) >= "2026-11-14"]
        self.assertEqual(sorted({i for i in ids if ids.count(i) > 1}), [])


if __name__ == "__main__":
    unittest.main()
