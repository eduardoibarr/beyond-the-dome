from core.game import Game 
from graphics.ui.screens import show_start_screen, show_go_screen, display_intro

# --- Inicialização do Jogo e Loop Principal ---
if __name__ == '__main__':
    g = Game()

    while g.running:
        show_start_screen(g) # Mostra a tela inicial
        if not g.running: # Verifica se o jogo foi fechado na tela inicial
            break

        # Mostra a introdução antes de iniciar o jogo
        display_intro(g)
        if not g.running: # Verifica se o jogo foi fechado durante a introdução
            break

        g.new() # Inicia uma nova sessão de jogo (chama g.run() internamente)

        # Se g.playing se tornou False (fim da sessão), mostra tela de game over
        if g.running: # Só mostra game over se não fechou a janela
             show_go_screen(g)

    # Limpa o Pygame e encerra
    g.quit()
