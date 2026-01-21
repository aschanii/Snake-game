import pygame
import random
import json
import os

# --- Configuration ---
WIDTH, HEIGHT = 640, 480
BLOCK = 20
FPS = 10
SAVE_FILE = "savegame.json"
HIGH_FILE = "highscore.txt"

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)
RED = (200, 0, 0)
BLUE = (0, 120, 255)
GRAY = (200, 200, 200)

# --- Utils highscore ---
def load_highscore():
    try:
        with open(HIGH_FILE, "r") as f:
            return int(f.read().strip() or 0)
    except Exception:
        return 0

def save_highscore(score):
    try:
        with open(HIGH_FILE, "w") as f:
            f.write(str(score))
    except Exception as e:
        print("Erreur en enregistrant highscore:", e)

# --- Utils save/load partie ---
def save_game(state):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(state, f)
        print("Partie sauvée dans", SAVE_FILE)
    except Exception as e:
        print("Erreur sauvegarde:", e)

def load_game():
    try:
        if not os.path.exists(SAVE_FILE):
            return None
        with open(SAVE_FILE, "r") as f:
            state = json.load(f)
        print("Partie chargée depuis", SAVE_FILE)
        return state
    except Exception as e:
        print("Erreur chargement:", e)
        return None

def random_food_position():
    x = random.randint(0, (WIDTH // BLOCK) - 1) * BLOCK
    y = random.randint(0, (HEIGHT // BLOCK) - 1) * BLOCK
    return [x, y]

# --- Boucle principale ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sneak (Snake) - double flèche = vitesse")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    bigfont = pygame.font.SysFont(None, 48)

    highscore = load_highscore()
    snake = [[WIDTH//2, HEIGHT//2]]
    direction = [BLOCK, 0]
    food = random_food_position()
    score = 0
    paused = False
    game_over = False

    # --- pour double appui flèche ---
    speed = FPS
    speed_increment = 2
    speed_max = 25
    last_key = None

    def reset_game():
        nonlocal snake, direction, food, score, paused, game_over, speed, last_key
        snake = [[WIDTH//2, HEIGHT//2]]
        direction = [BLOCK, 0]
        food = random_food_position()
        score = 0
        paused = False
        game_over = False
        speed = FPS
        last_key = None

    running = True
    while running:
        clock.tick(speed + score // 5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                key_pressed = None

                # Directions (flèches + WASD)
                if event.key in (pygame.K_UP, pygame.K_w):
                    if direction[1] == 0:
                        direction = [0, -BLOCK]
                        key_pressed = 'UP'
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if direction[1] == 0:
                        direction = [0, BLOCK]
                        key_pressed = 'DOWN'
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if direction[0] == 0:
                        direction = [-BLOCK, 0]
                        key_pressed = 'LEFT'
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if direction[0] == 0:
                        direction = [BLOCK, 0]
                        key_pressed = 'RIGHT'

                # --- double appui flèche → vitesse augmente ---
                if key_pressed:
                    if last_key == key_pressed:
                        speed = min(speed + speed_increment, speed_max)
                    last_key = key_pressed

                # Pause
                elif event.key == pygame.K_p and not game_over:
                    paused = not paused

                # Save / Load
                elif event.key == pygame.K_s:
                    state = {"snake": snake, "direction": direction, "food": food, "score": score, "speed": speed}
                    save_game(state)
                elif event.key == pygame.K_l:
                    loaded = load_game()
                    if loaded and all(k in loaded for k in ("snake","direction","food","score")):
                        snake = loaded["snake"]
                        direction = loaded["direction"]
                        food = loaded["food"]
                        score = loaded["score"]
                        speed = loaded.get("speed", FPS)
                        paused = False
                        game_over = False

                # Restart / Quit
                elif event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_q:
                    running = False

        if not paused and not game_over:
            head_x = snake[0][0] + direction[0]
            head_y = snake[0][1] + direction[1]

            # wrap-around bordures
            head_x %= WIDTH
            head_y %= HEIGHT

            new_head = [head_x, head_y]
            snake.insert(0, new_head)

            if new_head == food:
                score += 1
                while True:
                    food = random_food_position()
                    if food not in snake:
                        break
            else:
                snake.pop()

            if new_head in snake[1:]:
                game_over = True
                if score > highscore:
                    highscore = score
                    save_highscore(highscore)

        # --- dessin ---
        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, (food[0], food[1], BLOCK, BLOCK))
        for i, seg in enumerate(snake):
            color = BLUE if i == 0 else GREEN
            pygame.draw.rect(screen, color, (seg[0], seg[1], BLOCK, BLOCK))

        # hud = font.render(f"Score: {score}    Highscore: {highscore}    Speed: {speed}", True, WHITE)
        # instr = font.render("P:Pause  S:Save  L:Load  R:Restart  Q:Quit", True, GRAY)
        # screen.blit(hud, (10, 10))
        # screen.blit(instr, (10, 35))

        if paused:
            pause_text = bigfont.render("PAUSE - appuyez P pour reprendre", True, WHITE)
            screen.blit(pause_text, ((WIDTH - pause_text.get_width())//2, HEIGHT//2 - 30))
        if game_over:
            go_text = bigfont.render("GAME OVER", True, RED)
            info = font.render("R: Restart   Q: Quit   S: Save   L: Load", True, WHITE)
            final = font.render(f"Score final: {score}    Highscore: {highscore}", True, WHITE)
            screen.blit(go_text, ((WIDTH - go_text.get_width())//2, HEIGHT//2 - 40))
            screen.blit(info, ((WIDTH - info.get_width())//2, HEIGHT//2 + 20))
            screen.blit(final, ((WIDTH - final.get_width())//2, HEIGHT//2 + 60))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
