from pathlib import Path
import pygame

FRAMERATE = 60
WIDTH, HEIGHT = 800, 400

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Runner")

# simple surfaces
# test_surface = pygame.Surface((100, 200))
# test_surface.fill("red")


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


# images
sky_surf = pygame.image.load("./graphics/sky.png").convert()
ground_surf = pygame.image.load("./graphics/ground.png").convert()
# do convert_alpha if the image is rectanglish
snail_surf = pygame.image.load("./graphics/snail/snail1.png").convert_alpha()
snail_x = 700
snail_height = 265
snail_vel = -8
snail_rect = snail_surf.get_rect(topleft=(snail_x, snail_height))

player_surf = pygame.image.load("./graphics/Player/player_walk_1.png").convert_alpha()
player_rect = player_surf.get_rect(midbottom=(100, 300))
player_gravity = 0

player_stand_image = pygame.image.load("./graphics/Player/player_stand.png").convert_alpha()
player_angle = 0
player_scale = 3
player_stand = pygame.transform.rotozoom(player_stand_image, player_angle, player_scale)
player_stand_rect = player_stand.get_rect(center=(WIDTH / 2, 300))

score = 0
hi_score = get_hi_score()
last_increment_score = 50

# fonts
font = pygame.font.Font("./font/Pixeltype.ttf", 30)
enter_text = font.render("press enter to start the game", False, "black")
hi_score_text = font.render(f"hi score: {hi_score}", False, "red")
hi_score_rect = hi_score_text.get_rect(topright=(WIDTH, 20))

# event timers
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

clock = pygame.time.Clock()
running = True
game_active = False

while running:
    clock.tick(FRAMERATE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            running = False
        # elif event.type == pygame.MOUSEMOTION  # if mouse is moved at all
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if player_rect.collidepoint(event.pos) and player_rect.bottom >= 300:
                player_gravity = -18.5

        # better approach then pygame.key
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if not game_active:
                    game_active = True
                    score = 0
            elif event.key == pygame.K_SPACE and player_rect.bottom >= 300:
                player_gravity = -18.5
        
        if game_active:
            if event.type == obstacle_timer:
                pass

    # screen.blit(test_surface, (0, 0))
    # backdrop
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
        player_angle += 0.5
        player_stand = pygame.transform.rotozoom(player_stand_image, player_angle, player_scale)
        player_stand = pygame.transform.rotate(player_stand, player_angle)
        player_stand_rect = player_stand.get_rect(center=(WIDTH / 2, 300))
        pygame.display.update()
        continue

    # draw module
    # pygame.draw.line(screen, "pink", (0, 0), pygame.mouse.get_pos(), 3)

    player_gravity += 1
    player_rect.y += player_gravity
    if player_rect.bottom > 300:
        player_rect.bottom = 300

    # characters
    snail_rect.x += snail_vel
    if snail_rect.x < -100:
        snail_rect.topleft = (WIDTH, snail_height)
    screen.blit(snail_surf, snail_rect)

    screen.blit(player_surf, player_rect)
    if player_rect.colliderect(snail_rect):
        snail_rect.x = 700
        snail_vel = -7
        game_active = False
        if round(score) > hi_score:
            set_hi_score(round(score))
        hi_score = get_hi_score()
        hi_score_text = font.render(f"hi score: {hi_score}", False, "red")
        hi_score_rect = hi_score_text.get_rect(topright=(WIDTH, 20))

    # pygame.mouse.get_pressed()  # returns a tuple of bools stating if the mouse is left, scroll, or right clicked
    # pygame.mouse.get_pos()  # alternate way to get mouse position

    # keyboard works similarly
    # keys = pygame.key.get_pressed()  # returns a tuple (akshually class) of all key states
    # if keys[pygame.K_SPACE]:
    #     print("jump")

    score += 0.1
    if score > last_increment_score:
        snail_vel -= 1
        last_increment_score += 50
    pygame.display.update()

pygame.quit()
