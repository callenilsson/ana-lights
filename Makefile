.DEFAULT_GOAL: all

# Export raspberry pi requirements
.PHONY: rpi-requirements
rpi-requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

# Run laptop code
.PHONY: laptop
laptop:
	poetry run python -m ana_lights.client.client

# Run raspberry pi code
.PHONY: rpi
rpi:
	poetry run python -m ana_lights.server.server