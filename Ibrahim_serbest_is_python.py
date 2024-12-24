import os
import subprocess
import logging
import json
from datetime import datetime

logging.basicConfig(
    filename="honeynet_automation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def log_message(level, message):
    """
    Logları konsolda və faylda göstərmək üçün funksiya.
    """
    print(f"{datetime.now()} - {level.upper()} - {message}")
    if level.lower() == "info":
        logging.info(message)
    elif level.lower() == "error":
        logging.error(message)
    elif level.lower() == "warning":
        logging.warning(message)


def setup_honeypot():
    """
    Cowrie Honeypot-u quraşdırır və mühit hazırlayır.
    """
    try:
        log_message("info", "Cowrie Honeypot quraşdırılması başlayır...")
        
        if not os.path.exists("cowrie"):
            subprocess.run(["git", "clone", "https://github.com/cowrie/cowrie.git"], check=True)
            log_message("info", "Cowrie deposu uğurla klonlandı.")
        else:
            log_message("warning", "Cowrie deposu artıq mövcuddur, yenidən klonlanmadı.")
       
        if not os.path.exists("cowrie-env"):
            subprocess.run(["python3", "-m", "venv", "cowrie-env"], check=True)
            log_message("info", "Virtual mühit uğurla yaradıldı.")
        
        subprocess.run(["cowrie-env/bin/pip", "install", "-r", "cowrie/requirements.txt"], check=True)
        log_message("info", "Asılılıqlar uğurla quraşdırıldı.")
    except subprocess.CalledProcessError as e:
        log_message("error", f"Cowrie quraşdırılmasında xəta: {e}")

def configure_honeypot():
    """
    Cowrie Honeypot-un konfiqurasiya faylını yeniləyir.
    """
    try:
        config_path = "cowrie/etc/cowrie.cfg"
        if os.path.exists(config_path):
            log_message("info", "Cowrie konfiqurasiya faylı yenilənir...")
            with open(config_path, "a") as config_file:
                config_file.write("\n# Custom Configuration\nhostname = 'Honeypot-Server'\n")
            log_message("info", "Konfiqurasiya faylı uğurla yeniləndi.")
        else:
            log_message("warning", "Konfiqurasiya faylı tapılmadı!")
    except Exception as e:
        log_message("error", f"Konfiqurasiya faylının yenilənməsində xəta: {e}")

def start_honeypot():
    """
    Cowrie Honeypot-u işə salır.
    """
    try:
        log_message("info", "Honeypot işə salınır...")
        subprocess.run(["cowrie-env/bin/python", "cowrie/bin/cowrie", "start"], check=True)
        log_message("info", "Honeypot uğurla işə salındı!")
    except subprocess.CalledProcessError as e:
        log_message("error", f"Honeypot-un işə salınmasında xəta: {e}")

def collect_logs():
    """
    Honeypot loglarını oxuyur və JSON formatına çevirir.
    """
    try:
        log_path = "./cowrie/var/log/cowrie/cowrie.json"
        if os.path.exists(log_path):
            log_message("info", "Loglar oxunur və analiz edilir...")
            with open(log_path, "r") as log_file:
                logs = [json.loads(line) for line in log_file]
         
            with open("honeynet_logs.json", "w") as output_file:
                json.dump(logs, output_file, indent=4)
            log_message("info", "Loglar JSON faylına yazıldı!")
        else:
            log_message("warning", "Log faylı tapılmadı!")
    except Exception as e:
        log_message("error", f"Logların toplanmasında xəta: {e}")

def execute_ssh_command(host, username, password, command):
    """
    SSH bağlantısı vasitəsilə uzaq əmr icra edir.
    """
    try:
        ssh_command = f"sshpass -p {password} ssh -o StrictHostKeyChecking=no {username}@{host} {command}"
        log_message("info", f"SSH əmr icra olunur: {command}")
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            log_message("info", f"Əmr nəticəsi: {result.stdout}")
        else:
            log_message("error", f"Əmr icrasında xəta: {result.stderr}")
    except Exception as e:
        log_message("error", f"SSH əmr icrasında xəta: {e}")

def main():
    """
    Honeynet yerləşdirilməsini avtomatlaşdırır.
    """
    log_message("info", "Honeynet yerləşdirilməsi başlayır...")
    setup_honeypot()
    configure_honeypot()
    start_honeypot()
    collect_logs()

    execute_ssh_command("127.0.0.1", "test_user", "test_password", "ls -la")
    log_message("info", "Honeynet yerləşdirilməsi tamamlandı!")

if __name__ == "__main__":
    main()