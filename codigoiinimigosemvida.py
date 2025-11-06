if modo == "host":
        while not fila_recebimento.empty():
            dados = fila_recebimento.get()
            if dados:
                
                if "ping" in dados:
                    try:
                        fila_envio.put({"pong": pygame.time.get_ticks()})
                    except:
                        pass
elif modo == "join":
        # Medir ping: envia um pacote de teste e mede o tempo de resposta
        if pygame.time.get_ticks() - tempo_envio_ping > 1000:  # mede a cada 1 segundo
            
            tempo_envio_ping = pygame.time.get_ticks()
            try:
                fila_envio.put({"ping": True})
            except:
                pass

        while not fila_recebimento.empty():
            dados = fila_recebimento.get()
            if dados:
                
                if "p1" in dados:
                    pos_x_player2 = dados["p1"]["x"]
                    pos_y_player2 = dados["p1"]["y"]
                    direcao_player2 = dados["p1"].get("direcao", "down")
                    host_ativo = True  # Se o host enviou dados, o host está ativo
                    if "morto" in dados["p1"]:
                        jogador_remoto_morto = dados["p1"]["morto"]
                # --- Recebe e sincroniza inimigos ---
                if "inimigos" in dados:
                    inimigos_recebidos = dados["inimigos"]
                    inimigos_comum = []
                    for inimigo in inimigos_recebidos:
                        novo = criar_inimigo(inimigo["x"], inimigo["y"])
                        novo["vida"] = inimigo["vida"]
                        novo["vida_maxima"] = inimigo["vida_max"]
                        inimigos_comum.append(novo)
                if "pong" in dados:
                    ping_atual = pygame.time.get_ticks() - dados["pong"]
                    # Define a cor conforme o ping
                    if ping_atual < 80:
                        cor_ping = (0, 255, 0)       # Verde
                    elif ping_atual < 160:
                        cor_ping = (255, 255, 0)     # Amarelo
                    else:
                        cor_ping = (255, 0, 0)       # Vermelho