#RapidPro docker build management
REGISTRY = 452158872079.dkr.ecr.us-east-1.amazonaws.com
NAME = rapidpro
BUILD_NUMBER?=latest

.PHONY: build tag release 

all: build tag release 

build:	
	docker build -t $(NAME) .
tag:
	docker tag $(NAME):$(BUILD_NUMBER) $(REGISTRY)/$(NAME):$(BUILD_NUMBER)
release: 
	docker push $(REGISTRY)/$(NAME):$(BUILD_NUMBER)

