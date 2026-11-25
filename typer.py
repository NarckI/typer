#!/usr/bin/env python3
"""typer.py - minimalist terminal typing practice (Python 3 stdlib only).

Usage:
  python3 typer.py [file.txt]     run (optionally practice passages from a file)
  python3 typer.py --install      install `typer` command + app-menu launcher
  python3 typer.py --install --desktop   ...and a shortcut on ~/Desktop
  python3 typer.py --uninstall    remove the command and launcher

Keys:
  1-5 mode (words/timed/quote/code/file)   Left/Right length or category
  Tab / Ctrl+R restart    Enter (results) race again
  Ctrl+T strict  Ctrl+G opponents  Ctrl+O theme  Ctrl+L scores  Ctrl+K help
  Esc / Ctrl+C quit
"""
import curses
import json
import os
import random
import sys
import time
from pathlib import Path

HOME = Path.home()
STATS_PATH = HOME / ".local" / "share" / "typer" / "stats.json"
WORD_OPTS = (25, 50, 100)
TIME_OPTS = (15, 30, 60)
MODES = ("words", "timed", "quote", "code", "file")
RACES = ("off", "ghost", "bots")
CATS = (("short", "Short & Easy"), ("inspire", "Inspirational"), ("science", "Scientific Facts"),
        ("books", "Classic Books"), ("gaming", "Gaming"), ("original", "Typing Originals"),
        ("endurance", "Endurance [Long]"), ("wild", "Wild [All]"))
THEMES = (("classic", 78, curses.COLOR_GREEN, 244), ("amber", 214, curses.COLOR_YELLOW, 243),
          ("ice", 81, curses.COLOR_CYAN, 244), ("rose", 211, curses.COLOR_MAGENTA, 244),
          ("mono", 255, curses.COLOR_WHITE, 244))
CODE_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".sql", ".sh", ".bash", ".c", ".h",
             ".cpp", ".java", ".go", ".rs", ".rb", ".php", ".json", ".yml", ".yaml",
             ".html", ".css", ".toml", ".lua"}
MIN_ROWS, MIN_COLS = 16, 50
KEY_BACKSPACES = (curses.KEY_BACKSPACE, 127, 8)

WORDS = """the be to of and a in that have it for not on with he as you do at this but his by
from they we say her she or an will my one all would there their what so up out if about who
get which go me when make can like time no just him know take people into year your good some
could them see other than then now look only come its over think also back after use two how
our work first well way even new want because any these give day most us great little world
still hand high follow large water between never being place again house point thing life home
school night every system small number off always problem left city story open change keep seem
next group those must read need long early begin while turn start example both paper mean fact
line right move light write found study earth mother answer state close white sea walk music
call door food real country run stand family keyboard simple morning window garden bridge
coffee river pencil forest silver orange planet travel quiet market letter paper ocean mountain
bright button cable screen signal memory engine rhythm pattern thought""".split()

QUOTES = {
    "short": [
        ("The quick brown fox jumps over the lazy dog.", "pangram"),
        ("Sunlight spilled across the table while the kettle began to sing.", "original"),
        ("A good habit is built one quiet day at a time.", "original"),
        ("Please keep your hands relaxed and your eyes on the screen.", "original"),
        ("The train left early, but the next one will come soon enough.", "original"),
        ("Fresh bread, warm tea, and an open window make a fine morning.", "original"),
        ("Pack a light bag and take the long road home.", "original"),
        ("Typing is just thinking with your fingertips.", "original"),
    ],
    "inspire": [
        ("Small steps taken every day will carry you farther than one giant leap taken once.", "original"),
        ("Nobody sees the whole road at once, so be brave enough to walk the part that is lit.", "original"),
        ("Mistakes are only proof that you are trying something your hands have not learned yet.", "original"),
        ("Be patient with yourself; every expert you admire once fumbled over the very same keys.", "original"),
        ("Progress rarely announces itself, but one day you look back and the mountain is behind you.", "original"),
        ("Do the work while it is quiet, and let the applause find you later.", "original"),
        ("Courage is not the absence of doubt; it is typing the next word anyway.", "original"),
    ],
    "science": [
        ("A day on Venus is longer than its year, because the planet rotates once every 243 Earth days while orbiting the Sun in about 225.", "science fact"),
        ("Honey stored in sealed containers can last for thousands of years because it is low in water and mildly acidic.", "science fact"),
        ("Octopuses have three hearts: two pump blood through the gills and one circulates it to the rest of the body.", "science fact"),
        ("Light from the Sun takes about eight minutes to reach Earth, so we always see the Sun as it was a few minutes ago.", "science fact"),
        ("Water is densest at about four degrees Celsius, which is why ice floats and lakes freeze from the top down.", "science fact"),
        ("The human body contains roughly as many bacterial cells as human cells.", "science fact"),
        ("Sound travels about four times faster in water than in air.", "science fact"),
        ("A teaspoon of neutron star material would weigh billions of tons.", "science fact"),
        ("Bananas are slightly radioactive because they contain a small amount of potassium-40.", "science fact"),
    ],
    "books": [
        ("It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.", "Pride and Prejudice, Jane Austen"),
        ("Call me Ishmael. Some years ago - never mind how long precisely - having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world.", "Moby-Dick, Herman Melville"),
        ("It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of Light, it was the season of Darkness, it was the spring of hope, it was the winter of despair.", "A Tale of Two Cities, Charles Dickens"),
        ('Alice was beginning to get very tired of sitting by her sister on the bank, and of having nothing to do: once or twice she had peeped into the book her sister was reading, but it had no pictures or conversations in it, "and what is the use of a book," thought Alice "without pictures or conversations?"', "Alice's Adventures in Wonderland, Lewis Carroll"),
        ("To Sherlock Holmes she is always the woman. I have seldom heard him mention her under any other name.", "A Scandal in Bohemia, Arthur Conan Doyle"),
        ("I went to the woods because I wished to live deliberately, to front only the essential facts of life, and see if I could not learn what it had to teach, and not, when I came to die, discover that I had not lived.", "Walden, Henry David Thoreau"),
        ("Four score and seven years ago our fathers brought forth on this continent, a new nation, conceived in Liberty, and dedicated to the proposition that all men are created equal.", "The Gettysburg Address, Abraham Lincoln"),
    ],
    "gaming": [
        ("Save your progress before the boss fight, and never trust a treasure chest sitting quietly in the middle of a hallway.", "original"),
        ("The final dungeon is always harder than it looks, but the healing potions you hoarded were meant to be used.", "original"),
        ("Every speedrunner knows that the fastest route is the one you practiced a thousand times.", "original"),
        ("When the screen goes dark and the music slows, the wise player checks every corner for a hidden door.", "original"),
        ("Co-op mode teaches a simple lesson: the team moves at the speed of its most careful player.", "original"),
        ("A good controller disappears in your hands, just like a good keyboard disappears under your fingers.", "original"),
    ],
    "original": [
        ("Accuracy first, speed second: slow down until every key lands where you aim, and the speed will arrive on its own.", "original"),
        ("Keep your wrists level, your shoulders loose, and your breathing slow; tension is the quietest enemy of rhythm.", "original"),
        ("Look at the next word while your fingers finish the current one; the eyes should always run slightly ahead.", "original"),
        ("A clean keystroke is a small promise kept, and a thousand small promises are what we call skill.", "original"),
        ("Home row is not a place you leave but a place you return to after every stroke.", "original"),
        ("The best typists are not the fastest in a sprint but the steadiest in a marathon of ordinary words.", "original"),
    ],
    "endurance": [
        ("The keyboard is an instrument, and like any instrument it rewards patience far more than force. Beginners imagine that speed comes from hitting the keys harder or moving the fingers faster, but the opposite is true. Speed is what remains after every unnecessary motion has been removed. Rest your hands lightly, keep your eyes on the words ahead instead of the keys beneath, and let each finger return home after every stroke. When you make a mistake, resist the urge to rush; correct it calmly and keep the rhythm unbroken. A steady pace practiced daily will beat a frantic burst practiced rarely, and one day you will notice that the words are simply appearing on the screen.", "original"),
        ("A river does not hurry, and yet it carves canyons. It follows the lowest path, gathers every small stream along the way, and never stops to argue with the stones in its bed. The people who live beside it learn its moods: the quiet green of late summer, the brown swell of spring, the thin silver ribbon that appears when the rains fail. They build bridges, mills, and small wooden docks, and the river carries all of it without complaint. If you stand on the bank long enough, you begin to understand that patience is not the absence of motion but the steady decision to keep moving in the same direction, day after day, until the landscape itself has changed.", "original"),
        ("Late at night the office is quiet except for the hum of the refrigerator and the soft clicking of one lone keyboard. A single lamp lights the desk, and beside it sits a cup of tea that went cold hours ago. The project is almost finished, but almost is the most dangerous word in the language, because it tempts a tired person to stop paying attention. So she reads the last paragraph once more, fixes a missing comma, renames a confusing variable, and runs the tests again. Everything passes. She saves the file, closes the laptop, and walks out into the cool air, grateful for the small, unglamorous work that nobody will ever notice.", "original"),
    ],
}

SNIPPETS = [
    ("python", r"""
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
"""),
    ("python", r"""
with open(path, "r") as f:
    data = {k: v for k, v in json.load(f).items() if v}
print(len(data))
"""),
    ("python", r"""
class Stack:
    def __init__(self):
        self.items = []

    def push(self, x):
        self.items.append(x)

    def pop(self):
        return self.items.pop() if self.items else None
"""),
    ("python", r"""
try:
    value = int(raw_input)
except ValueError as err:
    print(f"invalid: {err}")
    value = None
"""),
    ("typescript", r"""
const total = items.reduce((sum, i) => sum + i.price * i.qty, 0);
console.log(`Total: ${total.toFixed(2)}`);
"""),
    ("typescript", r"""
async function load(url: string): Promise<User[]> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(res.statusText);
  return res.json();
}
"""),
    ("typescript", r"""
interface User {
  id: number;
  name: string;
  tags?: string[];
}
"""),
    ("javascript", r"""
export const debounce = (fn, ms = 200) => {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
};
"""),
    ("sql", r"""
SELECT c.name, COUNT(o.id) AS orders
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.created_at >= '2025-01-01'
GROUP BY c.name
HAVING COUNT(o.id) > 5
ORDER BY orders DESC;
"""),
    ("sql", r"""
CREATE TABLE tasks (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  done BOOLEAN DEFAULT FALSE
);
"""),
    ("sql", r"""
UPDATE accounts
SET balance = balance - 100
WHERE id = 42 AND balance >= 100;
"""),
    ("bash", r"""
find . -name "*.log" -mtime +7 -exec rm {} \;
"""),
    ("bash", r"""
for f in *.txt; do
  mv "$f" "${f%.txt}.md"
done
"""),
    ("bash", r"""
grep -rn "TODO" src/ | sort | uniq -c | sort -nr | head -n 10
"""),
    ("bash", r"""
tar -czf backup_$(date +%F).tar.gz ~/projects && echo "done"
"""),
    ("bash", r"""
if [ -f "$HOME/.env" ]; then
  source "$HOME/.env"
fi
"""),
]

GLYPHS = {
    "0": ["███", "█ █", "█ █", "█ █", "███"],
    "1": [" █ ", "██ ", " █ ", " █ ", "███"],
    "2": ["███", "  █", "███", "█  ", "███"],
    "3": ["███", "  █", "███", "  █", "███"],
    "4": ["█ █", "█ █", "███", "  █", "  █"],
    "5": ["███", "█  ", "███", "  █", "███"],
    "6": ["███", "█  ", "███", "█ █", "███"],
    "7": ["███", "  █", "  █", "  █", "  █"],
    "8": ["███", "█ █", "███", "█ █", "███"],
    "9": ["███", "█ █", "███", "  █", "███"],
    ".": [" ", " ", " ", " ", "█"],
    ":": [" ", "█", " ", "█", " "],
}

ASCII_MAP = {"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u2013": "-",
             "\u2014": "-", "\u2026": "...", "\u00a0": " ", "\t": "    "}

HELP_ROWS = [
    ("1 2 3 4 5", "words / timed / quote / code / file"),
    ("Left Right", "length (words, timed) or category (quote)"),
    ("Tab  ^R", "restart with a new text"),
    ("Enter", "race again (on results screen)"),
    ("^T", "strict mode: fix an error to advance"),
    ("^G", "opponents: off / ghost (your best) / bots"),
    ("^O", "cycle color theme"),
    ("^L", "scores: recent, mine, hall of fame"),
    ("^K", "this help"),
    ("Esc  ^C", "quit"),
]

ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="12" fill="#14181c"/>
<rect x="8" y="14" width="48" height="36" rx="6" fill="none" stroke="#4ade80" stroke-width="3"/>
<path d="M17 28l7 5-7 5" fill="none" stroke="#4ade80" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M29 40h14" stroke="#e5e7eb" stroke-width="3.5" stroke-linecap="round"/>
</svg>
"""


# --------------------------------------------------------------------------- helpers

def to_ascii(s):
    out = []
    for c in s:
        c = ASCII_MAP.get(c, c)
        for d in c:
            if d == "\n" or 32 <= ord(d) <= 126:
                out.append(d)
    return "".join(out)


def load_passages(path):
    """Return a list of (lang, text) passages built from a file."""
    raw = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    raw = to_ascii(raw)
    passages = []
    if path.suffix.lower() in CODE_EXTS:
        lines = [ln.rstrip() for ln in raw.split("\n")]
        blocks, cur = [], []
        for ln in lines + [""]:
            if ln.strip():
                cur.append(ln)
            elif cur:
                blocks.append(cur)
                cur = []
        for b in blocks:
            for i in range(0, len(b), 12):
                passages.append("\n".join(b[i:i + 12]))
    else:
        paras, cur = [], []
        for ln in raw.split("\n") + [""]:
            if ln.strip():
                cur.append(ln)
            elif cur:
                paras.append(" ".join(" ".join(cur).split()))
                cur = []
        pieces = []
        for p in paras:
            w = p.split()
            for i in range(0, len(w), 60):
                pieces.append(w[i:i + 60])
        buf = []
        for p in pieces:
            buf += p
            if len(buf) >= 25:
                passages.append(" ".join(buf))
                buf = []
        if buf:
            if passages and len(buf) < 10:
                passages[-1] += " " + " ".join(buf)
            else:
                passages.append(" ".join(buf))
    return [("", p) for p in passages if p.strip()]


def load_data():
    data = {"sessions": [], "bests": {}, "settings": {}, "totals": {}}
    try:
        raw = json.loads(STATS_PATH.read_text())
        if isinstance(raw, dict):
            for k in data:
                if isinstance(raw.get(k), type(data[k])):
                    data[k] = raw[k]
    except (OSError, ValueError):
        pass
    data["bests"] = {k: v for k, v in data["bests"].items()
                     if isinstance(v, dict) and isinstance(v.get("wpm"), (int, float))}
    data["sessions"] = [s for s in data["sessions"]
                        if isinstance(s, dict) and isinstance(s.get("wpm"), (int, float))]
    st = data["settings"]
    if st.get("mode") not in MODES:
        st["mode"] = "words"
    st["wi"] = st["wi"] if st.get("wi") in (0, 1, 2) else 0
    st["ti"] = st["ti"] if st.get("ti") in (0, 1, 2) else 1
    st["ci"] = st["ci"] if st.get("ci") in range(len(CATS)) else 0
    st["race"] = st["race"] if st.get("race") in (0, 1, 2) else 0
    st["theme"] = st["theme"] if st.get("theme") in range(len(THEMES)) else 0
    st["strict"] = bool(st.get("strict", False))
    t = data["totals"]
    t["races"] = max(int(t.get("races", 0) or 0), len(data["sessions"]))
    t["secs"] = float(t.get("secs", 0) or 0)
    return data


def save_data(data):
    try:
        STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = STATS_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2))
        tmp.replace(STATS_PATH)
    except OSError:
        pass


def wrap(text, width):
    """Split text into (start, end) index ranges; newlines stay at line ends."""
    lines, pos, n = [], 0, len(text)
    while pos < n:
        nl = text.find("\n", pos)
        end = n if nl == -1 else nl + 1
        if end - pos > width:
            limit = pos + width
            sp = text.rfind(" ", pos, limit)
            end = sp + 1 if sp > pos else limit
        lines.append((pos, end))
        pos = end
    return lines or [(0, 0)]


def big(text):
    rows = [""] * 5
    for i, ch in enumerate(text):
        g = GLYPHS.get(ch, GLYPHS["0"])
        for r in range(5):
            rows[r] += g[r] + (" " if i < len(text) - 1 else "")
    return rows, len(rows[0])


def fmt_time(secs):
    if secs < 60:
        return f"{secs:.1f}"
    return f"{int(secs // 60)}:{int(secs % 60):02d}"


def key_name(k):
    return {" ": "space", "\n": "enter"}.get(k, k)


def ordinal(n):
    suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def ago(s):
    ts = s.get("ts")
    if not isinstance(ts, (int, float)):
        return str(s.get("date", ""))[:16]
    d = max(0, int(time.time() - ts))
    if d < 60:
        return "just now"
    if d < 3600:
        return f"{d // 60} min ago"
    if d < 86400:
        return f"{d // 3600} hr ago"
    return f"{d // 86400} days ago"


# --------------------------------------------------------------------------- app

class App:
    def __init__(self, scr, passages, fname, notice=""):
        self.scr = scr
        self.passages = passages
        self.fname = fname
        self.notice = notice
        self.data = load_data()
        st = self.data["settings"]
        self.mode = st["mode"]
        if self.mode == "file" and not passages:
            self.mode = "words"
        if passages:
            self.mode = "file"
        self.wi, self.ti, self.ci = st["wi"], st["ti"], st["ci"]
        self.strict, self.race, self.theme = st["strict"], st["race"], st["theme"]
        self.view = None
        self.tab = 0
        self.A = {}
        self.bg = -1
        self.setup_colors()
        self.last_text = ""
        self.result = None
        self.new_test()

    # ----- colors -----
    def setup_colors(self):
        if curses.has_colors():
            curses.start_color()
            try:
                curses.use_default_colors()
                self.bg = -1
            except curses.error:
                self.bg = curses.COLOR_BLACK
        self.apply_theme()

    def apply_theme(self):
        A = self.A
        A.update({"dim": curses.A_DIM, "ok": curses.A_BOLD,
                  "bad": curses.A_REVERSE | curses.A_BOLD, "bold": curses.A_BOLD})
        if not curses.has_colors():
            return
        _, acc256, acc8, dim256 = THEMES[self.theme]
        wide = curses.COLORS >= 256
        curses.init_pair(1, dim256 if wide else curses.COLOR_WHITE, self.bg)
        curses.init_pair(2, acc256 if wide else acc8, self.bg)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)
        A["dim"] = curses.color_pair(1) | (0 if wide else curses.A_DIM)
        A["ok"] = curses.color_pair(2) | curses.A_BOLD
        A["bad"] = curses.color_pair(3) | curses.A_BOLD

    # ----- state -----
    def save_settings(self):
        self.data["settings"] = {"mode": self.mode, "wi": self.wi, "ti": self.ti, "ci": self.ci,
                                 "strict": self.strict, "race": self.race, "theme": self.theme}
        save_data(self.data)

    def best_key(self):
        if self.mode == "words":
            return f"words:{WORD_OPTS[self.wi]}"
        if self.mode == "timed":
            return f"timed:{TIME_OPTS[self.ti]}"
        if self.mode == "quote":
            return f"quote:{CATS[self.ci][0]}"
        return self.mode

    def mode_label(self):
        if self.mode == "words":
            return f"words {WORD_OPTS[self.wi]}"
        if self.mode == "timed":
            return f"timed {TIME_OPTS[self.ti]}s"
        if self.mode == "quote":
            return f"quote {CATS[self.ci][1]}"
        return self.mode

    def avg_recent(self, n=10):
        s = self.data["sessions"][-n:]
        return sum(x["wpm"] for x in s) / len(s) if s else 0.0

    def gen_words(self, n):
        out, prev = [], None
        while len(out) < n:
            w = random.choice(WORDS)
            if w != prev:
                out.append(w)
                prev = w
        return out

    def pick(self, pool):
        for _ in range(8):
            item = random.choice(pool)
            text = item[0] if self.mode == "quote" else item[1]
            if text.strip("\n") != self.last_text:
                break
        return item

    def make_opps(self):
        if self.race == 1:
            b = self.data["bests"].get(self.best_key())
            return [("ghost", float(b["wpm"]))] if b and b["wpm"] > 0 else []
        if self.race == 2:
            base = self.avg_recent() or 40.0
            return [(n, max(10.0, float(round(base * f))))
                    for n, f in (("Tortoise", 0.75), ("Cruiser", 1.0), ("Hare", 1.25))]
        return []

    def new_test(self):
        self.lang = ""
        self.source = ""
        if self.mode == "words":
            text = " ".join(self.gen_words(WORD_OPTS[self.wi]))
        elif self.mode == "timed":
            text = " ".join(self.gen_words(400))
        elif self.mode == "quote":
            cid = CATS[self.ci][0]
            pool = [q for k, v in QUOTES.items() for q in v] if cid == "wild" else QUOTES[cid]
            text, self.source = self.pick(pool)
        elif self.mode == "code":
            self.lang, text = self.pick(SNIPPETS)
            text = text.strip("\n")
        else:
            _, text = self.pick(self.passages)
            text = text.strip("\n")
        self.text = text
        self.last_text = text
        self.typed = []
        self.total = 0
        self.wrong = 0
        self.missed = {}
        self.start = None
        self.state = "idle"
        self.result = None
        self.opps = self.make_opps()

    def correct_count(self):
        return sum(1 for i, c in enumerate(self.typed) if c == self.text[i])

    def live_wpm(self, el):
        if el < 1.5:
            return 0.0
        return self.correct_count() / 5 / (el / 60)

    def elapsed(self):
        return time.monotonic() - self.start if self.start is not None else 0.0

    def rank(self):
        el, n, mine = self.elapsed(), len(self.text), len(self.typed)
        return 1 + sum(1 for _, w in self.opps if min(n, w * 5 * el / 60) > mine)

    def finish(self, end):
        self.state = "done"
        secs = max(end - self.start, 0.0)
        minutes = max(secs, 0.5) / 60
        correct = self.correct_count()
        wpm = correct / 5 / minutes
        raw = self.total / 5 / minutes
        acc = 100.0 * (self.total - self.wrong) / self.total if self.total else 100.0
        top = sorted(self.missed.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
        key = self.best_key()
        prev = self.data["bests"].get(key)
        is_best = wpm > 0 and (prev is None or wpm > prev["wpm"])
        place = total = None
        if self.opps:
            n = len(self.text)
            if self.mode == "timed":
                ahead = sum(1 for _, w in self.opps if min(n, w * 5 * secs / 60) > len(self.typed))
            else:
                ahead = sum(1 for _, w in self.opps if n * 12 / w < secs)
            place, total = ahead + 1, len(self.opps) + 1
        self.result = {"wpm": wpm, "raw": raw, "acc": acc, "secs": secs, "top": top,
                       "keys": self.total, "errors": self.wrong, "best": is_best,
                       "prev": prev["wpm"] if prev else None, "place": place, "field": total}
        sessions = self.data["sessions"]
        sessions.append({"date": time.strftime("%Y-%m-%d %H:%M:%S"), "ts": time.time(),
                         "mode": self.mode, "label": self.mode_label(), "strict": self.strict,
                         "wpm": round(wpm, 1), "raw": round(raw, 1), "accuracy": round(acc, 1),
                         "time": round(secs, 1), "missed": [k for k, _ in top]})
        self.data["sessions"] = sessions[-500:]
        t = self.data["totals"]
        t["races"] += 1
        t["secs"] += secs
        if is_best:
            self.data["bests"][key] = {"wpm": round(wpm, 1), "accuracy": round(acc, 1),
                                       "date": time.strftime("%Y-%m-%d")}
        save_data(self.data)

    def tick(self):
        if self.state == "running" and self.mode == "timed":
            dur = TIME_OPTS[self.ti]
            if self.elapsed() >= dur:
                self.finish(self.start + dur)

    # ----- input -----
    def select(self, ch):
        m = MODES[ch - 49]
        if m == "file" and not self.passages:
            return
        self.mode = m
        self.save_settings()
        self.new_test()

    def cycle(self, d):
        if self.mode == "words":
            self.wi = (self.wi + d) % 3
        elif self.mode == "timed":
            self.ti = (self.ti + d) % 3
        elif self.mode == "quote":
            self.ci = (self.ci + d) % len(CATS)
        else:
            return
        self.save_settings()
        self.new_test()

    def handle(self, ch):
        if ch == 3:
            return False
        if ch == curses.KEY_RESIZE:
            self.scr.clear()
            return True
        if ch == 15:
            self.theme = (self.theme + 1) % len(THEMES)
            self.apply_theme()
            self.save_settings()
            return True
        if self.view:
            if ch == 27 or ch in (10, 13, curses.KEY_ENTER, ord("q"), 11, 12):
                self.view = None
            elif self.view == "scores" and ch == curses.KEY_LEFT:
                self.tab = (self.tab - 1) % 3
            elif self.view == "scores" and ch == curses.KEY_RIGHT:
                self.tab = (self.tab + 1) % 3
            return True
        if ch == 27:
            return False
        if ch in (9, 18):
            self.new_test()
            return True
        running = self.state == "running"
        if not running:
            if ch == 20:
                self.strict = not self.strict
                self.save_settings()
                return True
            if ch == 7:
                self.race = (self.race + 1) % 3
                self.opps = self.make_opps()
                self.save_settings()
                return True
            if ch == 12:
                self.view, self.tab = "scores", 0
                return True
            if ch == 11:
                self.view = "help"
                return True
            if ch in (curses.KEY_LEFT, curses.KEY_RIGHT):
                self.cycle(-1 if ch == curses.KEY_LEFT else 1)
                return True
            if 49 <= ch <= 53:
                if not (self.state == "idle" and self.text[:1] == chr(ch)):
                    self.select(ch)
                    return True
        if self.state == "done":
            if ch in (10, 13, curses.KEY_ENTER):
                self.new_test()
            return True
        if ch in KEY_BACKSPACES:
            if running and self.typed and not self.strict:
                self.typed.pop()
            return True
        if ch in (10, 13, curses.KEY_ENTER):
            if "\n" not in self.text:
                return True
            key = "\n"
        elif 32 <= ch <= 126:
            key = chr(ch)
        else:
            return True
        now = time.monotonic()
        if self.state == "idle":
            self.start = now
            self.state = "running"
            self.notice = ""
        expected = self.text[len(self.typed)]
        self.total += 1
        if key == expected:
            self.typed.append(key)
        else:
            self.wrong += 1
            self.missed[expected] = self.missed.get(expected, 0) + 1
            if not self.strict:
                self.typed.append(key)
        if len(self.typed) >= len(self.text):
            self.finish(now)
        return True

    # ----- drawing primitives -----
    def put(self, y, x, s, attr=0):
        rows, cols = self.scr.getmaxyx()
        if y < 0 or y >= rows or x >= cols:
            return
        if x < 0:
            s = s[-x:]
            x = 0
        s = s[:cols - x]
        if not s:
            return
        try:
            self.scr.addstr(y, x, s, attr)
        except curses.error:
            pass

    def segs(self, y, segs):
        _, cols = self.scr.getmaxyx()
        x = (cols - sum(len(t) for t, _ in segs)) // 2
        for t, a in segs:
            self.put(y, x, t, a)
            x += len(t)

    def center(self, y, s, attr=0):
        self.segs(y, [(s, attr)])

    def draw_header(self):
        dim, bold = self.A["dim"], self.A["bold"]
        segs = []
        for i, m in enumerate(MODES):
            if segs:
                segs.append(("   ", 0))
            off = m == "file" and not self.passages
            segs.append((f"{i + 1} {m}", bold if m == self.mode and not off else dim))
        self.segs(1, segs)
        if self.mode in ("words", "timed"):
            opts, cur, suf = ((WORD_OPTS, self.wi, "") if self.mode == "words"
                              else (TIME_OPTS, self.ti, "s"))
            segs = [("< ", dim)]
            for i, v in enumerate(opts):
                if i:
                    segs.append(("   ", 0))
                segs.append((f"{v}{suf}", bold if i == cur else dim))
            segs.append((" >", dim))
            self.segs(2, segs)
        elif self.mode == "quote":
            self.segs(2, [("< ", dim), (CATS[self.ci][1], bold),
                          (f" ({self.ci + 1}/{len(CATS)}) >", dim)])
        elif self.mode == "code":
            self.center(2, "python  typescript  sql  bash", dim)
        else:
            self.center(2, self.fname or "", dim)
        self.segs(3, [("^T ", dim), ("strict" if self.strict else "standard", bold),
                      ("   ^G race ", dim), (RACES[self.race], bold),
                      ("   ^O ", dim), (THEMES[self.theme][0], bold)])

    def draw_footer(self, rows):
        if self.state == "running":
            msg = "tab restart    esc quit"
        elif self.state == "done":
            msg = "enter race again    ^L scores    esc quit"
        else:
            msg = "tab new text    ^L scores    ^K help    esc quit"
        self.center(rows - 2, msg, self.A["dim"])

    # ----- screens -----
    def status_text(self):
        parts = []
        if self.state == "idle":
            if self.notice:
                return self.notice
            if self.lang:
                parts.append(self.lang)
            elif self.mode == "file" and self.fname:
                parts.append(self.fname)
            elif self.mode == "quote":
                parts.append(CATS[self.ci][1])
            b = self.data["bests"].get(self.best_key())
            if b:
                parts.append(f"best {b['wpm']:.0f} wpm")
            n = self.data["totals"]["races"]
            if n:
                parts.append(f"avg {self.avg_recent():.0f}")
                parts.append(f"{n} races")
            if self.race == 1 and not self.opps:
                parts.append("no ghost yet")
            if not parts:
                parts.append("start typing to begin")
        else:
            el = self.elapsed()
            if self.mode == "timed":
                left = TIME_OPTS[self.ti] - el
                parts.append(f"{max(0, int(left + 0.999))}s")
            elif self.mode == "words":
                done = self.text[:len(self.typed)].count(" ")
                parts.append(f"{done}/{len(self.text.split())}")
            parts.append(f"{self.live_wpm(el):.0f} wpm")
            if self.opps:
                parts.append(f"{ordinal(self.rank())}/{len(self.opps) + 1}")
        return "   ".join(parts)

    def lane_rows(self):
        el, n, timed = self.elapsed(), len(self.text), self.mode == "timed"

        def prog(chars):
            return f"{chars / 5:.0f} w" if timed else f"{min(100, 100 * chars / n):.0f}%"
        out = [("you", f"{self.live_wpm(el):.0f} wpm", prog(len(self.typed)), True)]
        for name, w in self.opps:
            out.append((name, f"{w:.0f} wpm", prog(min(n, w * 5 * el / 60)), False))
        return out

    def draw_test(self, rows, cols):
        A = self.A
        W = max(20, min(cols - 8, 76))
        x0 = (cols - W) // 2
        lines = wrap(self.text, W)
        pos = len(self.typed)
        cl = len(lines) - 1
        for i, (s, e) in enumerate(lines):
            if pos < e:
                cl = i
                break
        multiline = "\n" in self.text
        lane_h = len(self.opps) + 2 if self.opps else 0
        cap = max(3, min(len(lines), rows - 12 - lane_h, 18)) if multiline else 4
        cap = min(cap, len(lines))
        if len(lines) <= cap:
            start = 0
        else:
            lead = cap // 3 if multiline else 1
            start = max(0, min(cl - lead, len(lines) - cap))
        top = max((rows - (cap + 2 + lane_h)) // 2, 5)
        if self.state == "idle":
            self.draw_header()
        self.center(top, self.status_text(), A["dim"])
        for li in range(start, start + cap):
            s, e = lines[li]
            y = top + 2 + li - start
            for idx in range(s, e):
                ch = self.text[idx]
                x = x0 + idx - s
                if idx < pos:
                    ok = self.typed[idx] == ch
                    if ch == "\n":
                        if not ok:
                            self.put(y, x, "\u21b5", A["bad"])
                        continue
                    self.put(y, x, ch, A["ok"] if ok else A["bad"])
                elif ch == "\n":
                    if idx == pos:
                        self.put(y, x, " ", curses.A_REVERSE)
                else:
                    self.put(y, x, ch, curses.A_REVERSE if idx == pos else A["dim"])
        if self.opps and self.state == "running":
            ly = top + 2 + cap + 1
            lanes = self.lane_rows()
            if ly + len(lanes) <= rows - 3:
                for i, (name, wpm_s, prog_s, you) in enumerate(lanes):
                    self.put(ly + i, x0, f"{name:<10}{wpm_s:>9}   {prog_s:>6}",
                             A["ok"] if you else A["dim"])
        self.draw_footer(rows)

    def draw_results(self, rows, cols):
        A, r = self.A, self.result
        if self.mode == "words":
            desc = f"words {WORD_OPTS[self.wi]}"
        elif self.mode == "timed":
            desc = f"timed {TIME_OPTS[self.ti]}s"
        elif self.mode == "quote":
            desc = f"quote \u00b7 {CATS[self.ci][1]}"
        else:
            desc = self.mode
        desc += " \u00b7 " + ("strict" if self.strict else "standard")
        missed = "  ".join(f"{key_name(k)} {c}" for k, c in r["top"]) or "none"
        rowsd = [("Net WPM", f"{r['wpm']:.1f}"), ("Raw WPM", f"{r['raw']:.1f}"),
                 ("Accuracy", f"{r['acc']:.1f}%"),
                 ("Keystrokes", f"{r['keys']}  ({r['errors']} errors)"),
                 ("Missed keys", missed), ("Mode", desc)]
        if r["place"]:
            rowsd.append(("Race", f"{ordinal(r['place'])} of {r['field']}"))
        if self.source:
            rowsd.append(("Source", self.source))
        bigh, comph = 8 + len(rowsd) + 2, 2 + len(rowsd) + 2
        is_big = cols >= 52 and rows >= bigh + 4
        height = bigh if is_big else comph
        show_header = rows >= 5 + height + 3
        if show_header:
            self.draw_header()
        y = max((rows - height) // 2, 5 if show_header else 1)
        tstr = fmt_time(r["secs"])
        if is_big:
            stats = [(str(round(r["wpm"])), "WPM"), (str(round(r["acc"])), "ACCURACY %"),
                     (tstr, "TIME")]
            cw = 16
            xs = (cols - cw * 3) // 2
            for i, (num, label) in enumerate(stats):
                glyph, w = big(num)
                cx = xs + i * cw + (cw - w) // 2
                for k in range(5):
                    self.put(y + k, cx, glyph[k], A["bold"])
                self.put(y + 6, xs + i * cw + (cw - len(label)) // 2, label, A["dim"])
            y += 8
        else:
            self.center(y, f"WPM {r['wpm']:.0f}    ACCURACY {r['acc']:.0f}%    TIME {tstr}",
                        A["bold"])
            y += 2
        bw = min(46, cols - 6)
        bx = (cols - bw) // 2
        for label, val in rowsd:
            self.put(y, bx, label, A["dim"])
            self.put(y, bx + bw - len(val), val, A["bold"])
            y += 1
        y += 1
        if r["best"]:
            self.center(y, "new personal best", A["ok"])
        elif r["prev"] is not None:
            self.center(y, f"personal best  {r['prev']:.1f} wpm", A["dim"])
        self.draw_footer(rows)

    def draw_scores(self, rows, cols):
        A = self.A
        tabs = ("Recent Scores", "My Scores", "Hall of Fame")
        segs = []
        for i, t in enumerate(tabs):
            if segs:
                segs.append(("    ", 0))
            segs.append((t, A["bold"] if i == self.tab else A["dim"]))
        self.segs(1, segs)
        bw = min(58, cols - 4)
        bx = (cols - bw) // 2
        y, limit = 4, rows - 4
        ss = self.data["sessions"]
        if self.tab in (0, 2):
            items = list(reversed(ss)) if self.tab == 0 else sorted(ss, key=lambda s: -s["wpm"])
            items = items[:max(0, min(10, limit - y))]
            if not items:
                self.center(y + 1, "no races yet", A["dim"])
            for i, s in enumerate(items):
                label = str(s.get("label") or f"{s.get('mode', '')}")[:22]
                self.put(y, bx, f"{i + 1:>2}", A["dim"])
                self.put(y, bx + 4, f"{s['wpm']:>4.0f} wpm", A["bold"])
                self.put(y, bx + 14, f"{s.get('accuracy', 0):>5.1f}%  {label}", A["dim"])
                t = ago(s)
                self.put(y, bx + bw - len(t), t, A["dim"])
                y += 1
        else:
            t = self.data["totals"]
            rec = ss[-10:]
            rows_s = [("Races", str(t["races"])),
                      ("Average speed", f"{sum(s['wpm'] for s in ss) / len(ss):.1f} wpm" if ss else "-"),
                      ("Average (last 10)", f"{sum(s['wpm'] for s in rec) / len(rec):.1f} wpm" if rec else "-"),
                      ("Best speed", f"{max(s['wpm'] for s in ss):.1f} wpm" if ss else "-"),
                      ("Average accuracy", f"{sum(s.get('accuracy', 0) for s in ss) / len(ss):.1f}%" if ss else "-"),
                      ("Time typed", f"{t['secs'] / 60:.1f} min")]
            for label, val in rows_s:
                self.put(y, bx, label, A["dim"])
                self.put(y, bx + bw - len(val), val, A["bold"])
                y += 1
            y += 1
            bests = sorted(self.data["bests"].items(), key=lambda kv: -kv[1]["wpm"])
            if bests and y < limit:
                self.put(y, bx, "Personal bests", A["dim"])
                y += 1
            for k, v in bests:
                if y >= limit:
                    break
                val = f"{v['wpm']:.1f} wpm"
                self.put(y, bx, k, A["bold"])
                self.put(y, bx + bw - len(val), val, A["bold"])
                y += 1
        self.center(rows - 2, "left/right tab    esc close", A["dim"])

    def draw_help(self, rows, cols):
        A = self.A
        self.center(1, "Keyboard Shortcuts", A["bold"])
        bw = min(60, cols - 4)
        bx = (cols - bw) // 2
        y = 4
        for k, d in HELP_ROWS:
            if y >= rows - 3:
                break
            self.put(y, bx, k, A["bold"])
            self.put(y, bx + 14, d, A["dim"])
            y += 1
        self.center(rows - 2, "esc close", A["dim"])

    def draw(self):
        rows, cols = self.scr.getmaxyx()
        self.scr.erase()
        if rows < MIN_ROWS or cols < MIN_COLS:
            self.center(rows // 2, f"terminal too small (need {MIN_COLS}x{MIN_ROWS})")
        elif self.view == "scores":
            self.draw_scores(rows, cols)
        elif self.view == "help":
            self.draw_help(rows, cols)
        elif self.state == "done" and self.result:
            self.draw_results(rows, cols)
        else:
            self.draw_test(rows, cols)
        self.scr.refresh()

    def run(self):
        self.scr.timeout(100)
        while True:
            self.tick()
            self.draw()
            ch = self.scr.getch()
            if ch == -1:
                continue
            if not self.handle(ch):
                break


def main(scr, passages, fname, notice):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    curses.raw()
    scr.keypad(True)
    try:
        curses.set_escdelay(25)
    except (AttributeError, curses.error):
        pass
    App(scr, passages, fname, notice).run()


# --------------------------------------------------------------------------- launcher

def app_paths():
    return {"bin": HOME / ".local" / "bin" / "typer",
            "desktop": HOME / ".local" / "share" / "applications" / "typer.desktop",
            "icon": HOME / ".local" / "share" / "icons" / "hicolor" / "scalable" / "apps" / "typer.svg",
            "shortcut": HOME / "Desktop" / "typer.desktop"}


def desktop_entry(exe):
    q = str(exe)
    for a, b in (("\\", "\\\\"), ('"', '\\"'), ("$", "\\$"), ("`", "\\`")):
        q = q.replace(a, b)
    return ("[Desktop Entry]\nType=Application\nVersion=1.0\nName=Typer\n"
            "GenericName=Typing Practice\nComment=Minimalist terminal typing practice\n"
            f'Exec="{q}" %f\nIcon=typer\nTerminal=true\nCategories=Utility;Education;\n'
            "Keywords=typing;wpm;keyboard;practice;typeracer;\nMimeType=text/plain;\n")


def install(with_desktop):
    p = app_paths()
    src = Path(__file__).resolve()
    for k in ("bin", "desktop", "icon"):
        p[k].parent.mkdir(parents=True, exist_ok=True)
    if not (p["bin"].exists() and p["bin"].resolve() == src):
        p["bin"].write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    p["bin"].chmod(0o755)
    p["icon"].write_text(ICON_SVG)
    entry = desktop_entry(p["bin"])
    p["desktop"].write_text(entry)
    p["desktop"].chmod(0o755)
    print(f"installed command : {p['bin']}")
    print(f"installed launcher: {p['desktop']}  (find 'Typer' in your app menu)")
    if with_desktop:
        if p["shortcut"].parent.is_dir():
            p["shortcut"].write_text(entry)
            p["shortcut"].chmod(0o755)
            print(f"desktop shortcut  : {p['shortcut']}  (GNOME: right-click > Allow Launching)")
        else:
            print("no ~/Desktop folder found; skipped desktop shortcut")
    if str(p["bin"].parent) not in os.environ.get("PATH", "").split(os.pathsep):
        print(f"note: add {p['bin'].parent} to your PATH to run `typer` from any terminal")
    else:
        print("run it anywhere with: typer")


def uninstall():
    for k, path in app_paths().items():
        try:
            if path.exists() and (k != "shortcut" or "typer" in path.read_text()):
                path.unlink()
                print(f"removed {path}")
        except OSError as e:
            print(f"could not remove {path}: {e.strerror or e}")
    print(f"your scores are kept in {STATS_PATH.parent}")


USAGE = ("usage: python3 typer.py [file.txt]\n"
         "       python3 typer.py --install [--desktop]\n"
         "       python3 typer.py --uninstall")

if __name__ == "__main__":
    args = sys.argv[1:]
    flags = [a for a in args if a.startswith("--")]
    plain = [a for a in args if not a.startswith("--")]
    if "-h" in plain or "--help" in flags:
        sys.exit(USAGE)
    if any(f not in ("--install", "--uninstall", "--desktop") for f in flags) or len(plain) > 1:
        sys.exit(USAGE)
    if "--uninstall" in flags:
        uninstall()
        sys.exit(0)
    if "--install" in flags:
        try:
            install("--desktop" in flags)
        except OSError as e:
            sys.exit(f"typer: install failed: {e.strerror or e}")
        sys.exit(0)
    passages, fname, notice = [], None, ""
    if plain:
        p = Path(plain[0]).expanduser()
        try:
            passages = load_passages(p)
            fname = p.name
            if not passages:
                notice = f"no usable text in {p.name}"
        except OSError as e:
            notice = f"cannot read {p.name}: {e.strerror or e}"
    try:
        curses.wrapper(main, passages, fname, notice)
    except KeyboardInterrupt:
        pass
