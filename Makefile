.PHONY: demos

demos:
	PATH="$(CURDIR)/.venv/bin:$(PATH)" vhs assets/demo/scan.tape
	PATH="$(CURDIR)/.venv/bin:$(PATH)" vhs assets/demo/attack.tape
