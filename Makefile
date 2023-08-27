IMAGE_NAME=cac
IMAGE_NAME_HUB=fgratzkowski/${IMAGE_NAME}


PORT_VAR := 9000

ifdef PORT
    PORT_VAR := $(PORT)
endif

build: Dockerfile
	docker build -t ${IMAGE_NAME} .

runhub:
	docker run -p $(PORT_VAR):$(PORT_VAR) --mount type=bind,source=".",target="/home/cac/CausalAnnotationCorrection" -it ${IMAGE_NAME_HUB}

run:
	docker run -p $(PORT_VAR):$(PORT_VAR) --mount type=bind,source=".",target="/home/cac/CausalAnnotationCorrection" -it ${IMAGE_NAME}

clean:
	docker system prune