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

# Send final_lights folder to a raspberry pi ip
.PHONY: send-lights
send-lights:
	sshpass -p "raspberry" scp -r final_lights/ pi@$(ip):~/ana-lights/

# Send code folder to a raspberry pi ip
.PHONY: send-code
send-code:
	sshpass -p "raspberry" scp -r ana_lights/client/ pi@$(ip):~/ana-lights/ana_lights/
	sshpass -p "raspberry" scp -r ana_lights/server/ pi@$(ip):~/ana-lights/ana_lights/
	sshpass -p "raspberry" scp -r ana_lights/avi_to_json.py pi@$(ip):~/ana-lights/ana_lights/avi_to_json.py
	sshpass -p "raspberry" scp -r ana_lights/color.py pi@$(ip):~/ana-lights/ana_lights/color.py
	sshpass -p "raspberry" scp -r ana_lights/enums.py pi@$(ip):~/ana-lights/ana_lights/enums.py