#!/usr/bin/env python3
"""
AI Sandbox Bridge - Connects AI models (Ollama) to Ubuntu sandbox
"""

import subprocess
import json
import requests
import sys
import os
import re
from typing import Optional, Dict, Any, List

OLLAMA_HOST = "http://127.0.0.1:11434"
SANDBOX_SCRIPT = "/workspace/start-ubuntu20.sh"

class SandboxExecutor:
    def run(self, command: str, timeout: int = 120) -> Dict[str, Any]:
        try:
            result = subprocess.run([SANDBOX_SCRIPT, command], capture_output=True, text=True, timeout=timeout)
            return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr if result.returncode != 0 else None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_and_run(self, filename: str, content: str, run_cmd: str) -> Dict[str, Any]:
        filepath = f"/tmp/{filename}"
        full_path = f"/workspace/ubuntu20-fs{filepath}"
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        return self.run(run_cmd.replace("{file}", filepath))

class OllamaClient:
    def __init__(self, host: str = OLLAMA_HOST):
        self.host = host

    def generate(self, model: str, prompt: str, system: str = None) -> str:
        data = {"model": model, "prompt": prompt, "stream": False}
        if system:
            data["system"] = system
        try:
            resp = requests.post(f"{self.host}/api/generate", json=data, timeout=120)
            return resp.json().get("response", "")
        except Exception as e:
            return f"Error: {e}"

    def list_models(self) -> List[str]:
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=10)
            return [m["name"] for m in resp.json().get("models", [])]
        except:
            return []

class AISandboxBridge:
    SYSTEM_PROMPT = "You are a coding assistant. Write ONLY code, no explanation. Use ```python or ```bash."

    def __init__(self, model: str = "tinyllama"):
        self.ollama = OllamaClient()
        self.sandbox = SandboxExecutor()
        self.model = model

    def code_and_run(self, task: str) -> Dict[str, Any]:
        response = self.ollama.generate(self.model, f"Write code for: {task}", self.SYSTEM_PROMPT)
        code = self._extract_code(response)
        if not code:
            return {"success": False, "error": "No code generated", "ai_response": response}
        lang, content = code.get("language", "python"), code.get("code", "")
        if lang == "python":
            result = self.sandbox.write_and_run("ai_code.py", content, "python3 {file}")
        elif lang in ["bash", "sh"]:
            result = self.sandbox.write_and_run("ai_code.sh", content, "bash {file}")
        else:
            result = {"success": False, "error": f"Unsupported: {lang}"}
        result["code"], result["language"] = content, lang
        return result

    def _extract_code(self, text: str) -> Optional[Dict[str, str]]:
        match = re.search(r'```(\w+)?\n(.*?)```', text, re.DOTALL)
        if match:
            return {"language": match.group(1) or "python", "code": match.group(2).strip()}
        if any(kw in text for kw in ['def ', 'import ', 'print(']):
            return {"language": "python", "code": text.strip()}
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: ./ai-sandbox-bridge.py {run|models|test} [args...]")
        return
    bridge = AISandboxBridge()
    cmd = sys.argv[1]
    if cmd == "models":
        print("Models:", bridge.ollama.list_models())
    elif cmd == "test":
        print(json.dumps(bridge.code_and_run("print current date and time"), indent=2))
    elif cmd == "run" and len(sys.argv) > 2:
        print(json.dumps(bridge.code_and_run(" ".join(sys.argv[2:])), indent=2))

if __name__ == "__main__":
    main()
