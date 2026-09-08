.PHONY: demos

demos:
	PATH="$(CURDIR)/.venv/bin:$(PATH)" vhs assets/demo/scan.tape
