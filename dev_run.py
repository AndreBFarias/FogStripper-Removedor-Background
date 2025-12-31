import os
import sys
import json
import subprocess
import venv

print("=" * 60, flush=True)
print("  FOGSTRIPPER - MODO DE DESENVOLVEDOR", flush=True)
print("=" * 60, flush=True)
print(flush=True)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(PROJECT_ROOT, ".dev_venv")
os.chdir(PROJECT_ROOT)


def run_pip_install(python_executable, packages):
    command = [python_executable, "-m", "pip", "install", "--no-cache-dir"] + packages
    print(f">> Executando: {' '.join(command)}", flush=True)
    pip_env = os.environ.copy()
    pip_env["TMPDIR"] = os.path.join(os.path.expanduser("~"), ".pip_tmp")
    os.makedirs(pip_env["TMPDIR"], exist_ok=True)
    subprocess.run(command, check=True, env=pip_env)


try:
    subprocess.run(["nvidia-smi"], capture_output=True, check=True)
    print(">> Detectada GPU NVIDIA. Usando CUDA.", flush=True)
    REMBG_REQS = "src/requirements_rembg.txt"

    TORCH_PACKAGES = ["torch==1.13.1", "torchvision==0.14.1", "--index-url", "https://download.pytorch.org/whl/cu117"]
except (subprocess.CalledProcessError, FileNotFoundError):
    print(">> Nenhuma GPU NVIDIA detectada. Usando CPU.", flush=True)
    REMBG_REQS = "src/requirements_rembg_cpu.txt"
    TORCH_PACKAGES = ["torch==1.13.1", "torchvision==0.14.1", "--index-url", "https://download.pytorch.org/whl/cpu"]

if not os.path.exists(VENV_DIR):
    print(f">> Criando ambiente de desenvolvimento isolado em: {VENV_DIR}", flush=True)
    venv.create(VENV_DIR, with_pip=True)

if sys.platform == "win32":
    python_executable = os.path.join(VENV_DIR, "Scripts", "python.exe")
else:
    python_executable = os.path.join(VENV_DIR, "bin", "python")

try:
    print(">> Verificando dependencias...", flush=True)

    subprocess.run([python_executable, "-c", "import realesrgan"], check=True, capture_output=True)
    print(">> Dependencias verificadas.", flush=True)
except (subprocess.CalledProcessError, FileNotFoundError):
    print(flush=True)
    print("=" * 60, flush=True)
    print("=" * 60, flush=True)
    print("  INSTALACAO DE DEPENDENCIAS", flush=True)
    print("  (Isso pode demorar alguns minutos na primeira vez)", flush=True)
    print("=" * 60, flush=True)
    print(flush=True)

    print("[1/2] Atualizando pip...", flush=True)
    run_pip_install(python_executable, ["--upgrade", "pip"])

    print(flush=True)
    print("[2/2] Instalando todas as dependencias do projeto...", flush=True)
    # Using the unified requirements.txt which includes rembg, torch, realesrgan etc.
    run_pip_install(python_executable, ["-r", "requirements.txt"])

    print(flush=True)
    print("=" * 60, flush=True)
    print("  INSTALACAO CONCLUIDA!", flush=True)
    print("=" * 60, flush=True)
    print(flush=True)

print("\n--- Gerando icones ---", flush=True)
icon_resizer_script = os.path.join(PROJECT_ROOT, "src", "utils", "icon_resizer.py")
if os.path.exists(icon_resizer_script):
    subprocess.run([python_executable, icon_resizer_script, PROJECT_ROOT], check=True, capture_output=True)
    print(">> Icones gerados em 'assets/generated_icons/'.", flush=True)
print("--- Fim da geracao de icones ---\n", flush=True)

config_path = os.path.join(PROJECT_ROOT, "config.dev.json")
dev_config = {
    "PYTHON_REMBG": python_executable,
    "PYTHON_UPSCALE": python_executable,
    "REMBG_SCRIPT": os.path.join(PROJECT_ROOT, "src", "workers", "worker_rembg.py"),
    "UPSCALE_SCRIPT": os.path.join(PROJECT_ROOT, "src", "workers", "worker_upscale.py"),
    "EFFECTS_SCRIPT": os.path.join(PROJECT_ROOT, "src", "workers", "worker_effects.py"),
    "BACKGROUND_SCRIPT": os.path.join(PROJECT_ROOT, "src", "workers", "worker_background.py"),
}
print(f">> Criando configuracao de desenvolvimento em: {config_path}", flush=True)
with open(config_path, "w") as f:
    json.dump(dev_config, f, indent=4)

main_script_path = os.path.join(PROJECT_ROOT, "src", "main.py")
env = os.environ.copy()
env["FOGSTRIPPER_DEV_MODE"] = "1"
env["PYTHONPATH"] = os.path.join(PROJECT_ROOT, "src") + os.pathsep + env.get("PYTHONPATH", "")

try:
    print(f">> Invocando a aplicação principal: {main_script_path}", flush=True)
    subprocess.run([python_executable, main_script_path], env=env)
except (subprocess.CalledProcessError, KeyboardInterrupt):
    print("\n>> Aplicação encerrada.", flush=True)
finally:
    if os.path.exists(config_path):
        print(">> Removendo configuracao temporaria...", flush=True)
        os.remove(config_path)

print("### Sessao de Desenvolvimento Concluida ###", flush=True)
