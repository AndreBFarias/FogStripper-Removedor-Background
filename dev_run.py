import os
import sys
import json
import subprocess
import venv

print("### Iniciando FogStripper em Modo de Desenvolvedor (Ateliê Imutável) ###")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(PROJECT_ROOT, ".dev_venv")
os.chdir(PROJECT_ROOT)

def run_pip_install(python_executable, packages):
    command = [python_executable, "-m", "pip", "install"] + packages
    print(f"--> Executando: {' '.join(command)}")
    subprocess.run(command, check=True)

try:
    subprocess.run(["nvidia-smi"], capture_output=True, check=True)
    print("--> Detectada GPU NVIDIA. O Ateliê usará o poder da CUDA.")
    REMBG_REQS = "src/requirements_rembg.txt"

    TORCH_PACKAGES = ["torch==1.13.1", "torchvision==0.14.1", "--index-url", "https://download.pytorch.org/whl/cu117"]
except (subprocess.CalledProcessError, FileNotFoundError):
    print("--> Nenhuma GPU NVIDIA detectada. O Ateliê usará o poder da CPU.")
    REMBG_REQS = "src/requirements_rembg_cpu.txt"
    TORCH_PACKAGES = ["torch==1.13.1", "torchvision==0.14.1", "--index-url", "https://download.pytorch.org/whl/cpu"]

if not os.path.exists(VENV_DIR):
    print(f"--> Criando ambiente de desenvolvimento isolado em: {VENV_DIR}")
    venv.create(VENV_DIR, with_pip=True)

if sys.platform == "win32":
    python_executable = os.path.join(VENV_DIR, "Scripts", "python.exe")
else:
    python_executable = os.path.join(VENV_DIR, "bin", "python")

try:
    print("--> Verificando a alma do Ateliê...")

    subprocess.run([python_executable, "-c", "import realesrgan"], check=True, capture_output=True)
    print("--> Alma do Ateliê já está presente e correta.")
except (subprocess.CalledProcessError, FileNotFoundError):
    print("--> Alma do Ateliê não encontrada ou corrompida. Forjando dependências (isso pode levar vários minutos)...")
    run_pip_install(python_executable, ["--upgrade", "pip"])

    print("\n--> Forjando dependências da Interface...")
    run_pip_install(python_executable, ["-r", "requirements.txt"])

    print("\n--> Forjando dependências do Desnudamento...")
    run_pip_install(python_executable, ["-r", REMBG_REQS])

    print("\n--> Forjando fundações da Ampliação (Deuses)...")
    run_pip_install(python_executable, TORCH_PACKAGES)

    print("\n--> Forjando ferramentas da Ampliação (Servos em sua forma imutável)...")

    run_pip_install(python_executable, ["basicsr==1.4.2", "realesrgan==0.3.0"])

    run_pip_install(python_executable, ["--force-reinstall", "numpy==1.26.4"])

    print("--> Forja de dependências concluída.")

print("\n--- Gerando Símbolos (Modo de Teste) ---")
icon_resizer_script = os.path.join(PROJECT_ROOT, "tools", "icon_resizer.py")
if os.path.exists(icon_resizer_script):
    subprocess.run([python_executable, icon_resizer_script, PROJECT_ROOT], check=True, capture_output=True)
    print("--> Ícones gerados para teste em 'assets/generated_icons/'.")
print("--- Fim da Geração de Símbolos ---\n")

config_path = os.path.join(PROJECT_ROOT, "config.dev.json")
dev_config = {
    "PYTHON_REMBG": python_executable,
    "PYTHON_UPSCALE": python_executable,
    "REMBG_SCRIPT": os.path.join(PROJECT_ROOT, "src", "worker_rembg.py"),
    "UPSCALE_SCRIPT": os.path.join(PROJECT_ROOT, "src", "worker_upscale.py"),
    "EFFECTS_SCRIPT": os.path.join(PROJECT_ROOT, "src", "worker_effects.py"),
    "BACKGROUND_SCRIPT": os.path.join(PROJECT_ROOT, "src", "worker_background.py")
}
print(f"--> Forjando o Mapa de Desenvolvimento temporário em: {config_path}")
with open(config_path, 'w') as f:
    json.dump(dev_config, f, indent=4)

main_script_path = os.path.join(PROJECT_ROOT, "src", "main.py")
env = os.environ.copy()
env["FOGSTRIPPER_DEV_MODE"] = "1"
env["PYTHONPATH"] = os.path.join(PROJECT_ROOT, "src") + os.pathsep + env.get("PYTHONPATH", "")

try:
    print(f"--> Invocando a aplicação principal: {main_script_path}")
    subprocess.run([python_executable, main_script_path], env=env)
except (subprocess.CalledProcessError, KeyboardInterrupt):
    print("\n--> Aplicação encerrada.")
finally:
    if os.path.exists(config_path):
        print("--> Limpando o rastro do Mapa de Desenvolvimento...")
        os.remove(config_path)

print("### Sessão de Desenvolvimento Concluída ###")
