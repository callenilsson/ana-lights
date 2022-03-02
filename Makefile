.DEFAULT_GOAL: all

# Export raspberry pi requirements
.PHONY: rpi-requirements
rpi-requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

# Install raspberry pi python requirements
.PHONY: rpi-install
rpi-install:
	pip3 install -r requirements.txt

# Run laptop code
.PHONY: laptop
laptop:
	sudo poetry run python -m ana_lights.client.client

# Run raspberry pi code
.PHONY: rpi
rpi:
	sudo /usr/bin/python3 -m ana_lights.server.server