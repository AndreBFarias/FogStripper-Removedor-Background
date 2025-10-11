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

if not os.path.exists(VENV_DIR):
    print(f"--> Criando ambiente de desenvolvimento isolado em: {VENV_DIR}")
    venv.create(VENV_DIR, with_pip=True)

if sys.platform == "win32":
    python_executable = os.path.join(VENV_DIR, "Scripts", "python.exe")
else:
    python_executable = os.path.join(VENV_DIR, "bin", "python")

try:
    print("--> Verificando a alma do Ateliê...")
    # Verifica a existência de um servo-chave do Reino da Ampliação
    subprocess.run([python_executable, "-c", "import realesrgan"], check=True, capture_output=True)
    print("--> Alma do Ateliê já está presente e correta.")
except (subprocess.CalledProcessError, FileNotFoundError):
    print("--> Alma do Ateliê não encontrada ou corrompida. Forjando dependências (isso pode levar vários minutos)...")
    run_pip_install(python_executable, ["--upgrade", "pip"])
    
    print("\n--> Forjando dependências da Interface...")
    run_pip_install(python_executable, ["-r", "requirements.txt"])
    
    print("\n--> Forjando dependências do Desnudamento...")
    run_pip_install(python_executable, ["-r", "src/requirements_rembg.txt"])
    
    print("\n--> Forjando fundações da Ampliação (Deuses)...")
    run_pip_install(python_executable, ["torch", "torchvision", "--index-url", "https://download.pytorch.org/whl/cu121"])
    
    print("\n--> Forjando ferramentas da Ampliação (Servos em sua forma imutável)...")
    # Decreta as versões exatas para garantir a paz eterna
    run_pip_install(python_executable, ["basicsr==1.4.2", "realesrgan==0.3.0"])
    
    print("--> Forja de dependências concluída.")

print("\n--- Ritual dos Símbolos (Modo de Teste) ---")
icon_resizer_script = os.path.join(PROJECT_ROOT, "tools", "icon_resizer.py")
if os.path.exists(icon_resizer_script):
    subprocess.run([python_executable, icon_resizer_script, PROJECT_ROOT], check=True, capture_output=True)
    print("--> Ícones gerados para teste em 'assets/generated_icons/'.")
print("--- Fim do Ritual dos Símbolos ---\n")

config_path = os.path.join(PROJECT_ROOT, "config.dev.json")
dev_config = {
    "PYTHON_REMBG": python_executable,
    "PYTHON_UPSCALE": python_executable,
    "REMBG_SCRIPT": os.path.join(PROJECT_ROOT, "src", "worker_rembg.py"),
    "UPSCALE_SCRIPT": os.path.join(PROJECT_ROOT, "src", "worker_upscale.py")
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
