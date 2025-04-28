# Beyond the Dome (Nome Provisório?)

## Descrição

Beyond the Dome é um jogo de ação e aventura 2D desenvolvido em Python com Pygame.

**Enredo:** Kael é um técnico vivendo com sua família em Ômega-7, uma cidade futurista protegida por uma cúpula de energia controlada por uma inteligência artificial (IA). Quando recursos vitais começam a escassear, Kael é convocado pela IA para uma missão perigosa: aventurar-se fora da segurança da cúpula para recuperar suprimentos e peças essenciais em um mundo devastado por ventos tóxicos e radiação. Durante sua jornada por zonas industriais em ruínas e instalações abandonadas, Kael encontra saqueadores, enfrenta perigos ambientais e descobre segredos sombrios sobre a verdadeira natureza da devastação e o papel da IA, colocando em xeque tudo o que ele acredita e forçando-o a tomar decisões difíceis sobre o futuro de sua família e de Ômega-7.

## Objetivo do Jogo

O objetivo inicial de Kael é coletar componentes essenciais (peças do sistema de filtragem, suprimentos médicos, baterias) para reparar os sistemas de suporte de vida da cidade Ômega-7. Conforme a narrativa avança e Kael descobre mais sobre a IA e os saqueadores (liderados por um ex-"Kael"), o objetivo evolui. O jogador deverá decidir o destino da cidade: confiar na IA e restaurar seu controle para manter a segurança ilusória, ou desafiar a IA, desligar o sistema na Sala de Controle Central, revelar a dura verdade sobre o mundo exterior aos habitantes e enfrentar as consequências imprevisíveis.

## Tecnologias Utilizadas

- **Python 3.x**
- **Pygame:** Biblioteca principal para desenvolvimento de jogos 2D.
- **Noise:** Biblioteca para geração de ruído procedural (provavelmente usada para geração de terreno ou texturas).

## Estrutura do Projeto

O projeto está organizado da seguinte forma:

```
.
├── main.py             # Ponto de entrada principal do jogo
├── requirements.txt    # Lista de dependências Python
├── core/               # Lógica central do jogo (classe Game, etc.)
├── entities/           # Entidades do jogo (jogador, inimigos, NPCs)
├── graphics/           # Código relacionado a gráficos (UI, sprites, animações)
│   └── ui/
│       └── screens.py  # Funções para as diferentes telas (menu, game over)
├── projectiles/        # Lógica para projéteis
├── items/              # Lógica para itens coletáveis ou utilizáveis
├── level/              # Geração e gerenciamento de níveis/mapas
├── utils/              # Funções utilitárias diversas
├── assets/             # Arquivos de mídia (imagens, sons, fontes)
├── .gitignore          # Arquivos/pastas a serem ignorados pelo Git
└── README.md           # Este arquivo
```

## Instalação e Configuração

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd <NOME_DA_PASTA_DO_PROJETO>
    ```
2.  **Crie um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

## Como Executar

Após a instalação das dependências, execute o jogo a partir da raiz do projeto:

```bash
python main.py
```

## Como Adicionar Funcionalidades

A estrutura modular do projeto visa facilitar a adição de novos elementos:

- **Novas Entidades (Jogador, Inimigos):** Crie novas classes no diretório `entities/`. Considere criar classes base para comportamentos comuns (ex: `EnemyBase`, `Character`). Integre-os em `level/` ou `core/game.py`.
- **Novos Itens/Power-ups:** Adicione classes em `items/`. Implemente a lógica de coleta (colisão com jogador) e efeito (modificar status do jogador, inventário) em `entities/player.py` ou `core/game.py`.
- **Novos Níveis/Mapas:** Desenvolva a lógica de geração/carregamento em `level/`. Adicione assets (tilesets, mapas Tiled) em `assets/maps/` (sugestão de subpasta).
- **Novos Projéteis:** Crie classes em `projectiles/`. Modifique as entidades (`entities/`) que os disparam.
- **Novas Telas de UI/Diálogos:** Adicione funções/classes em `graphics/ui/`. Chame-as a partir do fluxo principal ou de gatilhos de eventos no jogo.
- **Novos Gráficos/Sons:** Adicione os arquivos em subpastas apropriadas de `assets/` (ex: `assets/images/enemies`, `assets/sounds/effects`) e atualize o código que os carrega.

## Contribuição

1.  Faça um fork do projeto.
2.  Crie uma nova branch (`git checkout -b feature/nova-funcionalidade`).
3.  Faça commit de suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`).
4.  Faça push para a branch (`git push origin feature/nova-funcionalidade`).
5.  Abra um Pull Request.

## Elementos do Jogo (Exemplo: Nível 1 - Zona Industrial em Ruínas)

- **Cenário:** Prédios destruídos, corredores instáveis, instalações tecnológicas abandonadas, áreas com alta radiação e gases tóxicos, pisos instáveis.
- **Inimigos:**
  - **Saqueadores:** Grupo organizado e armado (armas brancas) que tenta convencer Kael a lutar contra a IA. Podem ser combatidos, evitados ou imobilizados (arma de choque).
  - **Cães Selvagens (Treinados):** Rápidos e capazes de detectar o jogador. Podem ser evitados com furtividade, presos em armadilhas ou neutralizados.
- **Obstáculos:** Perigos ambientais como radiação e gás, que podem exigir o uso de itens ou power-ups para atravessar. Estruturas instáveis.
- **Itens Colecionáveis:** Peças do sistema de filtragem (objetivo primário), suprimentos médicos (cura), baterias de energia (para equipamentos).
- **Power-ups:**
  - **Máscara Reforçada:** Aumenta o tempo de resistência a ambientes tóxicos/radioativos.
