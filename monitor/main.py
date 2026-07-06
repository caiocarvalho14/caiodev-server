import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psutil
import docker

app = FastAPI()

# Permite que o seu HTML (rodando no Nginx na porta 80) acesse esta API (porta 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o cliente do Docker apontando para o socket interno do container
try:
    client = docker.from_env()
except Exception as e:
    print(f"Erro ao conectar ao Docker Socket: {e}")
    client = None

CONTAINER_NAME = "minecraft_geyser_server"

# --- ROTAS DE DESEMPENHO DO SERVIDOR (HOST) ---

@app.get("/api/host/stats")
def get_host_stats():
    # psutil lê os dados usando o volume /host mapeado no docker-compose
    # Se rodar direto no host, lê direto da máquina.
    uptime_seconds = time.time() - psutil.boot_time()
    
    return {
        "cpu_usage": psutil.cpu_percent(interval=0.5),
        "ram_usage": psutil.virtual_memory().percent,
        "uptime": format_uptime(uptime_seconds)
    }

@app.post("/api/host/shutdown")
def shutdown_host():
    # Comandos de desligamento exigem privilégios. 
    # Como o container roda isolado, o comando ideal é disparar via sysrq ou um script no host,
    # mas uma tentativa direta via comando mapeado seria:
    os.system("shutdown -h now")
    return {"message": "Comando de desligamento enviado ao sistema."}


# --- ROTAS DO MINECRAFT ---

def get_minecraft_container():
    if not client:
        raise HTTPException(status_code=500, detail="Docker não disponível no backend.")
    try:
        return client.containers.get(CONTAINER_NAME)
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container do Minecraft não encontrado.")

@app.get("/api/minecraft/status")
def get_minecraft_status():
    container = get_minecraft_container()
    return {"status": container.status} # Retorna 'running', 'exited', etc.

@app.post("/api/minecraft/{action}")
def control_minecraft(action: str):
    container = get_minecraft_container()
    if action == "start":
        container.start()
    elif action == "stop":
        container.stop()
    elif action == "restart":
        container.restart()
    else:
        raise HTTPException(status_code=400, detail="Ação inválida. Use start, stop ou restart.")
    return {"message": f"Servidor do Minecraft recebeu comando: {action}"}

@app.get("/api/minecraft/logs")
def get_minecraft_logs():
    container = get_minecraft_container()
    # Pega as últimas 40 linhas de logs/chat codificados em UTF-8
    logs = container.logs(tail=40).decode("utf-8")
    return {"logs": logs.split("\n")}

@app.post("/api/minecraft/command")
def send_minecraft_command(payload: dict):
    command = payload.get("command")
    if not command:
        raise HTTPException(status_code=400, detail="Comando não enviado.")
    
    container = get_minecraft_container()
    
    # Executa o comando via rcon-cli que já vem embutido na imagem do itzg
    # Remova a barra '/' se o usuário digitar, pois o rcon não usa barra nos comandos internos
    clean_command = command.lstrip("/")
    exec_result = container.exec_run(f'rcon-cli "{clean_command}"')
    
    return {"output": exec_result.output.decode("utf-8")}


# --- FUNÇÃO AUXILIAR ---
def format_uptime(seconds):
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{int(days)}d {int(hours)}h {int(minutes)}m"