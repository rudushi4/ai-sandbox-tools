# AI Sandbox Tools

Universal toolkit for AI models to build, run, and preview code in an Ubuntu 20.04 sandbox.

## Features

- **Ubuntu 20.04 sandbox** via proot (no root required)
- **Ollama integration** for local LLM inference
- **Python/Bash/Node.js** code execution
- **Package management** (apt, pip, npm)

## Quick Start

```bash
# Run command in sandbox
./start-ubuntu20.sh "python3 -c 'print(1+1)'"

# Use Python API
python3 sandbox.py "uname -a"

# AI generates and runs code
python3 ai-sandbox-bridge.py run "calculate fibonacci"
```

## Tools

| File | Description |
|------|-------------|
| `sandbox.py` | Python API for sandbox control |
| `sandbox-cli.sh` | Bash CLI wrapper |
| `ai-sandbox-bridge.py` | AI model to sandbox integration |

## Setup

1. Download Ubuntu rootfs and extract to `ubuntu20-fs/`
2. Download [proot](https://proot.gitlab.io/proot/bin/proot)
3. Run `./start-ubuntu20.sh` to enter sandbox

## With Ollama

```bash
# Pull a model
ollama pull tinyllama

# AI generates code, runs in sandbox
python3 ai-sandbox-bridge.py run "create a web server"
```

## License

MIT
