import pygame, random

from enemy import Enemy
from player import Player
from bullet import Bullet
from room import Room
from power import PowerUp
import os


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Binding of Isaac clone")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("arial", 40)

        self.reset()

    def reset(self):
        """Reset game state for restart"""
        self.all_sprites = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.player = Player((WINDOW_WIDTH//2, WINDOW_HEIGHT//2), self.all_sprites, self.bullet_group)

        num_rooms = random.randint(6, 10)
        self.rooms = self.generate_rooms(num_rooms)
        self.current_room = self.rooms[(0,0)]
        self.current_room.visited = True

        for room in self.rooms.values():
            room.spawn_enemies(self.player, self.bullet_group)
            room.spawn_powerups()

    def button(self, text, x, y, w, h, inactive_color, active_color):
        """Draw a button and return True if clicked"""
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        # hover effect
        if x+w > mouse[0] > x and y+h > mouse[1] > y:
            pygame.draw.rect(self.screen, active_color, (x, y, w, h))
            if click[0] == 1:
                return True
        else:
            pygame.draw.rect(self.screen, inactive_color, (x, y, w, h))

        text_surf = self.font.render(text, True, (0,0,0))
        text_rect = text_surf.get_rect(center=(x+w//2, y+h//2))
        self.screen.blit(text_surf, text_rect)
        return False

    

    

    def start_screen(self):
        """Show start menu with rounded button, centered title, and floating enemy images"""
        # load enemy images
        enemy_types = next(os.walk("images/enemies"))[1]
        enemy_images = []
        for etype in enemy_types:
            folder = os.path.join("images/enemies", etype)
            files = sorted(os.listdir(folder), key=lambda n: int(n.split('.')[0]))
            if files:
                img = pygame.image.load(os.path.join(folder, files[0])).convert_alpha()
                img = pygame.transform.scale(img, (50, 50))
                enemy_images.append(img)

        # generate positions and velocities for floating effect
        enemies = []
        for _ in range(15):
            pos = [random.randint(0, WINDOW_WIDTH - 50), random.randint(0, WINDOW_HEIGHT - 50)]
            # increased speed: random values between -60 and 60 pixels/sec
            vel = [random.choice([-60, -50, -40, 40, 50, 60]), random.choice([-60, -50, -40, 40, 50, 60])]
            img = random.choice(enemy_images)
            enemies.append({'pos': pos, 'vel': vel, 'img': img})

        title_font = pygame.font.SysFont("comicsansms", 80)
        button_font = pygame.font.SysFont("comicsansms", 30)

        button_width, button_height = 180, 50
        button_x = WINDOW_WIDTH // 2 - button_width // 2
        button_y = 400

        dt = 0
        clock = pygame.time.Clock()
        waiting = True
        while waiting:
            dt = clock.tick(60) / 1000.0  # seconds per frame
            self.screen.fill((30, 30, 30))

            # update enemy positions
            for e in enemies:
                e['pos'][0] += e['vel'][0] * dt
                e['pos'][1] += e['vel'][1] * dt

                # bounce off edges
                if e['pos'][0] < 0 or e['pos'][0] > WINDOW_WIDTH - 50:
                    e['vel'][0] *= -1
                if e['pos'][1] < 250 or e['pos'][1] > WINDOW_HEIGHT - 50:
                    e['vel'][1] *= -1

                self.screen.blit(e['img'], e['pos'])

            # draw title
            title = title_font.render("The Path of GineShko", True, (255, 255, 255))
            title_x = WINDOW_WIDTH // 2 - title.get_width() // 2
            title_y = button_y - title.get_height() - 40
            self.screen.blit(title, (title_x, title_y))

            # draw rounded button
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            color_idle = (100, 200, 100)
            color_hover = (50, 255, 50)
            color = color_hover if button_x + button_width > mouse[0] > button_x and button_y + button_height > mouse[
                1] > button_y else color_idle

            pygame.draw.rect(self.screen, color, (button_x, button_y, button_width, button_height), border_radius=12)

            if color == color_hover and click[0] == 1:
                waiting = False

            # draw button text
            text_surf = button_font.render("Start Game", True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
            self.screen.blit(text_surf, text_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            pygame.display.update()


    def game_over_screen(self):
        """Game Over menu with floating enemies, rounded buttons, and red theme"""

        # load enemy images
        enemy_types = next(os.walk("images/enemies"))[1]
        enemy_images = []
        for etype in enemy_types:
            folder = os.path.join("images", "enemies", etype)
            files = sorted(os.listdir(folder), key=lambda n: int(n.split('.')[0]))
            if files:
                img = pygame.image.load(os.path.join(folder, files[0])).convert_alpha()
                img = pygame.transform.scale(img, (50, 50))
                enemy_images.append(img)

        # generate positions and velocities for floating effect
        enemies = []
        for _ in range(15):
            pos = [random.randint(0, WINDOW_WIDTH - 50), random.randint(0, WINDOW_HEIGHT - 50)]
            vel = [random.choice([-80, -60, -40, 40, 60, 80]), random.choice([-80, -60, -40, 40, 60, 80])]
            img = random.choice(enemy_images)
            enemies.append({'pos': pos, 'vel': vel, 'img': img})

        title_font = pygame.font.SysFont("comicsansms", 80)
        button_font = pygame.font.SysFont("comicsansms", 30)

        button_width, button_height = 150, 50
        spacing = 40
        total_width = button_width * 2 + spacing
        start_x = WINDOW_WIDTH // 2 - total_width // 2
        restart_x = start_x
        quit_x = start_x + button_width + spacing
        button_y = 400

        dt = 0
        clock = pygame.time.Clock()
        waiting = True
        while waiting:
            dt = clock.tick(60) / 1000.0
            self.screen.fill((50, 0, 0))  # dark red background

            # update and draw floating enemies
            for e in enemies:
                e['pos'][0] += e['vel'][0] * dt
                e['pos'][1] += e['vel'][1] * dt

                if e['pos'][0] < 0 or e['pos'][0] > WINDOW_WIDTH - 50:
                    e['vel'][0] *= -1
                if e['pos'][1] < 0 or e['pos'][1] > WINDOW_HEIGHT - 50:
                    e['vel'][1] *= -1

                self.screen.blit(e['img'], e['pos'])

            # draw Game Over title
            title = title_font.render("Game Over", True, (255, 100, 100))
            title_x = WINDOW_WIDTH // 2 - title.get_width() // 2
            title_y = button_y - title.get_height() - 40
            self.screen.blit(title, (title_x, title_y))

            # mouse info
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()

            # draw Restart button
            restart_color = (200, 100, 100)
            if restart_x < mouse[0] < restart_x + button_width and button_y < mouse[1] < button_y + button_height:
                restart_color = (255, 50, 50)
                if click[0] == 1:
                    self.reset()
                    waiting = False
            pygame.draw.rect(self.screen, restart_color, (restart_x, button_y, button_width, button_height),
                             border_radius=12)
            restart_text = button_font.render("Restart", True, (0, 0, 0))
            restart_rect = restart_text.get_rect(center=(restart_x + button_width // 2, button_y + button_height // 2))
            self.screen.blit(restart_text, restart_rect)

            # draw Quit button
            quit_color = (200, 100, 100)
            if quit_x < mouse[0] < quit_x + button_width and button_y < mouse[1] < button_y + button_height:
                quit_color = (255, 50, 50)
                if click[0] == 1:
                    pygame.quit()
                    exit()
            pygame.draw.rect(self.screen, quit_color, (quit_x, button_y, button_width, button_height), border_radius=12)
            quit_text = button_font.render("Quit", True, (0, 0, 0))
            quit_rect = quit_text.get_rect(center=(quit_x + button_width // 2, button_y + button_height // 2))
            self.screen.blit(quit_text, quit_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            pygame.display.update()

    def victory_screen(self):
        """Victory menu with floating enemies, green theme, and Restart/Quit buttons"""

        # load enemy images
        enemy_types = next(os.walk("images/enemies"))[1]
        enemy_images = []
        for etype in enemy_types:
            folder = os.path.join("images/enemies", etype)
            files = sorted(os.listdir(folder), key=lambda n: int(n.split('.')[0]))
            if files:
                img = pygame.image.load(os.path.join(folder, files[0])).convert_alpha()
                img = pygame.transform.scale(img, (50, 50))
                enemy_images.append(img)

        # generate positions and velocities for floating effect
        enemies = []
        for _ in range(15):
            pos = [random.randint(0, WINDOW_WIDTH - 50), random.randint(0, WINDOW_HEIGHT - 50)]
            vel = [random.choice([-80, -60, -40, 40, 60, 80]), random.choice([-80, -60, -40, 40, 60, 80])]
            img = random.choice(enemy_images)
            enemies.append({'pos': pos, 'vel': vel, 'img': img})

        title_font = pygame.font.SysFont("comicsansms", 60)
        button_font = pygame.font.SysFont("comicsansms", 30)

        button_width, button_height = 150, 50
        spacing = 40
        total_width = button_width * 2 + spacing
        start_x = WINDOW_WIDTH // 2 - total_width // 2
        restart_x = start_x
        quit_x = start_x + button_width + spacing
        button_y = 400

        dt = 0
        clock = pygame.time.Clock()
        waiting = True
        while waiting:
            dt = clock.tick(60) / 1000.0
            self.screen.fill((30, 80, 30))  # dark green background

            # update and draw floating enemies
            for e in enemies:
                e['pos'][0] += e['vel'][0] * dt
                e['pos'][1] += e['vel'][1] * dt

                if e['pos'][0] < 0 or e['pos'][0] > WINDOW_WIDTH - 50:
                    e['vel'][0] *= -1
                if e['pos'][1] < 0 or e['pos'][1] > WINDOW_HEIGHT - 50:
                    e['vel'][1] *= -1

                self.screen.blit(e['img'], e['pos'])

            # draw Victory title
            title = title_font.render("Successfully Completed The Game!", True, (180, 255, 180))
            title_x = WINDOW_WIDTH // 2 - title.get_width() // 2
            title_y = button_y - title.get_height() - 40
            self.screen.blit(title, (title_x, title_y))

            # mouse info
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()

            # Restart button
            restart_color = (120, 255, 120)
            if restart_x < mouse[0] < restart_x + button_width and button_y < mouse[1] < button_y + button_height:
                restart_color = (50, 255, 50)
                if click[0] == 1:
                    self.reset()
                    waiting = False
            pygame.draw.rect(self.screen, restart_color, (restart_x, button_y, button_width, button_height),
                             border_radius=12)
            restart_text = button_font.render("Restart", True, (0, 0, 0))
            restart_rect = restart_text.get_rect(center=(restart_x + button_width // 2, button_y + button_height // 2))
            self.screen.blit(restart_text, restart_rect)

            # Quit button
            quit_color = (120, 255, 120)
            if quit_x < mouse[0] < quit_x + button_width and button_y < mouse[1] < button_y + button_height:
                quit_color = (50, 255, 50)
                if click[0] == 1:
                    pygame.quit()
                    exit()
            pygame.draw.rect(self.screen, quit_color, (quit_x, button_y, button_width, button_height), border_radius=12)
            quit_text = button_font.render("Quit", True, (0, 0, 0))
            quit_rect = quit_text.get_rect(center=(quit_x + button_width // 2, button_y + button_height // 2))
            self.screen.blit(quit_text, quit_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            pygame.display.update()

    def generate_rooms(self, max_rooms):
        rooms = {(0,0): Room((100,100,100), (0,0))}
        poz = [(0,0)]

        while len(rooms) < max_rooms and poz:
            cx, cy = random.choice(poz)
            directions = [(1,0),(-1,0),(0,1),(0,-1)]
            dx, dy = random.choice(directions)
            new_pos = (cx+dx, cy+dy)
            if new_pos not in rooms:
                color = (random.randint(50,200), random.randint(50,200), random.randint(50,200))
                rooms[new_pos] = Room(color, new_pos)
                poz.append(new_pos)
            if len(poz) > max_rooms:
                poz.pop(0)

        for room in rooms.values():
            room.update_doors(rooms)

        return rooms

    def draw_health(self):
        heart = pygame.image.load("images/heart.png").convert_alpha()
        s_heart = pygame.transform.scale(heart, (32,32))
        for i in range(self.player.health):
            self.screen.blit(s_heart, (20 + i * 40, 20))

    def draw_minimap(self, screen, offset_y=60):
        xs = [pos[0] for pos in self.rooms.keys()]
        ys = [pos[1] for pos in self.rooms.keys()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        cell_size = 15
        spacing = 20

        for (x, y), room in self.rooms.items():
            draw_x = 20 + (x - min_x) * spacing
            draw_y = 20 + (y - min_y) * spacing + offset_y
            color = (100, 100, 100) if not room.visited else (255, 255, 255)
            rect = pygame.Rect(draw_x, draw_y, cell_size, cell_size)
            pygame.draw.rect(screen, color, rect)

        cx, cy = self.current_room.pos
        draw_x = 20 + (cx - min_x) * spacing
        draw_y = 20 + (cy - min_y) * spacing + offset_y
        rect = pygame.Rect(draw_x, draw_y, cell_size, cell_size)
        pygame.draw.rect(screen, (0, 255, 0), rect)

    def run(self):
        self.start_screen()

        while self.running:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.all_sprites.update(dt)
            self.bullet_group.update(dt)
            self.current_room.sprites.update(dt)

            new_room, new_pos = self.current_room.check_doors(self.player, self.rooms)
            if new_room:
                self.current_room = new_room
                nx = max(0, min(WINDOW_WIDTH, new_pos[0]))
                ny = max(0, min(WINDOW_HEIGHT, new_pos[1]))
                self.player.rect.center = (nx, ny)

            for spr in list(self.current_room.sprites):
                if isinstance(spr, PowerUp) and self.player.rect.colliderect(spr.rect):
                    spr.apply(self.player)

            self.current_room.draw(self.screen)
            self.all_sprites.draw(self.screen)
            self.bullet_group.draw(self.screen)
            self.current_room.sprites.draw(self.screen)

            self.draw_minimap(self.screen, offset_y=60)
            self.draw_health()

            pygame.display.update()

            # check for game over
            if self.player.health <= 0:
                self.game_over_screen()

            # check if all enemies are defeated in all rooms
            all_enemies_defeated = all(
                not any(isinstance(s, Enemy) for s in room.sprites)
                for room in self.rooms.values()
            )
            if all_enemies_defeated:
                self.victory_screen()
                self.reset()

        pygame.quit()


if __name__ == "__main__":
    igra = Game()
    igra.run()
