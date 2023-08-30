IMAGE_NAME=cac
IMAGE_NAME_HUB=fgratzkowski/${IMAGE_NAME}


PORT_VAR := 9000

ifdef PORT
    PORT_VAR := $(PORT)
endif


build:
	docker build -t cac . --no-cache
push:
	docker build -t cac . --no-cache
	docker tag cac fgratzkowski/cac
	docker push fgratzkowski/cac
tutorial:
	docker run -p $(PORT_VAR):$(PORT_VAR) -it ${IMAGE_NAME_HUB}
clean:
	docker system prune