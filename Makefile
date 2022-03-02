.DEFAULT_GOAL: all
	
# Run laptop code
.PHONY: laptop
laptop:
	poetry run python -m ana_lights.client.client

# Run raspberry pi code
.PHONY: rpi
rpi:
	poetry run python -m ana_lights.server.server