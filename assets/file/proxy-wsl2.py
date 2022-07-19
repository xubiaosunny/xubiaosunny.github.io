#!python3
import os
import sys
import logging
from pathlib import Path


WIN_BASE_DIR = str(Path(__file__).resolve().parent)
WSL2_BASE_DIR = WIN_BASE_DIR.replace('C:', '/mnt/c').replace('\\', '/')

file_handler = logging.FileHandler(os.path.join(WIN_BASE_DIR, 'proxy-wsl2.log'), encoding='UTF-8')
console_handler = logging.StreamHandler()
logging.basicConfig(
    level=logging.INFO, 
    format='[%(asctime)s %(filename)s:%(lineno)d %(levelname)s] - %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[file_handler, console_handler]
)

if (len(sys.argv) < 4):
    print('param error!')
    print('proxy-wsl2.py <listen_port> <connect_port> <wsl2_password>')
    sys.exit(1)

listen_port = sys.argv[1]
connect_port = sys.argv[2]
wsl2_password = sys.argv[3]

WIN_BASE_DIR = str(Path(__file__).resolve().parent)
WSL2_BASE_DIR = WIN_BASE_DIR.replace('C:', '/mnt/c').replace('\\', '/')
logging.info(f'WIN_BASE_DIR is {WIN_BASE_DIR}')
logging.info(f'WSL2_BASE_DIR is {WSL2_BASE_DIR}')

out = os.popen(f'bash.exe -c "echo {wsl2_password}|sudo -S /etc/init.d/ssh restart"')
logging.info(f'start sshd: {out.read()}')
print(f'bash.exe -c "cd {WSL2_BASE_DIR} && ./get_wsl2_ip.sh"')
out = os.popen(f'bash.exe -c "cd {WSL2_BASE_DIR} && ./get_wsl2_ip.sh"')
wsl2_ip = out.read().strip()
logging.info(f'WSL2 IP is {wsl2_ip}')
out = os.popen(f'netsh interface portproxy add v4tov4 listenport={listen_port} listenaddress=0.0.0.0 connectport={connect_port} connectaddress={wsl2_ip}')
logging.info(f'port proxy: {out.read()}')
