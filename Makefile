#RapidPro docker build management
REGISTRY = 452158872079.dkr.ecr.us-east-1.amazonaws.com
NAME = rapidpro
VERSION = latest

.PHONY: build tag release clean

all: build tag release clean

build:	
	docker build -t $(NAME) .
tag:
	docker tag $(NAME):$(VERSION) $(REGISTRY)/$(NAME):$(VERSION)
release: 
	docker push $(REGISTRY)/$(NAME):$(VERSION)
clean:
	echo "Not yet implemented" #docker rmi $(NAME):$(VERSION)

