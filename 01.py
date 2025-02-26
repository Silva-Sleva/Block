import random
import pygame
import math
import os

in_menu = True
game_over = False


def draw_menu():
    window.fill((0, 0, 50))
    font = pygame.font.Font(None, 74)
    title_text = font.render("Block Blast!", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(window.get_width() // 2, window.get_height() // 3))

    button_font = pygame.font.Font(None, 50)
    play_text = button_font.render("Начать игру", True, (0, 0, 0))
    quit_text = button_font.render("Выйти", True, (0, 0, 0))

    button_width = max(play_text.get_width(), quit_text.get_width()) + 40
    button_height = play_text.get_height() + 20
    center_x = window.get_width() // 2 - button_width // 2
    center_y = window.get_height() // 2

    play_button = pygame.Rect(center_x, center_y, button_width, button_height)
    quit_button = pygame.Rect(center_x, center_y + 80, button_width, button_height)

    pygame.draw.rect(window, (255, 255, 255), play_button)
    pygame.draw.rect(window, (255, 255, 255), quit_button)

    window.blit(title_text, title_rect)
    window.blit(play_text, play_button.move(20, 10).topleft)
    window.blit(quit_text, quit_button.move(20, 10).topleft)

    return play_button, quit_button


pygame.init()
window = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    window.fill((30, 30, 30))

    if in_menu:
        play_button, quit_button = draw_menu()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    in_menu = False
                elif quit_button.collidepoint(event.pos):
                    running = False
    else:
        class Vector3D:
            def __init__(self, x, y, z):
                self.x, self.y, self.z = x, y, z
                self.magnitude = math.sqrt(x ** 2 + y ** 2 + z ** 2)

            def normalize(self):
                if self.magnitude == 0:
                    return self.copy()
                return Vector3D(self.x / self.magnitude, self.y / self.magnitude, self.z / self.magnitude)

            def copy(self):
                return Vector3D(self.x, self.y, self.z)

            def dot_product(self, other):
                return self.x * other.x + self.y * other.y + self.z * other.z

            def multiply(self, other):
                return Vector3D(self.x * other.x, self.y * other.y, self.z * other.z)

            def clamp(self, lower=(0, 0, 0), upper=(255, 255, 255)):
                return Vector3D(min(max(self.x, lower[0]), upper[0]), min(max(self.y, lower[1]), upper[1]),
                                min(max(self.z, lower[2]), upper[2]))

            def to_tuple(self):
                return (int(self.x), int(self.y), int(self.z))

            def __add__(self, other):
                return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

            def __sub__(self, other):
                return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

            def __mul__(self, scalar):
                return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

            def __truediv__(self, scalar):
                return Vector3D(self.x / scalar, self.y / scalar, self.z / scalar)

            def __str__(self):
                return f"{self.x} {self.y} {self.z}"


        class Vector2D:
            def __init__(self, x, y):
                self.x, self.y = x, y
                self.magnitude = math.sqrt(x ** 2 + y ** 2)

            def normalize(self):
                if self.magnitude == 0:
                    return self.copy()
                return Vector2D(self.x / self.magnitude, self.y / self.magnitude)

            def copy(self):
                return Vector2D(self.x, self.y)

            def dot_product(self, other):
                return self.x * other.x + self.y * other.y

            def multiply(self, other):
                return Vector2D(self.x * other.x, self.y * other.y)

            def clamp(self, lower=(0, 0), upper=(255, 255)):
                return Vector2D(min(max(self.x, lower[0]), upper[0]), min(max(self.y, lower[1]), upper[1]))

            def to_tuple(self):
                return (int(self.x), int(self.y))

            def __floordiv__(self, scalar):
                return Vector2D(self.x // scalar, self.y // scalar)

            def __add__(self, other):
                return Vector2D(self.x + other.x, self.y + other.y)

            def __sub__(self, other):
                return Vector2D(self.x - other.x, self.y - other.y)

            def __mul__(self, scalar):
                return Vector2D(self.x * scalar, self.y * scalar)

            def __truediv__(self, scalar):
                return Vector2D(self.x / scalar, self.y / scalar)

            def __str__(self):
                return f"{self.x} {self.y}"


        def random_vector():
            angle = math.tau * random.random()
            return Vector2D(math.sin(angle), math.cos(angle))


        with open("settings.txt", "r") as file:
            settings = file.read().split("\n")
            board_size = Vector2D(*map(int, settings[0].split(",")))
            cell_size = int(settings[1])

        pygame.init()
        window = pygame.display.set_mode((board_size.x * cell_size, board_size.y * cell_size + 150))
        clock = pygame.time.Clock()

        colors = [
            Vector3D(255, 100, 100),
            Vector3D(100, 255, 100),
            Vector3D(100, 100, 255),
            Vector3D(255, 255, 100),
            Vector3D(255, 100, 255),
            Vector3D(100, 255, 255),
        ]
        score, best_score = 0, 0


        def draw_cell(color, position, border=4, surface=window):
            pygame.draw.rect(surface, color.clamp().multiply(Vector3D(1, 1, 1)).to_tuple(),
                             (position.x, position.y, cell_size, cell_size))
            pygame.draw.rect(surface, color.multiply(Vector3D(0.8, 0.8, 0.8)).clamp().to_tuple(),
                             (position.x + border, position.y + border, cell_size - 2 * border, cell_size - 2 * border))


        def create_background():
            background = pygame.Surface((board_size.x * cell_size, board_size.y * cell_size))
            for x in range(board_size.x):
                for y in range(board_size.y):
                    draw_cell(Vector3D(20, 20, 20), Vector2D(x, y) * cell_size, surface=background)
            return background


        class Particle:
            def __init__(self, position, size):
                self.position, self.size = position, size
                self.direction = random_vector()
                self.speed = random.randint(0, 10)
                self.active = True

            def update(self):
                self.speed /= 1.1
                self.position += self.direction * self.speed
                self.size /= 1.2
                if self.size < 0.1:
                    self.active = False

            def draw(self):
                pygame.draw.rect(window, (255, 255, 255), (self.position.x, self.position.y, self.size, self.size))


        class ParticleSystem:
            def __init__(self):
                self.particles = []

            def add(self, particle):
                self.particles.append(particle)

            def update(self):
                self.particles = [p for p in self.particles if p.active]
                for p in self.particles:
                    p.update()

            def draw(self):
                for p in self.particles:
                    p.draw()


        particle_system = ParticleSystem()


        class GameBoard:
            def __init__(self, size):
                self.size = size
                self.grid = [[0 for _ in range(size.x)] for _ in range(size.y)]
                self.colors = [[Vector3D(0, 0, 0) for _ in range(size.x)] for _ in range(size.y)]

            def is_inside(self, position):
                return 0 <= position.x < self.size.x and 0 <= position.y < self.size.y

            def reset(self):
                self.grid = [[0 for _ in range(self.size.x)] for _ in range(self.size.y)]

            def can_place(self, block, position):
                for y in range(block.height):
                    for x in range(block.width):
                        if block.shape[y][x] == 1:
                            global_pos = position + Vector2D(x, y)
                            if not self.is_inside(global_pos) or self.grid[global_pos.y][global_pos.x] == 1:
                                return False
                return True

            def place_block(self, block, color, position):
                if self.can_place(block, position):
                    for y in range(block.height):
                        for x in range(block.width):
                            if block.shape[y][x] == 1:
                                self.grid[position.y + y][position.x + x] = 1
                                self.colors[position.y + y][position.x + x] = color
                    return True
                return False

            def clear_lines(self):
                global score
                rows_to_clear = [y for y in range(self.size.y) if all(self.grid[y])]
                cols_to_clear = [x for x in range(self.size.x) if all(self.grid[y][x] for y in range(self.size.y))]

                for y in rows_to_clear:
                    self.grid[y] = [0] * self.size.x
                    for x in range(self.size.x):
                        particle_system.add(
                            Particle(Vector2D(x, y) * cell_size + Vector2D(cell_size, cell_size) * 0.5,
                                     random.randint(0, 50)))

                for x in cols_to_clear:
                    for y in range(self.size.y):
                        self.grid[y][x] = 0
                        particle_system.add(
                            Particle(Vector2D(x, y) * cell_size + Vector2D(cell_size, cell_size) * 0.5,
                                     random.randint(0, 50)))

                score += (len(rows_to_clear) + len(cols_to_clear)) * 100

            def is_game_over(self, blocks):
                for block in blocks:
                    for y in range(self.size.y):
                        for x in range(self.size.x):
                            if self.can_place(block, Vector2D(x, y)):
                                return False
                return True

            def draw(self):
                for y in range(self.size.y):
                    for x in range(self.size.x):
                        color = self.colors[y][x] if self.grid[y][x] else Vector3D(50, 50, 50)
                        draw_cell(color, Vector2D(x, y) * cell_size)


        class Block:
            def __init__(self, shape):
                self.shape = shape
                self.width = len(shape[0])
                self.height = len(shape)


        board = GameBoard(board_size)


        class DraggableBlock:
            def __init__(self, block, position):
                self.block = block
                self.position = position
                self.color = random.choice(colors)

            def draw(self, current_block, mouse_position):
                if current_block != self:
                    temp_surface = pygame.Surface((500, 500), pygame.SRCALPHA)
                    for y in range(self.block.height):
                        for x in range(self.block.width):
                            if self.block.shape[y][x] == 1:
                                draw_cell(self.color, Vector2D(x, y) * cell_size, surface=temp_surface)
                    scaled_surface = pygame.transform.scale_by(temp_surface, 0.5)
                    window.blit(scaled_surface, self.position.to_tuple())
                    return

                can_fit = board.can_place(self.block, mouse_position // cell_size)
                for y in range(self.block.height):
                    for x in range(self.block.width):
                        if self.block.shape[y][x] == 1:
                            pos = mouse_position + Vector2D(x, y) * cell_size
                            draw_cell(self.color, pos // cell_size * cell_size if can_fit else pos)

            def is_hovered(self, mouse_position):
                scale = 0.5
                return (
                        self.position.x <= mouse_position.x <= self.position.x + self.block.width * cell_size * scale and
                        self.position.y <= mouse_position.y <= self.position.y + self.block.height * cell_size * scale)


        if os.path.exists("best_score.txt"):
            with open("best_score.txt", "r") as f:
                best_score = int(f.read())
        else:
            best_score = 0

        score = 0
        game_over = False
        in_menu = True


        def draw_menu():
            window.fill((0, 0, 50))
            font = pygame.font.Font(None, 74)
            title_text = font.render("Block Blast!", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(window.get_width() // 2, window.get_height() // 3))

            button_font = pygame.font.Font(None, 50)
            play_text = button_font.render("Играть", True, (0, 0, 0))
            button_width = play_text.get_width() + 40
            button_height = play_text.get_height() + 20
            play_button = pygame.Rect(window.get_width() // 2 - button_width // 2, window.get_height() // 2,
                                      button_width,
                                      button_height)

            pygame.draw.rect(window, (255, 255, 255), play_button)
            window.blit(title_text, title_rect)
            window.blit(play_text, play_button.move(20, 10).topleft)

            return play_button


        def save_best_score():
            with open("best_score.txt", "w") as f:
                f.write(str(best_score))


        def draw_game_over_screen():
            font = pygame.font.Font(None, 74)
            text = font.render("Game Over", True, (255, 255, 255))
            text_rect = text.get_rect(center=(window.get_width() // 2, window.get_height() // 3))

            button_font = pygame.font.Font(None, 50)

            retry_text = button_font.render("Попробовать снова", True, (0, 0, 0))
            quit_text = button_font.render("Выйти из игры", True, (0, 0, 0))

            button_width = max(retry_text.get_width(), quit_text.get_width()) + 40
            button_height = retry_text.get_height() + 20
            center_x = window.get_width() // 2 - button_width // 2
            center_y = window.get_height() // 2

            retry_button = pygame.Rect(center_x, center_y, button_width, button_height)
            quit_button = pygame.Rect(center_x, center_y + 80, button_width, button_height)

            pygame.draw.rect(window, (255, 255, 255), retry_button)
            pygame.draw.rect(window, (255, 255, 255), quit_button)

            window.blit(text, text_rect)
            window.blit(retry_text, retry_button.move(20, 10).topleft)
            window.blit(quit_text, quit_button.move(20, 10).topleft)

            return retry_button, quit_button


        def draw_score():
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Счёт: {score}", True, (255, 255, 255))
            best_score_text = font.render(f"Рекорд: {best_score}", True, (255, 255, 255))
            window.blit(score_text, (20, 20))
            window.blit(best_score_text, (20, 60))


        running = True
        background = create_background()
        current_block = None
        block_shapes = [
            [[1, 1], [1, 1]],
            [[1, 1, 1], [1, 1, 1]],
            [[1, 1], [1, 1], [1, 1]],
            [[1], [1], [1], [1]],
            [[1, 0], [1, 0], [1, 1]],
            [[1, 1, 0], [0, 1, 1]],
            [[1, 1, 1], [0, 1, 0]]
        ]

        blocks = [DraggableBlock(Block(random.choice(block_shapes)),
                                 Vector2D(board_size.x / 3 * i * cell_size + 50, board_size.y * cell_size + 50))
                  for i in range(3)]

        while running:
            mouse_pos = Vector2D(*pygame.mouse.get_pos())
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_best_score()
                    running = False
                elif game_over and event.type == pygame.MOUSEBUTTONDOWN:
                    retry_button, quit_button = draw_game_over_screen()
                    if retry_button.collidepoint(event.pos):
                        game_over = False
                        blocks = [DraggableBlock(Block(random.choice(block_shapes)),
                                                 Vector2D(board_size.x / 3 * i * cell_size + 50,
                                                          board_size.y * cell_size + 50))
                                  for i in range(3)]
                        current_block = None
                        board.reset()
                        score = 0
                    elif quit_button.collidepoint(event.pos):
                        save_best_score()
                        running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                save_best_score()
                running = False

            window.fill((30, 30, 30))

            if not game_over:
                if pygame.mouse.get_pressed()[0]:
                    for block in blocks:
                        if block.is_hovered(mouse_pos):
                            current_block = block
                            break
                else:
                    if current_block:
                        grid_position = mouse_pos // cell_size
                        if board.place_block(current_block.block, current_block.color, grid_position):
                            blocks.remove(current_block)
                            score += 10
                        current_block = None

                board.clear_lines()

                if not blocks:
                    blocks = [DraggableBlock(Block(random.choice(block_shapes)),
                                             Vector2D(board_size.x / 3 * i * cell_size + 50,
                                                      board_size.y * cell_size + 50))
                              for i in range(3)]

                if board.is_game_over([b.block for b in blocks]):
                    game_over = True

                particle_system.update()

            board.draw()
            for block in blocks:
                block.draw(current_block, mouse_pos)
            particle_system.draw()

            if score > best_score:
                best_score = score
                save_best_score()

            draw_score()

            if game_over:
                draw_game_over_screen()

            pygame.display.flip()
            clock.tick(60)
