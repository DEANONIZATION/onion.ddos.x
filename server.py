from flask import Flask, request, jsonify
import time
import threading
import random

app = Flask(__name__)

request_count = 0
start_time = time.time()
blocked_ips = set()

def get_stats():
    current_time = time.time()
    elapsed = current_time - start_time
    rps = request_count / elapsed if elapsed > 0 else 0
    return {
        'total_requests': request_count,
        'elapsed_time': round(elapsed, 2),
        'requests_per_second': round(rps, 2),
        'blocked_ips_count': len(blocked_ips)
    }

@app.route('/')
def home():
    global request_count
    request_count += 1
    
    client_ip = request.remote_addr
    
    if client_ip in blocked_ips:
        return jsonify({
            'status': 'blocked',
            'message': 'IP заблокирован за подозрительную активность',
            'your_ip': client_ip
        }), 403
    
    if request_count % 100 == 0:
        time.sleep(0.1)
    
    if request_count % 500 == 0:
        blocked_ips.add(client_ip)
        return jsonify({
            'status': 'blocked',
            'message': 'Слишком много запросов. IP временно заблокирован',
            'your_ip': client_ip
        }), 429
    
    response_time = random.uniform(0.01, 0.5)
    time.sleep(response_time)
    
    return jsonify({
        'status': 'success',
        'message': 'Добро пожаловать на тестовый сервер!',
        'your_ip': client_ip,
        'server_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_requests': request_count,
        'response_time': round(response_time, 3)
    })

@app.route('/api/data')
def api_data():
    global request_count
    request_count += 1
    
    client_ip = request.remote_addr
    
    if client_ip in blocked_ips:
        return jsonify({'error': 'IP заблокирован'}), 403
    
    response_time = random.uniform(0.05, 1.0)
    time.sleep(response_time)
    
    return jsonify({
        'data': [{'id': i, 'value': random.randint(1, 100)} for i in range(10)],
        'response_time': round(response_time, 3),
        'requests_count': request_count
    })

@app.route('/slow')
def slow_endpoint():
    global request_count
    request_count += 1
    
    delay = random.uniform(2, 5)
    time.sleep(delay)
    
    return jsonify({
        'status': 'slow_response',
        'delay': round(delay, 2),
        'message': 'Это медленный эндпоинт'
    })

@app.route('/error')
def error_endpoint():
    global request_count
    request_count += 1
    
    if random.random() > 0.7:
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500
    
    return jsonify({'status': 'ok', 'message': 'Иногда работает, иногда нет'})

@app.route('/stats')
def stats():
    stats_data = get_stats()
    return jsonify(stats_data)

@app.route('/reset')
def reset():
    global request_count, start_time, blocked_ips
    request_count = 0
    start_time = time.time()
    blocked_ips.clear()
    return jsonify({'status': 'reset', 'message': 'Статистика сброшена'})

@app.route('/block_me')
def block_me():
    client_ip = request.remote_addr
    blocked_ips.add(client_ip)
    return jsonify({'status': 'blocked', 'message': 'Ваш IP был заблокирован', 'ip': client_ip})

def print_stats():
    while True:
        time.sleep(5)
        stats_data = get_stats()
        print(f"\n📊 Статистика сервера:")
        print(f"   Всего запросов: {stats_data['total_requests']}")
        print(f"   RPS: {stats_data['requests_per_second']}")
        print(f"   Заблокировано IP: {stats_data['blocked_ips_count']}")
        print(f"   Время работы: {stats_data['elapsed_time']}с")

if __name__ == '__main__':
    print("🚀 Запуск тестового сервера...")
    print("📍 Доступные эндпоинты:")
    print("   GET / - Основная страница")
    print("   GET /api/data - API с данными") 
    print("   GET /slow - Медленный эндпоинт (2-5 сек)")
    print("   GET /error - Эндпоинт с ошибками")
    print("   GET /stats - Статистика сервера")
    print("   GET /reset - Сброс статистики")
    print("   GET /block_me - Блокировка вашего IP")
    print("\n📡 Сервер запущен: http://localhost:5000")
    print("⏹️  Для остановки нажмите Ctrl+C\n")
    
    stats_thread = threading.Thread(target=print_stats, daemon=True)
    stats_thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=False)