.PHONY: all dist docker/oe docker vendor_local

all: vendor docker
dist: build/oslab.tar.gz

vendor: requirements.txt
	rsync -av requirements.txt vendor.sh ecs:/tmp/osbuild/
	ssh ecs "cd /tmp/osbuild && ./vendor.sh"
	rsync -av ecs:/tmp/osbuild/vendor.tar.gz build/
	rm -rf vendor && mkdir vendor && cd vendor && tar xf ../build/vendor.tar.gz

vendor_local: build requirements.txt
	mv requirements.txt vendor.sh build/
	cd build && ./vendor.sh
	rm -rf vendor && mkdir vendor && cd vendor && tar xf ../build/vendor.tar.gz

docker/oe:
	$(MAKE) -C docker/oe

docker/board: oscore/*
	rm -rf docker/board/scoreboard/{static,templates}
	cd oscore && yarn build
	mkdir docker/board/scoreboard/templates
	mv oscore/dist/index.html docker/board/scoreboard/templates/
	mv oscore/dist/static docker/board/scoreboard/

docker: docker/oe docker/board

build:
	mkdir -p build

build/oslab.tar.gz: build all
	tar czf $@ --exclude dep --exclude .git --exclude known_hosts --exclude venv --exclude .vent \
		 vendor docker install ostest board.json config.ini create* delete* settings LICENSE
