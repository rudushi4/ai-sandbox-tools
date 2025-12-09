#!/usr/bin/env python3
"""
AI Sandbox Toolkit - Universal interface for AI models to use Ubuntu sandbox
"""

import subprocess
import json
import os
from typing import List, Dict, Any

SANDBOX_ROOT = "/workspace/ubuntu20-fs"
LAUNCH_SCRIPT = "/workspace/start-ubuntu20.sh"

class Sandbox:
    def __init__(self):
        self.root = SANDBOX_ROOT
        self.workspace = f"{self.root}/root/workspace"
        os.makedirs(self.workspace, exist_ok=True)

    def run(self, command: str, timeout: int = 300) -> Dict[str, Any]:
        try:
            result = subprocess.run([LAUNCH_SCRIPT, command], capture_output=True, text=True, timeout=timeout)
            return {"success": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def install(self, packages: List[str]) -> Dict[str, Any]:
        return self.run(f"DEBIAN_FRONTEND=noninteractive apt install -y {' '.join(packages)}")

    def pip_install(self, packages: List[str]) -> Dict[str, Any]:
        return self.run(f"pip3 install {' '.join(packages)}")

    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        full_path = f"{self.root}{path}" if path.startswith("/") else f"{self.workspace}/{path}"
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        try:
            with open(full_path, 'w') as f:
                f.write(content)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_file(self, path: str) -> Dict[str, Any]:
        full_path = f"{self.root}{path}" if path.startswith("/") else f"{self.workspace}/{path}"
        try:
            with open(full_path, 'r') as f:
                return {"success": True, "content": f.read()}
        except Exception as e:
            return {"success": False, "error": str(e)}

class AIToolkit:
    def __init__(self):
        self.sandbox = Sandbox()

    def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        ext_map = {"python": "py", "javascript": "js", "bash": "sh"}
        run_map = {"python": "python3", "javascript": "node", "bash": "bash"}
        ext = ext_map.get(language, "txt")
        runner = run_map.get(language, "cat")
        filename = f"/tmp/code_{os.getpid()}.{ext}"
        self.sandbox.write_file(filename, code)
        return self.sandbox.run(f"{runner} {filename}")

def api_handler(request: Dict[str, Any]) -> Dict[str, Any]:
    toolkit = AIToolkit()
    action = request.get("action")
    handlers = {
        "run": lambda: toolkit.sandbox.run(request.get("command", "")),
        "install": lambda: toolkit.sandbox.install(request.get("packages", [])),
        "pip_install": lambda: toolkit.sandbox.pip_install(request.get("packages", [])),
        "write_file": lambda: toolkit.sandbox.write_file(request.get("path", ""), request.get("content", "")),
        "read_file": lambda: toolkit.sandbox.read_file(request.get("path", "")),
        "execute_code": lambda: toolkit.execute_code(request.get("code", ""), request.get("language", "python")),
    }
    handler = handlers.get(action)
    return handler() if handler else {"success": False, "error": f"Unknown action: {action}"}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--json":
            print(json.dumps(api_handler(json.loads(sys.argv[2]))))
        else:
            result = Sandbox().run(" ".join(sys.argv[1:]))
            print(result["stdout"])
