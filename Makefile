.PHONY: run test install uninstall

run:
	python3 typer.py

test:
	python3 -m unittest discover -s tests -v

install:
	python3 typer.py --install

uninstall:
	python3 typer.py --uninstall
