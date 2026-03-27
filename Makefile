.PHONY: all check check-docs

all: check check-docs

check:
	mise run check

check-docs:
	mise run check-docs
