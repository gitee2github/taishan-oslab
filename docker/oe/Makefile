all: rpms/code.rpm bin/wakatime-cli

rpms/code.rpm:
	mkdir -p rpms
	wget -nc -O rpms/code.rpm https://github.com/coder/code-server/releases/download/v4.7.0/code-server-4.7.0-arm64.rpm

bin/wakatime-cli:
	mkdir -p bin
	wget -nc -O bin/waka.zip https://github.com/wakatime/wakatime-cli/releases/download/v1.55.1/wakatime-cli-linux-arm64.zip || true
	unzip -o bin/waka.zip -d bin
	mv -f bin/wakatime-cli-linux-arm64 bin/wakatime-cli
	rm bin/waka.zip
