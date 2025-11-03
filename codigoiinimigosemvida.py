if modo == "host":
        # --- Atualiza e envia estado completo para o cliente ---
        estado = {
            "p1": {
                "x": pos_x_personagem,
                "y": pos_y_personagem,
                "direcao": direcao_atual,
                "morto": jogador_morto
            },
            "inimigos": [
                {
                    "x": inimigo["rect"].x,
                    "y": inimigo["rect"].y,
                    "vida": inimigo["vida"],
                    "vida_max": inimigo["vida_maxima"]
                }
                for inimigo in inimigos_comum
            ]
        }
        fila_envio.put(estado)
        
        while not fila_recebimento.empty():
            dados = fila_recebimento.get()
            if dados:
            ...

        # --- Tempo limite do convite ---
        if convite_boss_ativo and pygame.time.get_ticks() - convite_boss_tempo > 5000:
            convite_boss_ativo = False
            convite_boss_enviado = False
            convite_boss_recebido = False
        outro_jogador_morto = jogador_remoto_morto  # cliente remoto