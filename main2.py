from pathlib import Path
from random import choice, randint
import pygame


FRAMERATE = 60
WIDTH, HEIGHT = 800, 400

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Runner")

sky_surf = pygame.image.load("./graphics/sky.png").convert()
ground_surf = pygame.image.load("./graphics/ground.png").convert()
player_stand_image = pygame.image.load(
    "./graphics/Player/player_stand.png"
).convert_alpha()
player_stand_rect = player_stand_image.get_rect(midbottom=(WIDTH / 2, 300))

bg_music = pygame.mixer.Sound("./audio/music.wav")
bg_music.set_volume(0.5)
bg_music.play(loops=-1)


def get_hi_score():
    try:
        file_path = Path.home() / ".pixelrunner.txt"
        with open(str(file_path), encoding="utf-8") as f:
            return int(f.read())
    except FileNotFoundError or ValueError:
        return 0
    except Exception as e:
        print("unknown error occured:", e)
        exit(1)


def set_hi_score(score):
    try:
        file_path = Path.home() / ".pixelrunner.txt"
        with open(str(file_path), "w", encoding="utf-8") as f:
            f.write(str(score))
    except Exception as e:
        print("unknown error occured:", e)
        exit(1)


score = 0
hi_score = get_hi_score()
last_increment_score = 50

font = pygame.font.Font("./font/Pixeltype.ttf", 30)
enter_text = font.render("press enter to start the game", False, "black")
hi_score_text = font.render(f"hi score: {hi_score}", False, "red")
hi_score_rect = hi_score_text.get_rect(topright=(WIDTH, 20))


class Player(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        player_walk1 = pygame.image.load(
            "./graphics/Player/player_walk_1.png"
        ).convert_alpha()
        player_walk2 = pygame.image.load(
            "./graphics/Player/player_walk_2.png"
        ).convert_alpha()
        self.frames = [player_walk1, player_walk2]
        self.frame_index = 0

        self.jump_image = pygame.image.load(
            "./graphics/Player/jump.png"
        ).convert_alpha()

        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(midbottom=(80, 300))

        self.gravity = 0

        self.jump_sound = pygame.mixer.Sound("./audio/jump.mp3")
        self.jump_sound.set_volume(0.5)

    def animate(self):
        if self.rect.bottom < 300:
            self.image = self.jump_image
        else:
            self.frame_index += 0.1
            if self.frame_index > len(self.frames):
                self.frame_index = 0

            self.image = self.frames[int(self.frame_index)]

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom > 300:
            self.rect.bottom = 300

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
            self.gravity = -20
            self.jump_sound.play()

    def update(self) -> None:
        self.player_input()
        self.apply_gravity()
        self.animate()


class Obstacle(pygame.sprite.Sprite):
    """
    Represents a snail or a fly obstacle.
    """

    def __init__(self, obstacle_type: str) -> None:
        super().__init__()

        if obstacle_type == "fly":
            fly1 = pygame.image.load("./graphics/Fly/Fly1.png").convert_alpha()
            fly2 = pygame.image.load("./graphics/Fly/Fly2.png").convert_alpha()

            self.frames = [fly1, fly2]
            y_pos = 210

        elif obstacle_type == "snail":
            snail1 = pygame.image.load("./graphics/snail/snail1.png").convert_alpha()
            snail2 = pygame.image.load("./graphics/snail/snail2.png").convert_alpha()

            self.frames = [snail1, snail2]
            y_pos = 300

        else:
            raise Exception(f"unknown obstacle type {obstacle_type}")

        self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(midbottom=(randint(900, 1100), y_pos))

        self.speed = -7

    def animate(self):
        self.frame_index += 0.1
        if self.frame_index > len(self.frames):
            self.frame_index = 0

        self.image = self.frames[int(self.frame_index)]

    def destroy(self):
        if self.rect.x < -100:
            self.kill()

    def update(self) -> None:
        self.animate()
        self.rect.x += self.speed
        global last_increment_score
        if score > last_increment_score:
            self.speed -= 1
            last_increment_score += 50
        self.destroy()


def collision(player_group, obstacle_group):
    if pygame.sprite.spritecollide(player_group.sprite, obstacle_group, False):
        obstacle_group.empty()
        return True

    return False


player = pygame.sprite.GroupSingle()
player.add(Player())

obstacles = pygame.sprite.Group()

obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)


running = True
clock = pygame.time.Clock()
game_active = False

while running:
    clock.tick(FRAMERATE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_q
        ):
            running = False

        # elif event.type == pygame.MOUSEMOTION  # if mouse is moved at all
        # elif event.type == pygame.MOUSEBUTTONDOWN:
        #     if player_rect.collidepoint(event.pos) and player_rect.bottom >= 300:
        #         player_gravity = -18.5

        # better approach than pygame.key
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if not game_active:
                    game_active = True
                    score = 0
            # elif event.key == pygame.K_SPACE:
            #     player_gravity = -18.5

        if game_active:
            if event.type == obstacle_timer:
                obstacles.add(Obstacle(choice(["fly", "snail", "snail", "snail"])))

    screen.blit(sky_surf, (0, 0))
    screen.blit(ground_surf, (0, 300))
    screen.blit(hi_score_text, hi_score_rect)

    # info
    score_text = font.render(f"score: {round(score)}", False, "red")
    score_rect = score_text.get_rect(topright=(WIDTH, 0))
    screen.blit(score_text, score_rect)
    if not game_active:
        screen.blit(enter_text, (300, 50))
        screen.blit(player_stand_image, player_stand_rect)
        pygame.display.update()
        continue

    player.draw(screen)
    player.update()

    obstacles.draw(screen)
    obstacles.update()

    game_active = not collision(player, obstacles)
    score += 0.1

    pygame.display.update()
