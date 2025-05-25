import pygame
import random
import math

# Initialize Pygame
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)

# --- Set up the display ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wheel of Fortune")

# --- Fonts ---
pygame.font.init()
font = pygame.font.SysFont('Press Start 2P', 24)  # Use a system font, fallback if not available.
small_font = pygame.font.SysFont('Press Start 2P', 16)

def draw_text(surface, text, x, y, color):
    """Draws text on a given surface."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)

def draw_small_text(surface, text, x, y, color):
    """Draws smaller text on a given surface."""
    text_surface = small_font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)

# --- Game Variables ---
phrases = [
    "JAVASCRIPT IS FUN",
    "WELCOME TO THE JUNGLE",
    "HAPPY CODING",
    "REACT IS AWESOME",
    "WINTER IS COMING",
    "THE QUICK BROWN FOX",
    "A JOURNEY OF A THOUSAND MILES",
    "TO BE OR NOT TO BE",
    "ALL THAT GLITTERS IS NOT GOLD",
    "EVERY CLOUD HAS A SILVER LINING"
]
phrase = ""
guessed_letters = set()
guesses = []
game_over = False
current_player = 1
num_players = 1
spin_value = 0
current_rotation = 0
total_rotation = 0
wheel_spinning = False
spin_time = 0
spin_time_total = 0
animation_start_time = 0
value_display_duration = 3000  # 3 seconds
display_start_time = 0
message_text = ""

# --- Wheel of Fortune variables ---
WHEEL_RADIUS = 200
WHEEL_CENTER_X = SCREEN_WIDTH // 4
WHEEL_CENTER_Y = SCREEN_HEIGHT // 2
NUM_SLICES = 8
SLICE_ANGLES = [i * 360 / NUM_SLICES for i in range(NUM_SLICES)]
SLICE_COLORS = ["#facc15", "#6ee7b7", "#3b82f6", "#d8b4fe", "#fb7185", "#f9a8d4", "#84cc16", "#a855f7"]  # Added more colors
SLICE_VALUES = [100, 200, 300, 400, 500, 600, 700, 800]
SPIN_DURATION = 5  # in seconds
FPS = 60

# --- Button Class ---
class Button:
    def __init__(self, x, y, width, height, color, text, text_color, action=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.text_color = text_color
        self.action = action
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        draw_text(surface, self.text, self.x + self.width // 2, self.y + self.height // 2, self.text_color)

    def is_over(self, pos):
        return self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_over(event.pos) and self.action:
                self.action()

# --- Functions ---
def select_phrase():
    global phrase, guessed_letters
    phrase = random.choice(phrases).upper()
    guessed_letters = set()
    display_phrase()

def display_phrase():
    display = ""
    for char in phrase:
        if char == " ":
            display += " "
        elif char in guessed_letters:
            display += char
        else:
            display += "_"
    return display

def check_guess(guess_input):
    global game_over, phrase, result_text, display_start_time, message_text
    if game_over:
        return

    guess = guess_input.upper()

    if not guess:
        message_text = "Please enter a guess."
        display_start_time = pygame.time.get_ticks()
        return

    if guess in guesses:
        message_text = "You already guessed that!"
        display_start_time = pygame.time.get_ticks()
        return

    guesses.append(guess)

    if len(guess) == 1:
        if guess in phrase:
            guessed_letters.add(guess)
            display_phrase_text = display_phrase()
            if "_" not in display_phrase_text:
                message_text = f"Congratulations! You guessed the phrase: {phrase}"
                game_over = True
                check_button.text = "Start New Game"
                spin_button.text = "Start New Game"
                display_start_time = pygame.time.get_ticks()
            else:
                message_text = "Correct guess!"
                display_start_time = pygame.time.get_ticks()
        else:
            message_text = "Incorrect guess!"
            display_start_time = pygame.time.get_ticks()
    else:
        if guess == phrase:
            message_text = f"Congratulations! You guessed the phrase: {phrase}"
            game_over = True
            check_button.text = "Start New Game"
            spin_button.text = "Start New Game"
            display_start_time = pygame.time.get_ticks()
        else:
            message_text = "Incorrect phrase guess!"
            display_start_time = pygame.time.get_ticks()

    guess_input = ""
    if game_over:
        check_button.action = reset_game
        spin_button.action = reset_game
    return guess_input

def draw_wheel():
    """Draws the Wheel of Fortune on the screen."""
    screen.blit(wheel_image, (WHEEL_CENTER_X - WHEEL_RADIUS, WHEEL_CENTER_Y - WHEEL_RADIUS))

def spin_wheel():
    """Starts the wheel spinning animation."""
    global wheel_spinning, spin_time, spin_time_total, spin_angle_start, animation_start_time
    if wheel_spinning:
        return
    wheel_spinning = True
    spin_time = 0
    spin_time_total = random.randint(2000, 5000)  # Random spin duration
    spin_angle_start = current_rotation
    animation_start_time = pygame.time.get_ticks()

def ease_out_cubic(t):
    """Easing function for smooth spin deceleration."""
    t -= 1
    return t * t * t + 1

def animate_spin():
    """Animates the wheel spinning."""
    global current_rotation, wheel_spinning, spin_time, total_rotation, spin_value, display_start_time
    if not wheel_spinning:
        return

    spin_time = pygame.time.get_ticks() - animation_start_time
    spin_progress = spin_time / spin_time_total

    if spin_progress >= 1:
        spin_progress = 1
        wheel_spinning = False
        calculate_spin_value()
        spin_time = 0
        spin_time_total = 0
        display_start_time = pygame.time.get_ticks()  # show the value
    easing = ease_out_cubic(spin_progress)
    current_rotation = spin_angle_start + easing * 720  # total rotation
    total_rotation = current_rotation

def calculate_spin_value():
    """Calculates the value of the slice the wheel landed on."""
    global spin_value
    num_slices = len(SLICE_VALUES)
    slice_angle = 360 / num_slices
    # Ensure rotation is positive
    final_rotation = total_rotation % 360
    # Find the slice index
    slice_index = int((360 - final_rotation) // slice_angle) % num_slices
    spin_value = SLICE_VALUES[slice_index]

def reset_game():
    """Resets the game to its initial state."""
    global phrase, guessed_letters, guesses, game_over, current_player, spin_value, current_rotation, total_rotation, wheel_spinning
    global check_button, spin_button, message_text
    phrase = ""
    guessed_letters = set()
    guesses = []
    game_over = False
    current_player = 1
    spin_value = 0
    current_rotation = 0
    total_rotation = 0
    wheel_spinning = False
    message_text = ""
    select_phrase()
    check_button.text = "Check Guess"
    spin_button.text = "Spin the Wheel"
    check_button.action = lambda: check_guess(guess_input)
    spin_button.action = spin_wheel

# --- Initialize Game ---
select_phrase()

# --- Create Buttons ---
guess_input = "" # Changed to a string
check_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50, GREEN, "Check Guess", WHITE, lambda: check_guess(guess_input))
spin_button = Button(WHEEL_CENTER_X - 75, WHEEL_CENTER_Y + WHEEL_RADIUS + 20, 150, 40, YELLOW, "Spin Wheel", BLACK, spin_wheel)
buttons = [check_button, spin_button]

# --- Load Wheel Image ---
# Load the image and scale it.  Make sure 'wheel.png' is in the same directory.
wheel_image = pygame.image.load('wheel.png')
wheel_image = pygame.transform.scale(wheel_image, (WHEEL_RADIUS * 2, WHEEL_RADIUS * 2))

# --- Main Game Loop ---
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLUE)
    draw_wheel()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for button in buttons:
            button.handle_event(event)
        if event.type == pygame.TEXTINPUT: # Handle text input
            guess_input += event.text

    # Draw the game elements
    display_phrase_text = display_phrase()
    draw_text(screen, "Phrase: " + display_phrase_text, SCREEN_WIDTH // 2, 50, WHITE)
    draw_text(screen, "Spin Value: " + str(spin_value), SCREEN_WIDTH // 2, 550, YELLOW)
    draw_small_text(screen, "Previous Guesses: " + ", ".join(guesses), SCREEN_WIDTH // 2, 580, WHITE)

    for button in buttons:
        button.draw(screen)

    # Draw the input box.  Use a rectangle and the guess_input string.
    input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 200, 200, 40)
    pygame.draw.rect(screen, WHITE, input_rect, 2)
    draw_text(screen, guess_input, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 180, WHITE)

    if message_text:
        draw_text(screen, message_text, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, RED)
        if pygame.time.get_ticks() - display_start_time > value_display_duration:
            message_text = ""

    if wheel_spinning:
        animate_spin()
        draw_wheel()  # Keep drawing the wheel during spin

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
