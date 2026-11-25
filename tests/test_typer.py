import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import typer  # noqa: E402


class HelperTests(unittest.TestCase):
    def test_wrap_covers_text_without_gaps(self):
        text = "alpha beta gamma\ndelta epsilon zeta eta theta iota kappa"
        lines = typer.wrap(text, 12)
        self.assertEqual(lines[0][0], 0)
        self.assertEqual(lines[-1][1], len(text))
        for (_, e), (s, _) in zip(lines, lines[1:]):
            self.assertEqual(e, s)
        self.assertTrue(all(e - s <= 13 for s, e in lines))

    def test_wrap_empty(self):
        self.assertEqual(typer.wrap("", 10), [(0, 0)])

    def test_ordinal(self):
        self.assertEqual([typer.ordinal(n) for n in (1, 2, 3, 4, 11, 12, 13, 21, 22)],
                         ["1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "21st", "22nd"])

    def test_fmt_time(self):
        self.assertEqual(typer.fmt_time(12.34), "12.3")
        self.assertEqual(typer.fmt_time(65), "1:05")

    def test_ago(self):
        self.assertEqual(typer.ago({"ts": time.time()}), "just now")
        self.assertEqual(typer.ago({"ts": time.time() - 300}), "5 min ago")
        self.assertEqual(typer.ago({"date": "2026-01-02 03:04:05"}), "2026-01-02 03:04")

    def test_big_digits(self):
        rows, width = typer.big("42.0")
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(len(r) == width for r in rows))

    def test_to_ascii(self):
        self.assertEqual(typer.to_ascii("\u201chi\u201d\t\u00e9"), '"hi"    ')


class PassageTests(unittest.TestCase):
    def _load(self, name, content):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / name
            p.write_text(content, encoding="utf-8")
            return typer.load_passages(p)

    def test_prose_collapses_whitespace(self):
        out = self._load("a.txt", "one  two\nthree\n\nfour five")
        self.assertEqual(len(out), 1)
        self.assertNotIn("\n", out[0][1])
        self.assertNotIn("  ", out[0][1])

    def test_code_keeps_lines(self):
        out = self._load("a.py", "def f():\n    return 1\n\nprint(f())\n")
        self.assertEqual(out[0][1], "def f():\n    return 1")
        self.assertEqual(out[1][1], "print(f())")

    def test_empty_file(self):
        self.assertEqual(self._load("a.txt", "\n\n"), [])


class DataTests(unittest.TestCase):
    def test_builtin_text_is_typeable(self):
        texts = [t for v in typer.QUOTES.values() for t, _ in v]
        texts += [t.strip("\n") for _, t in typer.SNIPPETS]
        texts.append(" ".join(typer.WORDS))
        for t in texts:
            for ch in t:
                self.assertTrue(ch == "\n" or 32 <= ord(ch) <= 126, repr(ch))
        for _, t in typer.SNIPPETS:
            self.assertFalse(t.strip("\n")[0].isdigit())

    def test_every_category_has_quotes(self):
        for cid, _ in typer.CATS:
            if cid != "wild":
                self.assertTrue(typer.QUOTES[cid])

    def test_desktop_entry(self):
        entry = typer.desktop_entry(Path("/home/u/.local/bin/typer"))
        self.assertIn('Exec="/home/u/.local/bin/typer" %f', entry)
        self.assertIn("Terminal=true", entry)


if __name__ == "__main__":
    unittest.main()
