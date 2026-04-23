import socket
import threading
import argparse
import logging
import ipaddress
from queue import Queue
from typing import List

# Configuração de Logs (Boa prática: usar logging ao invés de prints soltos)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class PortScanner:
    """
    Classe responsável por gerenciar e executar o scan de portas.
    """
    def __init__(self, target: str, start_port: int, end_port: int, num_threads: int = 100, timeout: float = 1.0):
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.num_threads = num_threads
        self.timeout = timeout
        
        self.queue: Queue[int] = Queue()
        self.open_ports: List[int] = []
        self._lock = threading.Lock() # Lock para evitar condição de corrida ao alterar variáveis compartilhadas

    def _scan_port(self, port: int) -> bool:
        """
        Tenta conectar a uma porta específica para verificar se está aberta.
        """
        try:
            # Usando with para garantir o fechamento correto do socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                result = sock.connect_ex((self.target, port))
                return result == 0
        except socket.error:
            return False

    def _worker(self):
        """
        Função consumidora da fila. As threads rodam isso continuamente.
        """
        while not self.queue.empty():
            port = self.queue.get()
            if self._scan_port(port):
                # Usando lock para printar e adicionar à lista de forma segura (Thread-safe)
                with self._lock:
                    logging.info(f"Porta {port} está ABERTA")
                    self.open_ports.append(port)
            self.queue.task_done()

    def run(self, force_public: bool = False):
        """
        Configura a fila, inicia as threads e aguarda a conclusão.
        """
        # Resolve o hostname para IP (caso o usuário passe urls como "localhost" ou um site, embora para testes locais seja IP)
        try:
            target_ip = socket.gethostbyname(self.target)
            
            # Validação de Segurança (Prevenir scans acidentais na internet)
            ip_obj = ipaddress.ip_address(target_ip)
            if not ip_obj.is_private and not ip_obj.is_loopback:
                if not force_public:
                    logging.error(f"ALERTA DE SEGURANÇA: O IP {target_ip} é PÚBLICO!")
                    logging.error("Escanear redes externas pode ser considerado hostil, ilegal e pode atrair retaliações ou firewalls.")
                    logging.error("Use a flag --force-public se você realmente tiver autorização para escanear este alvo.")
                    return
                else:
                    logging.warning(f"AVISO: Escaneando IP PÚBLICO ({target_ip}) com a flag --force-public.")

            logging.info(f"Iniciando scan no alvo: {self.target} ({target_ip})")
            logging.info(f"Escaneando portas de {self.start_port} até {self.end_port}...")
        except socket.gaierror:
            logging.error(f"Não foi possível resolver o hostname: {self.target}")
            return
        except ValueError:
            logging.error(f"Falha ao validar o endereço IP: {target_ip}")
            return

        # Popula a fila com as portas a serem verificadas
        for port in range(self.start_port, self.end_port + 1):
            self.queue.put(port)

        threads: List[threading.Thread] = []
        
        # Cria e inicia as threads
        for _ in range(min(self.num_threads, self.queue.qsize())):
            thread = threading.Thread(target=self._worker)
            thread.daemon = True # Threads daemon fecham automaticamente se o programa principal fechar
            thread.start()
            threads.append(thread)

        # Aguarda a fila ser processada (Join bloqueia até todos os task_done() da fila)
        self.queue.join()
        
        # Ordena as portas antes de exibir (já que as threads terminam em ordens aleatórias)
        self.open_ports.sort()
        logging.info(f"Scan finalizado. Portas abertas encontradas: {self.open_ports}")


def main():
    # Usando argparse para permitir argumentos de linha de comando (Boa prática para ferramentas CLI)
    parser = argparse.ArgumentParser(description="Port Scanner Simples para uso local (Fins Educacionais)")
    parser.add_argument("target", help="Endereço IP ou hostname do alvo (ex: 192.168.1.1 ou localhost)")
    parser.add_argument("-s", "--start", type=int, default=1, help="Porta inicial (padrão: 1)")
    parser.add_argument("-e", "--end", type=int, default=1024, help="Porta final (padrão: 1024)")
    parser.add_argument("-t", "--threads", type=int, default=100, help="Número de threads a serem usadas (padrão: 100)")
    parser.add_argument("--timeout", type=float, default=1.0, help="Timeout da conexão em segundos (padrão: 1.0)")
    parser.add_argument("--force-public", action="store_true", help="Força a execução mesmo se o IP alvo for público (fora da rede local)")

    args = parser.parse_args()

    # Validação simples
    if args.start < 1 or args.end > 65535 or args.start > args.end:
        logging.error("Intervalo de portas inválido. Deve ser entre 1 e 65535, e o início deve ser menor/igual ao fim.")
        return

    # Inicia o scanner
    scanner = PortScanner(
        target=args.target,
        start_port=args.start,
        end_port=args.end,
        num_threads=args.threads,
        timeout=args.timeout
    )
    scanner.run(force_public=args.force_public)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScan interrompido pelo usuário.")
