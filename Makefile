#RapidPro docker build management
REGISTRY = 452158872079.dkr.ecr.us-east-1.amazonaws.com
IMAGE = rapidpro
BUILD_NUMBER?=latest

.PHONY: build release 

all: build release 

build:	
	docker build -t $(REGISTRY)/$(IMAGE):$(BUILD_NUMBER) .
release: 
	docker push $(REGISTRY)/$(IMAGE):$(BUILD_NUMBER)

