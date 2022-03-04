.DEFAULT_GOAL: all

# Export raspberry pi requirements
.PHONY: rpi-requirements
rpi-requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

# Install raspberry pi python requirements
.PHONY: rpi-install
rpi-install:
	sudo pip install -r requirements.txt

# Run ntp server
.PHONY: ntp
ntp:
	docker run --name=ntp --restart=always --detach --publish=123:123/udp cturra/ntp

# Run ntp server
.PHONY: ntp-stop
ntp-stop:
	docker stop ntp
	docker rm ntp

# Run laptop code
.PHONY: laptop
laptop:
	sudo poetry run python -m ana_lights.client.client

# Run raspberry pi code
.PHONY: rpi
rpi:
	sudo /usr/bin/python -m ana_lights.server.server