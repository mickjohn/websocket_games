IMAGE_NAME = wbskt_games

all: clean build-website image server

build-website: build
	./build

build-image : 
		sudo docker build -t $(IMAGE_NAME) .

image : build-image
	sudo docker save $(IMAGE_NAME) --output $(IMAGE_NAME).tar && \
		sudo chown mick:mick $(IMAGE_NAME).tar && \
		zip $(IMAGE_NAME).tar.zip $(IMAGE_NAME).tar && \
		rm $(IMAGE_NAME).tar

clean : 
	rm $(IMAGE_NAME).tar $(IMAGE_NAME).tar.zip||true

server :
	$(MAKE) -C frontend && mv frontend/wbskt_server.tar.zip .
