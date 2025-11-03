import threading
import queue
import socket
import json
import time

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



def conectar_ao_host(ip, porta=5050):
    s = socket.socket()
    s.connect((ip, porta))
    return s


