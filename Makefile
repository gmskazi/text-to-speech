.PHONY: all check check-docs build-local-image deploy-local graphify

all: check check-docs

check:
	mise run check

check-docs:
	mise run check-docs

build-local-image:
	mise run build-local-image

deploy-local:
	mise run deploy-local

graphify:
	mise run graphify
