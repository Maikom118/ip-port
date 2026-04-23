# 🛡️ Python TCP Port Scanner (Educacional)

Um scanner de portas TCP rápido, assíncrono (multi-threaded) e seguro, desenvolvido em Python. Este projeto foi criado com foco em **boas práticas de programação** e **segurança defensiva**, sendo ideal para estudantes de cibersegurança e administradores de rede que desejam auditar suas próprias infraestruturas.

## ✨ Funcionalidades

- **Multi-threading (Rápido)**: Verifica dezenas de portas simultaneamente usando `threading` e `Queue`.
- **Interface de Linha de Comando (CLI)**: Totalmente customizável via terminal (alvo, intervalo de portas, threads, timeouts).
- **Safe-Lock (Trava de Segurança)**: Possui um mecanismo integrado que detecta IPs públicos e bloqueia scans acidentais na internet para evitar retaliações de firewalls externos.
- **Thread-safe**: Utiliza `threading.Lock()` para prevenir condições de corrida ao registrar portas abertas.
- **Limpeza de Recursos**: Construído com context managers (`with`) para garantir que sockets abertos sejam devidamente fechados.
- **Zero Dependências**: Usa exclusivamente bibliotecas padrão do Python (Standard Library). Nenhum `pip install` é necessário!

## 🚀 Como usar

### Pré-requisitos
- Python instalado na máquina (versão 3.6 ou superior).

### Uso Básico
Abra o terminal, navegue até a pasta do projeto e execute:
```bash
# Escaneia o localhost (127.0.0.1) nas portas padrão (1 a 1024)
python scanner.py 127.0.0.1
```

### Personalizando o Scan
Você pode ajustar as portas, a velocidade (threads) e o tempo de desistência (timeout):
```bash
# Escaneia da porta 20 a 80, usando 50 threads e 0.5s de timeout
python scanner.py 192.168.1.1 -s 20 -e 80 -t 50 --timeout 0.5
```

### Menu de Ajuda
Para ver todos os parâmetros disponíveis:
```bash
python scanner.py -h
```

### Escaneando IPs Públicos (Somente com Autorização)
O scanner possui uma trava de segurança que bloqueia a varredura caso você informe um IP público. Se você realmente tem autorização (ex: auditando seu próprio servidor na nuvem), use a flag `--force-public`:
```bash
# A flag anula o bloqueio defensivo
python scanner.py 8.8.8.8 --force-public
```

## 🧠 Boas Práticas Python Aplicadas
1. **POO (Orientação a Objetos)**: Lógica encapsulada.
2. **Type Hinting**: Facilita a manutenção do código indicando quais tipos de parâmetros a função precisa receber.
3. **Módulo Logging**: Logs profissionais indicando avisos (`WARNING`), erros (`ERROR`) e rotinas (`INFO`) no terminal com data e hora.
4. **Resolução Limpa de Erros**: Tratamento de `KeyboardInterrupt` para permitir paradas bruscas com `CTRL+C` de forma limpa.

---

**⚠️ AVISO LEGAL**: Este software foi feito **exclusivamente para fins educacionais**. O uso dessa ferramenta em redes/sistemas onde o utilizador não possui permissões explícitas é contra-indicado e pode infringir leis de crimes cibernéticos dependendo do seu país. Sempre obtenha autorização antes de auditar um alvo. O autor não se responsabiliza pelo mau uso da ferramenta.
