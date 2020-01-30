SOURCEDIR := src
SOURCE_FILES := $(shell find $(SOURCEDIR))
SOURCES := $(SOURCE_FILES) node_modules

build: $(SOURCES) node_modules
	npm run build

node_modules: package.json package-lock.json
	npm install