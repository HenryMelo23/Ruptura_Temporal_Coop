import threading
import queue
import socket
import json
import time
import requests
fila_envio = queue.Queue()
fila_recebimento = queue.Queue()
rodando_rede = True


def thread_envio(conn):
    while rodando_rede:
        try:
            dados = fila_envio.get(timeout=0.05)  # espera 50ms por pacotes
            json_data = json.dumps(dados) + "\n"  # adiciona delimitador
            conn.sendall(json_data.encode())
        except queue.Empty:
            continue
        except Exception as e:
            break



def thread_recebimento(conn):
    buffer = b""
    while rodando_rede:
        try:
            parte = conn.recv(4096)
            if not parte:
                break

            buffer += parte
            while b"\n" in buffer:
                pacote, buffer = buffer.split(b"\n", 1)
                try:
                    dados = json.loads(pacote.decode())
                    fila_recebimento.put(dados)
                except json.JSONDecodeError:
                    continue

        except Exception as e:
            break



def iniciar_host(porta=5050):
    import pygame, time, socket
    from Variaveis import largura_tela, altura_tela  # usa as mesmas dimensões do jogo

    pygame.init()
    tela = pygame.display.set_mode((largura_tela, altura_tela))
    fonte = pygame.font.Font("Texto/World.otf", 42)
    clock = pygame.time.Clock()

    # Cria o socket
    s = socket.socket()
    s.bind(("0.0.0.0", porta))
    s.listen(1)
    s.settimeout(0.1)  # não trava o loop


    # botão cancelar centralizado
    botao_cancelar = pygame.Rect(largura_tela // 2 - 120, altura_tela // 2 + 80, 240, 60)
    pontos = 0
    ultimo_tempo = time.time()

    # Obtém o IP local para mostrar na tela
    import socket
    ip_local = socket.gethostbyname(socket.gethostname())

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                s.close()
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                s.close()
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if botao_cancelar.collidepoint(event.pos):
                    s.close()
                    return None

        # animação dos pontinhos
        if time.time() - ultimo_tempo > 0.5:
            pontos = (pontos + 1) % 4
            ultimo_tempo = time.time()

        # tenta aceitar conexão sem travar
        try:
            conn, addr = s.accept()
            return conn
        except socket.timeout:
            pass

        # desenha a tela
        tela.fill((10, 10, 25))
        texto = fonte.render(f"Esperando Player 2{'.' * pontos}", True, (255, 255, 255))
        tela.blit(texto, (largura_tela // 2 - texto.get_width() // 2, altura_tela // 2 - 60))

        # mostra IP local
        ip_texto = fonte.render(f"IP do Host: {ip_local}", True, (180, 180, 0))
        tela.blit(ip_texto, (largura_tela // 2 - ip_texto.get_width() // 2, altura_tela // 2 + 10))

        # botão cancelar
        pygame.draw.rect(tela, (200, 60, 60), botao_cancelar, border_radius=15)
        txt_cancelar = fonte.render("Cancelar", True, (255, 255, 255))
        tela.blit(txt_cancelar, (largura_tela // 2 - txt_cancelar.get_width() // 2, botao_cancelar.y + 10))

        pygame.display.flip()
        clock.tick(30)

# ===============================================================
# === BROADCAST DE DESCOBERTA AUTOMÁTICA DO HOST (NOVIDADE) ====
# ===============================================================
def anunciar_host_udp(porta_udp=5051):
    """Host envia broadcast UDP para anunciar sua presença na rede local."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ip_local = socket.gethostbyname(socket.gethostname())
    mensagem = f"RupturaTemporalHost:{ip_local}".encode()

    def enviar():
        while rodando_rede:
            try:
                s.sendto(mensagem, ("<broadcast>", porta_udp))
                time.sleep(1)  # envia a cada 1s
            except Exception:
                break

    threading.Thread(target=enviar, daemon=True).start()
    
def descobrir_host_udp(porta_udp=5051, timeout=5):
    """Cliente escuta broadcasts UDP para detectar o IP do host."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", porta_udp))
    s.settimeout(timeout)

    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            data, addr = s.recvfrom(1024)
            msg = data.decode()
            if msg.startswith("RupturaTemporalHost:"):
                ip_host = msg.split(":")[1]
                print(f"[Descoberto Host] {ip_host}")
                return ip_host
        except socket.timeout:
            continue
        except Exception:
            break

    return None

def conectar_ao_host(ip, porta=5050):
    s = socket.socket()
    s.connect((ip, porta))
    return s

def iniciar_host_internet(porta=5050):
    import pygame, time, socket
    from Variaveis import largura_tela, altura_tela
    from rede import registrar_ip_host
    import pyperclip

    pygame.init()
    tela = pygame.display.set_mode((largura_tela, altura_tela))
    fonte = pygame.font.Font("Texto/World.otf", 42)
    clock = pygame.time.Clock()

    # Cria socket e inicia servidor
    s = socket.socket()
    s.bind(("0.0.0.0", porta))
    s.listen(1)
    s.settimeout(0.1)

    ip_local = socket.gethostbyname(socket.gethostname())
    token = registrar_ip_host(ip_local)

    botao_copiar = pygame.Rect(largura_tela // 2 + 150, altura_tela // 2, 150, 50)
    botao_cancelar = pygame.Rect(largura_tela // 2 - 120, altura_tela // 2 + 100, 240, 60)

    pontos = 0
    ultimo_tempo = time.time()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                s.close()
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                s.close()
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if botao_cancelar.collidepoint(event.pos):
                    s.close()
                    return None
                elif botao_copiar.collidepoint(event.pos):
                    if token:
                        pyperclip.copy(token)

        if time.time() - ultimo_tempo > 0.5:
            pontos = (pontos + 1) % 4
            ultimo_tempo = time.time()

        try:
            conn, addr = s.accept()
            return conn
        except socket.timeout:
            pass

        # Desenho da tela
        tela.fill((10, 10, 25))
        texto = fonte.render(f"Aguardando Player 2{'.' * pontos}", True, (255, 255, 255))
        tela.blit(texto, (largura_tela // 2 - texto.get_width() // 2, altura_tela // 2 - 120))

        ip_texto = fonte.render(f"Seu IP: {ip_local}", True, (180, 180, 0))
        tela.blit(ip_texto, (largura_tela // 2 - ip_texto.get_width() // 2, altura_tela // 2 - 40))

        token_texto = fonte.render(f"Token: {token}", True, (0, 255, 255))
        tela.blit(token_texto, (largura_tela // 2 - token_texto.get_width() // 2, altura_tela // 2 + 20))

        pygame.draw.rect(tela, (0, 180, 0), botao_copiar, border_radius=10)
        txt_copiar = fonte.render("Copiar", True, (255, 255, 255))
        tela.blit(txt_copiar, (botao_copiar.x + 15, botao_copiar.y + 5))

        pygame.draw.rect(tela, (200, 60, 60), botao_cancelar, border_radius=15)
        txt_cancelar = fonte.render("Cancelar", True, (255, 255, 255))
        tela.blit(txt_cancelar, (botao_cancelar.x + 25, botao_cancelar.y + 10))

        pygame.display.flip()
        clock.tick(30)

def conectar_ao_host_internet(token, porta=5050):
    import pygame, socket, time, requests
    from Variaveis import largura_tela, altura_tela
    from rede import obter_ip_host

    pygame.init()
    tela = pygame.display.set_mode((largura_tela, altura_tela))
    fonte = pygame.font.Font("Texto/World.otf", 42)
    clock = pygame.time.Clock()

    botao_cancelar = pygame.Rect(largura_tela // 2 - 120, altura_tela // 2 + 80, 240, 60)
    pontos = 0
    ultimo_tempo = time.time()

    ip_host = obter_ip_host(token)
    if not ip_host:
        tela.fill((10, 10, 25))
        erro_txt = fonte.render("Token inválido ou host indisponível", True, (255, 80, 80))
        tela.blit(erro_txt, (largura_tela // 2 - erro_txt.get_width() // 2, altura_tela // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        return None

    s = socket.socket()
    s.settimeout(3)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if botao_cancelar.collidepoint(event.pos):
                    pygame.quit()
                    return None

        try:
            s.connect((ip_host, porta))
            return s  # Conectado com sucesso
        except socket.timeout:
            pass
        except Exception as e:
            erro_txt = fonte.render(f"Erro: {str(e)}", True, (255, 80, 80))
            tela.blit(erro_txt, (largura_tela // 2 - erro_txt.get_width() // 2, altura_tela // 2 + 40))

        if time.time() - ultimo_tempo > 0.5:
            pontos = (pontos + 1) % 4
            ultimo_tempo = time.time()

        tela.fill((10, 10, 25))
        texto = fonte.render(f"Conectando ao Host{'.' * pontos}", True, (255, 255, 255))
        tela.blit(texto, (largura_tela // 2 - texto.get_width() // 2, altura_tela // 2 - 60))

        ip_texto = fonte.render(f"IP: {ip_host}", True, (180, 180, 0))
        tela.blit(ip_texto, (largura_tela // 2 - ip_texto.get_width() // 2, altura_tela // 2))

        pygame.draw.rect(tela, (200, 60, 60), botao_cancelar, border_radius=15)
        txt_cancelar = fonte.render("Cancelar", True, (255, 255, 255))
        tela.blit(txt_cancelar, (largura_tela // 2 - txt_cancelar.get_width() // 2, botao_cancelar.y + 10))

        pygame.display.flip()
        clock.tick(30)




def registrar_ip_host(ip_local=None):
    import requests
    try:
        # Descobre o IP público automaticamente
        ip_publico = requests.get("https://api.ipify.org").text
        response = requests.post(
            "https://servidor-matchmaking-gsmh.onrender.com/registrar",
            json={"ip": ip_publico},
            timeout=5
        )
        if response.status_code == 200:
            token = response.json().get("token")
            print(f"[SERVIDOR] IP público registrado: {ip_publico} | Token: {token}")
            return token
        else:
            print(f"[ERRO] Falha ao registrar no servidor: {response.text}")
            return None
    except Exception as e:
        print(f"[ERRO] Não foi possível registrar IP: {e}")
        return None
    




def obter_ip_host(token):
    url = f"https://servidor-matchmaking-gsmh.onrender.com/obter_ip_host?token={token}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("ip")
    return None