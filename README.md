# typer

Minimalist terminal typing practice. Single file, Python 3 standard library only (`curses`), built for Debian Linux terminals.

## Install

```sh
git clone <your-repo-url> typer && cd typer
python3 typer.py --install            # `typer` command + app-menu launcher (opens in your terminal)
python3 typer.py --install --desktop  # also a ~/Desktop shortcut
```

Or just run it: `python3 typer.py [file.txt]`. Remove with `python3 typer.py --uninstall` (scores are kept).
Needs a terminal of at least 50x16. Make sure `~/.local/bin` is on your `PATH`.

## Modes

| Key | Mode |
|-----|------|
| `1` | Words: 25 / 50 / 100 common words |
| `2` | Timed: 15 / 30 / 60 s word stream |
| `3` | Quote: Short, Inspirational, Science, Classic Books, Gaming, Typing Originals, Endurance, Wild |
| `4` | Code: Python, TypeScript/JavaScript, SQL, Bash snippets |
| `5` | File: passages from `python3 typer.py path/to/file.txt` |

## Keys

| Key | Action |
|-----|--------|
| `Left` / `Right` | length (words, timed) or category (quote) |
| `Tab`, `Ctrl+R` | restart with a new text |
| `Enter` | race again (results screen) |
| `Ctrl+T` | strict mode (fix an error to advance) |
| `Ctrl+G` | opponents: off / ghost (your best) / bots |
| `Ctrl+O` | color theme |
| `Ctrl+L` | scores: recent, mine, hall of fame |
| `Ctrl+K` | help |
| `Esc`, `Ctrl+C` | quit |

Digits `1`-`5` are shortcuts only before your first keypress of a test.

## Metrics

Net WPM = `(correct_chars / 5) / minutes`, raw WPM from all keystrokes, accuracy, and top 3 missed keys.
Scores and settings are saved to `~/.local/share/typer/stats.json`.

## Development

```sh
python3 -m unittest discover -s tests -v
```

## License

MIT
