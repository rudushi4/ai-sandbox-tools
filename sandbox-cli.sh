#!/bin/bash
# AI Sandbox CLI
SANDBOX_SCRIPT="/workspace/start-ubuntu20.sh"

case "$1" in
    run) shift; $SANDBOX_SCRIPT "$*" ;;
    install) shift; $SANDBOX_SCRIPT "DEBIAN_FRONTEND=noninteractive apt install -y $*" ;;
    pip) shift; $SANDBOX_SCRIPT "pip3 install $*" ;;
    python) shift; $SANDBOX_SCRIPT "python3 $*" ;;
    node) shift; $SANDBOX_SCRIPT "node $*" ;;
    info) $SANDBOX_SCRIPT "uname -a && cat /etc/os-release | head -3" ;;
    shell) $SANDBOX_SCRIPT ;;
    *) echo "Usage: $0 {run|install|pip|python|node|info|shell} [args...]" ;;
esac
