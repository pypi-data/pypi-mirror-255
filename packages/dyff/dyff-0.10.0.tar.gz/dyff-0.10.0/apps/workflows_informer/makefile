LOCALBIN ?= $(shell pwd)/bin
IMAGE ?= workflows-informer
APP_BIN_NAME ?= workflows-informer
APP_BIN_PATH ?= $(LOCALBIN)/$(APP_BIN_NAME)

.PHONY: build
build: $(LOCALBIN)
	go build -o $(APP_BIN_PATH) main.go

$(LOCALBIN):
	mkdir -p $(LOCALBIN)
