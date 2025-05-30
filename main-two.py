import pygame
import random
import time
import os
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# --- Constants ---
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
PURPLE = (128, 0, 128)
DARK_PURPLE = (85, 26, 139)

# Screen dimensions
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 1000
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

GAME_DISPLAY_WIDTH = 800
GAME_DISPLAY_HEIGHT = 600
GAME_DISPLAY_SIZE = (GAME_DISPLAY_WIDTH, GAME_DISPLAY_HEIGHT)
# GAME_DISPLAY_X = (SCREEN_WIDTH - GAME_DISPLAY_WIDTH) // 2
GAME_DISPLAY_X = 100
GAME_DISPLAY_Y = (SCREEN_HEIGHT - GAME_DISPLAY_HEIGHT) // 2

WORD_DISPLAY_WIDTH = 800
WORD_DISPLAY_HEIGHT = 200
WORD_DISPLAY_SIZE = (WORD_DISPLAY_WIDTH, WORD_DISPLAY_HEIGHT)
WORD_DISPLAY_X = SCREEN_WIDTH // 2 + 100
WORD_DISPLAY_Y = (SCREEN_HEIGHT - WORD_DISPLAY_HEIGHT) // 2
# Game display

# Font
FONT_TYPE = 'GEORGIA'
FONT_SMALL = pygame.font.SysFont(FONT_TYPE, 24)
FONT_MEDIUM = pygame.font.SysFont(FONT_TYPE, 36)
FONT_LARGE = pygame.font.SysFont(FONT_TYPE, 48)
FONT_XLARGE = pygame.font.SysFont(FONT_TYPE, 60) # For the puzzle reveal
FONT_XXLARGE = pygame.font.SysFont(FONT_TYPE, 72) # For the title
HIGHLIGHT_COLOR = (255, 215, 0)  # Gold/yellow highlight
# Load font

#Music
pygame.mixer.music.load("Assets/Superfly Full Mix.mp3")  # Replace with your music file
pygame.mixer.music.set_volume(0.5)  # Set volume (0.0 to 1.0)

# Game values
VOWELS = ('A', 'E', 'I', 'O', 'U')
CONSONANTS = ('B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Y', 'Z')
WHEEL_VALUES = [
    2500, 600, 700, 650, 800, 500, 600, 550, 500, 600,
    650, 700, 800, 'BANKRUPT', 900, 500, 600, 700, 800, 500,
    600, 650, 700, 1000, 'BANKRUPT', 'LOSE A TURN'
] # More visually appealing order



# --- Helper Functions ---

def load_sound(filename):
    """Loads a sound file and handles errors."""
    try:
        sound = pygame.mixer.Sound(filename)
        return sound
    except pygame.error as e:
        print(f"Error loading sound file {filename}: {e}")
        return None


# --- Load Sound Effects ---
wheel_sound = load_sound("Assets/Wheel-Sound.wav")
bankrupt_sound = load_sound("Assets/awww-01.wav")
lose_turn_sound = load_sound("Assets/awww-01.wav")
win_sound = load_sound("Assets/Crowd_Cheer.wav")
buy_vowel_sound = load_sound("Assets/bonus.wav")
wrong_guess_sound = load_sound("Assets/wrong_guess.mp3")
button_click_sound = load_sound("Assets/button_click.wav")
button_select_sound = load_sound("Assets/button_select.flac")

last_hovered_button_id = None



def display_message(surface, message, font, color, position, center=True):
    """Displays a text message on the screen."""
    text = font.render(message, True, color)
    rect = text.get_rect()
    if center:
        rect.center = position
    else:
        rect.topleft = position
    surface.blit(text, rect)
    
def draw_button(surface, rect, text, font, text_color, highlight_color, mouse_pos, button_id=None):
    """Draws a button and highlights it if hovered. Plays sound on hover."""
    global last_hovered_button_id
    is_hovered = rect.collidepoint(mouse_pos)
    if is_hovered:
        text_color = PURPLE
        pygame.draw.rect(surface, highlight_color, rect)
        if button_id is not None and last_hovered_button_id != button_id:
            if button_click_sound:
                button_click_sound.play()
        last_hovered_button_id = button_id
    else:
        pygame.draw.rect(surface, WHITE, rect, 2)
        if button_id is not None and last_hovered_button_id == button_id:
            last_hovered_button_id = None
    display_message(surface, text, font, text_color, rect.center)
    
    
def draw_info_section(surface, x, y, w, h, player_name, player_score, spin_value=None, font=FONT_MEDIUM, category=None):
    """Draws the info section with background and game info."""
    bg_color = (30, 30, 60)
    border_radius = 20
    pygame.draw.rect(surface, bg_color, (x, y, w, h), border_radius=border_radius)
    pygame.draw.rect(surface, WHITE, (x, y, w, h), 3, border_radius=border_radius)
    info_y = y + 20
    if category is None:
        category = "No Category Selected"
    display_message(surface,"Category: " + category, FONT_MEDIUM, WHITE, (x + 30,  info_y), center=False)
    info_y +=45
    display_message(surface, f"Player Turn: {player_name}", font, YELLOW, (x + 30, info_y), center=False)
    info_y += 45
    if spin_value is not None:
        display_message(surface, f"Spin Value: {spin_value}", font, WHITE, (x + 30, info_y), center=False)
        info_y += 45
    display_message(surface, f"Score: ${player_score}", font, GREEN, (x + 30, info_y), center=False)



def get_text_input(surface, prompt, font, text_color, bg_color, input_rect_center, overlap=False, puzzle='', revealed='', spin_value=None, category='', current_player_name=None):
    """Gets text input from the user."""
    input_text = ""
    active = True

    # Dynamically set input box width based on puzzle width
    if "consonant" in prompt.lower() or "vowel" in prompt.lower():
        input_box_width = 120  # Small box for single letter
    else:
        if puzzle:
            puzzle_surface = font.render(puzzle, True, text_color)
            input_box_width = puzzle_surface.get_width() + 40  # Add some padding
            input_box_width = max(200, min(input_box_width, SCREEN_WIDTH - 100))  # Clamp to reasonable range
        else:
            input_box_width = 200

    input_rect = pygame.Rect(0, 0, input_box_width, 50)
    input_rect.center = input_rect_center  # Center the input rect

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        surface.fill(bg_color)
        if overlap and len(puzzle) > 0:
            display_board(surface, puzzle, revealed, font, text_color, 40, 50, WORD_DISPLAY_X, SCREEN_WIDTH)
            display_message(surface, f'WHEEL OF FORTUNE', FONT_XXLARGE, text_color, (SCREEN_WIDTH // 2, 100))
            # Info section (left)
            info_x = GAME_DISPLAY_X
            info_y = 135
            info_w = 465
            info_h = GAME_DISPLAY_HEIGHT - 200
            draw_info_section(surface, info_x, info_y, info_w, info_h,
                              current_player_name, 0, spin_value, font=FONT_MEDIUM, category=category)
        display_message(surface, prompt, font, text_color, (input_rect.centerx, input_rect.y - 30))
        pygame.draw.rect(surface, text_color, input_rect, 2)
        text_surface = font.render(input_text, True, text_color)
        text_rect = text_surface.get_rect(center=input_rect.center)
        surface.blit(text_surface, text_rect)
        pygame.display.flip()
    return input_text


FONT_WHEEL = pygame.font.SysFont(FONT_TYPE, 36, bold=True)
FONT_WHEEL_SMALL = pygame.font.SysFont(FONT_TYPE, 22, bold=True)

def draw_wheel(surface, center, radius, angle, values, spin_colors, text_color):
    """Draws the Wheel of Fortune with grouped value colors and special slice styling."""
    num_slices = len(values)
    slice_angle = 360 / num_slices

    # Assign a unique color to each unique value (except BANKRUPT and LOSE A TURN)
    unique_values = []
    for v in values:
        if v not in unique_values and v not in ("BANKRUPT", "LOSE A TURN"):
            unique_values.append(v)
    # Pick as many distinct colors as needed for unique values
    palette = [
        (255, 99, 71), (60, 179, 113), (30, 144, 255), (255, 215, 0), (255, 140, 0),
        (186, 85, 211), (0, 206, 209), (255, 105, 180), (154, 205, 50), (255, 69, 0),
        (0, 191, 255), (255, 20, 147), (255, 182, 193), (0, 255, 127), (255, 165, 0),
        (138, 43, 226), (0, 250, 154), (255, 0, 255), (255, 228, 181), (0, 128, 128),
        (255, 222, 173), (255, 0, 0), (0, 255, 255), (255, 255, 0)
    ]
    value_color_map = {}
    for idx, v in enumerate(unique_values):
        value_color_map[v] = palette[idx % len(palette)]

    # Draw each slice as a filled sector
    for i in range(num_slices):
        value = values[i]
        if value == "BANKRUPT":
            color = BLACK
        elif value == "LOSE A TURN":
            color = WHITE
        else:
            color = value_color_map[value]

        start_angle = i * slice_angle + angle
        end_angle = (i + 1) * slice_angle + angle

        # Points for the sector (pie slice)
        points = [center]
        for t in range(0, 16):
            interp_angle = start_angle + (end_angle - start_angle) * t / 15
            x = center[0] + radius * math.cos(math.radians(interp_angle))
            y = center[1] + radius * math.sin(math.radians(interp_angle))
            points.append((x, y))
        pygame.draw.polygon(surface, color, points)

    # Draw a hub in the center
    pygame.draw.circle(surface, (40, 40, 40), center, int(radius * 0.25))

    # Draw slice borders
    for i in range(num_slices):
        border_angle = i * slice_angle + angle
        x = center[0] + radius * math.cos(math.radians(border_angle))
        y = center[1] + radius * math.sin(math.radians(border_angle))
        pygame.draw.line(surface, (0, 0, 0), center, (x, y), 4)

    # Draw text for each slice
    for i in range(num_slices):
        value = str(values[i])
        start_angle = i * slice_angle + angle
        end_angle = (i + 1) * slice_angle + angle
        text_angle = (start_angle + end_angle) / 2
        text_radius = radius * 0.72
        x = center[0] + text_radius * math.cos(math.radians(text_angle))
        y = center[1] + text_radius * math.sin(math.radians(text_angle))

        if value == "BANKRUPT":
            txt_color = WHITE
            font = FONT_WHEEL_SMALL
            text_surface = font.render(value, True, txt_color)
            rotated_text = pygame.transform.rotate(text_surface, -text_angle)
            text_rect = rotated_text.get_rect(center=(int(x), int(y)))
            surface.blit(rotated_text, text_rect)
        elif value == "LOSE A TURN":
            txt_color = BLACK
            font = FONT_WHEEL_SMALL
            text_surface = font.render(value, True, txt_color)
            rotated_text = pygame.transform.rotate(text_surface, -text_angle)
            text_rect = rotated_text.get_rect(center=(int(x), int(y)))
            surface.blit(rotated_text, text_rect)
        else:
            txt_color = BLACK
            font = FONT_WHEEL
            text_surface = font.render(value, True, txt_color)
            rotated_text = pygame.transform.rotate(text_surface, -text_angle)
            text_rect = rotated_text.get_rect(center=(int(x), int(y)))
            surface.blit(rotated_text, text_rect)


def display_board(surface, puzzle, revealed, font, text_color, rect_width, rect_height, starting_x, screen_width):
    """Displays the puzzle board to the right of the wheel, wrapping as needed, never splitting words."""
    margin = 40  # Right margin
    available_width = screen_width - starting_x - margin
    max_letters_per_line = max((available_width) // (rect_width + 10), 1)

    # Split puzzle into words, keep track of their indices
    words = []
    idx = 0
    while idx < len(puzzle):
        if puzzle[idx] == ' ':
            words.append([(idx, ' ')])
            idx += 1
        else:
            start = idx
            while idx < len(puzzle) and puzzle[idx] != ' ':
                idx += 1
            word = [(i, puzzle[i]) for i in range(start, idx)]
            words.append(word)

    lines = []
    current_line = []
    current_length = 0
    for word in words:
        word_length = len(word)
        # +1 for space if not first word and not a space itself
        extra_space = 1 if current_line and word[0][1] != ' ' else 0
        if current_length + word_length + extra_space > max_letters_per_line:
            if current_line:
                lines.append(current_line)
            current_line = []
            current_length = 0
            # If the word itself is longer than the line, just add it (will overflow)
        if current_line and word[0][1] != ' ':
            current_line.append((-1, ' '))  # Add a space between words
            current_length += 1
        current_line.extend(word)
        current_length += word_length
    if current_line:
        lines.append(current_line)

    total_height = len(lines) * (rect_height + 20)
    start_y = SCREEN_HEIGHT // 2 - total_height // 2

    for line_num, line in enumerate(lines):
        line_length = len(line)
        board_width = line_length * rect_width + (line_length - 1) * 10  # Space between letters
        start_x = starting_x
        y = start_y + line_num * (rect_height + 20)
        for j, (i, char) in enumerate(line):
            x = start_x + j * (rect_width + 10)
            rect = pygame.Rect(x, y, rect_width, rect_height)
            pygame.draw.rect(surface, WHITE, rect, 2)
            if char.isalpha():
                if i != -1 and revealed[i]:
                    display_message(surface, char.upper(), font, text_color, rect.center, center=True)
                elif i != -1:
                    pygame.draw.rect(surface, GRAY, rect)
            # Optionally, you can skip drawing anything for spaces/punctuation
                    

def choose_category(surface, categories, font, text_color, bg_color):
    """Lets the player choose a category for the puzzle."""
    global last_hovered_button_id
    num_columns = 3
    col_width = SCREEN_WIDTH // num_columns
    row_height = 50
    padding_x = 40
    padding_y = 10

    while True:
        surface.fill(bg_color)
        display_message(surface, "Choose a Category:", font, text_color, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6))

        mouse_pos = pygame.mouse.get_pos()
        HIGHLIGHT_COLOR = (255, 215, 0)  # Gold/yellow highlight

        hovered_category_id = None

        for idx, category in enumerate(categories):
            col = idx % num_columns
            row = idx // num_columns
            x = col * col_width + padding_x
            y = SCREEN_HEIGHT // 4 + row * (row_height + padding_y)
            rect = pygame.Rect(x, y, col_width - 2 * padding_x, row_height)
            category_id = f"category_{idx}"
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, HIGHLIGHT_COLOR, rect)
                display_message(surface, category, font, PURPLE, rect.center, center=True)
                hovered_category_id = category_id
            else:
                pygame.draw.rect(surface, WHITE, rect, 2)
                display_message(surface, category, font, text_color, rect.center, center=True)

        # Play sound only when hover state changes
        if hovered_category_id != last_hovered_button_id and hovered_category_id is not None:
            if button_click_sound:
                button_click_sound.play()
        last_hovered_button_id = hovered_category_id

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for idx, category in enumerate(categories):
                    col = idx % num_columns
                    row = idx // num_columns
                    x = col * col_width + padding_x
                    y = SCREEN_HEIGHT // 4 + row * (row_height + padding_y)
                    rect = pygame.Rect(x, y, col_width - 2 * padding_x, row_height)
                    if rect.collidepoint(mouse_pos):
                        button_select_sound.play()  # Play sound on selection
                        return category

def reveal_letters(puzzle, revealed, guess):
    """Reveals the positions of a guessed letter in the puzzle."""
    positions = [i for i, letter in enumerate(puzzle) if letter.upper() == guess.upper()]
    for pos in positions:
        revealed[pos] = True
    return len(positions) # Return the number of letters revealed

def generate_puzzle(category, puzzles):
    """Selects a random puzzle from the chosen category."""
    return random.choice(puzzles[category]).upper()

def create_revealed_array(puzzle):
    """Creates a boolean array indicating which letters in the puzzle have been revealed."""
    return [False for _ in puzzle]

def calculate_winnings(spin_value, num_revealed):
    """Calculates the winnings for a correct letter guess."""
    if isinstance(spin_value, int):
        return spin_value * num_revealed
    return 0  # Return 0 for BANKRUPT or LOSE A TURN

def display_player_info(surface, player, font, color, position):
    """Displays player information (name and score)."""
    display_message(surface, f"{player['name']}: ${player['score']}", font, color, position, center=False)

def display_current_player(surface, player_name, font, color, position):
    """Displays the current player's name."""
    display_message(surface, f"Current Player: {player_name}", font, color, position, center=False)

def switch_player(current_player_index, players):
    """Switches to the next player."""
    return (current_player_index + 1) % len(players)

def spin_wheel(surface, center, radius, values, angle, spin_duration, spin_color, text_color):
    """Simulates the spinning of the wheel."""
    start_time = time.time()
    current_angle = angle

    # Play the wheel sound as the wheel spins
    if wheel_sound:
        wheel_sound.play(-1)  # Loop the sound

    while time.time() - start_time < spin_duration:
        for event in pygame.event.get():  # Handle events during spin
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        time_elapsed = time.time() - start_time
        #ease out
        delta_angle = (time_elapsed / spin_duration) * 720 + (1 - (time_elapsed / spin_duration)) * 1440
        current_angle += delta_angle
        surface.fill(DARK_PURPLE)  # Clear the screen
        draw_wheel(surface, center, radius, current_angle, values, spin_color, text_color)
        pygame.display.flip()

    # Stop the wheel sound after spinning
    if wheel_sound:
        wheel_sound.stop()

    return current_angle % 360  # Return the final angle

def get_wheel_value(angle, values):
    """Gets the value of the wheel at the given angle."""
    num_slices = len(values)
    slice_angle = 360 / num_slices
    # Normalize angle to be within 0-360
    normalized_angle = angle % 360
    slice_index = int(normalized_angle // slice_angle)
    return values[slice_index]

def handle_spin_result(surface, player, spin_value, puzzle, revealed, font, text_color, players, current_player_index, wheel_sound, bankrupt_sound, lose_turn_sound, category='', guessed_letters=None):
    """Handles the result of a wheel spin."""
    if guessed_letters is None:
        guessed_letters = set()
    if spin_value == "BANKRUPT":
        if bankrupt_sound:
            bankrupt_sound.play()
        player['score'] = 0  # Set current player's round score to 0
        surface.fill(BLACK)  # Draw black background
        display_message(surface, "BANKRUPT!", font, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        time.sleep(2)
        return 'BANKRUPT', current_player_index
    elif spin_value == "LOSE A TURN":
        if lose_turn_sound:
            lose_turn_sound.play()
        # Draw black background and red text for "Lose a turn"
        surface.fill(BLACK)
        display_message(surface, "LOSE A TURN", font, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        time.sleep(2)
        return 'LOSE A TURN', current_player_index
    else:
        if wheel_sound:
            wheel_sound.play()
            display_message(surface, f"{spin_value}!", font, GREEN, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            time.sleep(5)
        while True:
            guess = get_text_input(
                surface,
                f"Guess a consonant:",
                font,
                text_color,
                DARK_PURPLE,
                (GAME_DISPLAY_X + 100, SCREEN_HEIGHT // 2 + 200),
                overlap=True,
                puzzle=puzzle,
                revealed=revealed,
                spin_value=spin_value,
                category=category,
                current_player_name=player['name']
            )
            guess = guess.upper()
            if guess in guessed_letters or (guess in [puzzle[i].upper() for i, r in enumerate(revealed) if r]):
                display_message(surface, "Letter already guessed. Pick another.", font, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200))
                pygame.display.flip()
                time.sleep(2)
                continue
            if guess in CONSONANTS:
                guessed_letters.add(guess)
                num_revealed = reveal_letters(puzzle, revealed, guess)
                if num_revealed > 0:
                    winnings = calculate_winnings(spin_value, num_revealed)
                    player['score'] += winnings
                    display_message(surface, f"There are {num_revealed} {guess}'s.  You win ${winnings}!", font, GREEN, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
                    pygame.display.flip()
                    time.sleep(3)
                    return 'CORRECT', current_player_index
                else:
                    display_message(surface, "Sorry, there are no " + guess + "'s.", font, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
                    pygame.display.flip()
                    time.sleep(2)
                    return 'INCORRECT', current_player_index
            else:
                display_message(surface, "Invalid guess.  Must be a consonant.", font, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
                pygame.display.flip()
                time.sleep(2)
                return 'INVALID', current_player_index # added return

def handle_buy_vowel(surface, player, puzzle, revealed, font, text_color, bg_color, buy_vowel_sound, guessed_letters=None):
    """Handles the buying of a vowel."""
    if guessed_letters is None:
        guessed_letters = set()
    if player['score'] < 250:
        display_message(surface, "You don't have enough money to buy a vowel.", font, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        time.sleep(2)
        return False  # Indicate failure
    else:
        if buy_vowel_sound:
            buy_vowel_sound.play()
        player['score'] -= 250
        display_board(surface, puzzle, revealed, font, text_color, 40, 50, WORD_DISPLAY_X, SCREEN_WIDTH) #show the board
        while True:
            guess = get_text_input(
                surface,
                "Guess a vowel:",
                font,
                text_color,
                bg_color,
                (GAME_DISPLAY_X + 100, SCREEN_HEIGHT // 2 + 100),
                overlap=True,
                puzzle=puzzle,
                revealed=revealed,
                current_player_name=player['name']
            )
            guess = guess.upper()
            if guess in guessed_letters or (guess in [puzzle[i].upper() for i, r in enumerate(revealed) if r]):
                display_message(surface, "Letter already guessed. Pick another.", font, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200))
                wrong_guess_sound.play()
                pygame.display.flip()
                time.sleep(2)
                continue
            if guess in VOWELS:
                guessed_letters.add(guess)
                num_revealed = reveal_letters(puzzle, revealed, guess)
                if num_revealed > 0:
                    display_message(surface, f"There are {num_revealed} {guess}'s.", font, GREEN, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
                    pygame.display.flip()
                    time.sleep(2)
                    return True # Indicate success
                else:
                    display_message(surface, "Sorry, there are no " + guess + "'s.", font, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
                    wrong_guess_sound.play()
                    pygame.display.flip()
                    time.sleep(2)
                    return False
            else:
                display_message(surface, "Invalid guess.  Must be a vowel.", font, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
                wrong_guess_sound.play()
                pygame.display.flip()
                time.sleep(2)
                return False

def handle_solve_puzzle(surface, player, puzzle, revealed, font, text_color, bg_color):
    """Handles a player's attempt to solve the puzzle."""

    guess = get_text_input(surface, "Enter your solution:", font, text_color, bg_color, (SCREEN_WIDTH//2, SCREEN_HEIGHT // 2 + 300), overlap=True, puzzle=puzzle, revealed=revealed)
    if guess.upper() == puzzle.upper():
        if win_sound:
            win_sound.play()
        for i in range(len(puzzle)): #reveal all letters
            revealed[i] = True
        display_board(surface, puzzle, revealed, font, text_color, 40, 50, WORD_DISPLAY_X, SCREEN_WIDTH) #show the board
        display_message(surface, "YOU SOLVED THE PUZZLE!", FONT_XLARGE, GREEN, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        pygame.display.flip()
        time.sleep(5)
        return True
    else:
        display_message(surface, "That is not the correct solution.", font, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        wrong_guess_sound.play()
        pygame.display.flip()
        time.sleep(2)
        return False

def display_round_winner(surface, player, font, color):
    """Displays the winner of the round"""
    display_message(surface, f"{player['name']} wins the round with ${player['score']}!", font, color, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200))

def reset_round(players):
    """Resets the players' scores for a new round."""
    for player in players:
        player['score'] = 0

def has_unrevealed_vowels(puzzle, revealed):
    """Returns True if there are unrevealed vowels in the puzzle."""
    for i, char in enumerate(puzzle):
        if char.upper() in VOWELS and not revealed[i]:
            return True
    return False

def has_unrevealed_consonants(puzzle, revealed):
    """Returns True if there are unrevealed consonants in the puzzle."""
    for i, char in enumerate(puzzle):
        if char.upper() in CONSONANTS and not revealed[i]:
            return True
    return False

def show_intro_screen(screen, spin_colors, text_color):
    """Displays an intro screen with a spinning wheel prop."""
    angle = 0
    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                # Start the game when a key is pressed or mouse button is clicked
                win_sound.play()
                running = False

        screen.fill(DARK_PURPLE)
        display_message(screen, "WHEEL OF FORTUNE", FONT_XXLARGE, text_color, (SCREEN_WIDTH // 2, 180))
        display_message(screen, "Click or Press Any Key to Start", FONT_LARGE, YELLOW, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200))
        # Draw the spinning wheel prop in the center
        draw_wheel(screen, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20), 250, angle, WHEEL_VALUES, spin_colors, text_color)
        angle = (angle + 3) % 360  # Spin speed
        pygame.display.flip()
        clock.tick(60)  # 60 FPS



def main():
    """Main game function."""
    # --- Initialization ---
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Wheel of Fortune")


    # --- Game Data ---
    categories = ["Food & Drink", "Movies", "Places", "Music", "Science", "Literature", "Cartoons", "Wine", "US States", "US Presidents", "Poems", "Sports", "Video Games", "Famous People", "TV Shows", "Animals", "Fruits","Vegetables", "Countries", "Famous Landmarks", "Famous Sayings", "Before and After", "Things people say", "Things around the house", "2000's Hits Songs", "90's TV Shows"]
    puzzles = {
        "Food & Drink": ["Pizza", "Hamburger", "Sushi", "Chocolate Cake", "Coffee", "Spaghetti", "Ice Cream", "Tacos", "Salad", "Pasta", "Sandwich", "Cereal", "Donut", "Steak", "Fried Chicken", "Watermelon", "Cheeseburger", "Milkshake", "Pancakes", "French Fries"],
        "Movies": ["Star Wars", "The Matrix", "Pulp Fiction", "The Dark Knight", "Avatar", "Jurassic Park", "Frozen", "Inception", "Titanic", "The Godfather", "Harry Potter", "The Lion King", "The Avengers", "Finding Nemo", "Toy Story"],
        "Places": ["Paris", "New York", "Tokyo", "London", "Rome", "Barcelona", "Berlin", "Dubai", "Amsterdam", "Rio de Janeiro", "Los Angeles", "Beijing", "New Delhi", "Moscow", "Sydney", "Singapore", "Bangkok", "Istanbul", "Cairo", "Cape Town", "Buenos Aires", "Seoul", "Hong Kong", "Toronto", "Mexico City"],
        "Music": ["Jazz", "Rock", "Classical", "Hip Hop", "Country", "Pop", "Reggae", "Blues", "Electronic", "Folk", "Metal", "R&B", "Disco", "Salsa", "Gospel", "Opera", "K Pop", "Indie", "Punk", "Ska", "Techno", "House", "Trance", "Dubstep", "Ambient", "Bluegrass", "Swing", "Bossa Nova"],
        "Science": ["Gravity", "Relativity", "Photosynthesis", "Black Hole", "DNA", "Atom", "Molecule", "Evolution", "Quantum Mechanics", "Thermodynamics", "Electromagnetism", "Cell Biology", "Genetics", "Astrophysics", "Chemistry"],
        "Literature": ["Hamlet", "Pride and Prejudice", "The Great Gatsby", "To Kill a Mockingbird", "The Catcher in the Rye", "The Odyssey", "War and Peace", "Moby", "Great Expectations", "The Brothers Karamazov", "Crime and Punishment", "The Picture of Dorian Gray", "Brave New World", "The Grapes of Wrath", "The Hobbit"],
        "Cartoons": ["SpongeBob SquarePants", "The Simpsons", "Looney Tunes", "Tom and Jerry", "Scooby Doo", "Avatar The Last Airbender", "Teen Titans", "Adventure Time", "Gravity Falls", "Futurama", "Rick and Morty", "Johnny Bravo", "The Flintstones", "The Jetsons", "DuckTales", "Squidward", "Popeye", "Dora the Explorer", "Bluey", "Peppa Pig", "Little Einsteins", "Arthur", "Hey Arnold!", "The Magic School Bus", "The Fairly OddParents", "Kim Possible", "Avatar: The Legend of Korra", "The Amazing World of Gumball", "Steven Universe"],
        "Wine":["Cabernet Sauvignon", "Chardonnay", "Merlot", "Pinot Noir", "Sauvignon Blanc", "Syrah", "Zinfandel", "Riesling", "Malbec", "Tempranillo", "Grenache", "Shiraz", "Moscato", "Prosecco", "Champagne"],
        "US States": ["California", "Texas", "Florida", "New York", "Illinois", "Pennsylvania", "Ohio", "Georgia", "North Carolina", "Michigan", "New Jersey", "Virginia", "Washington", "Arizona", "Massachusetts"],
        "US Presidents": ["George Washington", "Thomas Jefferson", "Abraham Lincoln", "Theodore Roosevelt", "Franklin D. Roosevelt", "John F. Kennedy", "Richard Nixon", "Ronald Reagan", "Bill Clinton", "Barack Obama", "Donald Trump", "Joe Biden", "Andrew Jackson", "James Madison", "James Monroe", "John Adams", "John Quincy Adams", "Martin Van Buren", "Ulysses S. Grant", "Woodrow Wilson", "Harry S. Truman", "Lyndon B. Johnson", "Gerald Ford", "Jimmy Carter", "George H.W. Bush", "George W. Bush", "Calvin Coolidge", "Warren G. Harding", "Herbert Hoover", "Chester A. Arthur", "Benjamin Harrison", "William Howard Taft", "Millard Fillmore", "James Buchanan", "Andrew Johnson", "Martin Van Buren"],
        "Poems": ["The Road Not Taken", "Stopping by Woods on a Snowy Evening", "I Wandered Lonely as a Cloud", "Ode to a Nightingale", "The Raven", "Sonnet 18", "Do Not Go Gentle into That Good Night", "Invictus", "The Waste Land", "Daffodils", "The Love Song of J Alfred Prufrock", "Still I Rise", "The Charge of the Light Brigade", "The Tyger", "Ozymandias", "The Second Coming", "Annabel Lee", "A Dream Within a Dream", "The Bells", "The Ballad of Reading Gaol", "The Song of Hiawatha", "Kubla Khan", "The Jabberwocky", "The Lady of Shalott", "The Prelude", "The Canterbury Tales"],
        "Famous People": ["Albert Einstein", "Marie Curie", "Isaac Newton", "Leonardo da Vinci", "Galileo Galilei", "Charles Darwin", "Nikola Tesla", "Thomas Edison", "Stephen Hawking", "Ada Lovelace", "Jane Goodall", "Mahatma Gandhi", "Nelson Mandela", "Martin Luther King Jr.", "Winston Churchill"],
        "Sports": ["Soccer", "Basketball", "Baseball", "Football", "Tennis", "Golf", "Hockey", "Cricket", "Rugby", "Volleyball", "Swimming", "Boxing", "Cycling", "Gymnastics", "Table Tennis"],
        "Video Games": ["Super Mario Bros", "The Legend of Zelda", "Minecraft", "Fortnite", "Call of Duty", "Overwatch", "World of Warcraft", "The Elder Scrolls V Skyrim", "Final Fantasy VII", "Pokémon Red and Blue", "Tetris", "Pacman", "Street Fighter II", "The Legend of Zelda: Ocarina of Time", "Half Life", "Portal", "Dark Souls", "The Witcher", "Red Dead Redemption", "Grand Theft Auto V", "Apex Legends", "Among Us", "Animal Crossing New Horizons", "Hades", "Stardew Valley", "Celeste", "Hollow Knight", "Undertale"],
        "TV Shows": ["Friends", "Breaking Bad", "Game of Thrones", "The Office", "Stranger Things", "The Simpsons", "The Big Bang Theory", "The Walking Dead", "Sherlock", "Black Mirror", "The Crown", "Westworld", "Better Call Saul", "The Mandalorian", "The Sopranos"],
        "Animals": ["Elephant", "Dolphin", "Giraffe", "Kangaroo", "Penguin", "Lion", "Tiger", "Bear", "Zebra", "Panda", "Koala", "Cheetah", "Hippopotamus", "Rhinoceros", "Alligator", "Crocodile", "Octopus", "Jellyfish", "Starfish", "Seahorse", "Crab", "Lobster", "Shrimp", "Clownfish", "Angelfish", "Goldfish", "Betta Fish", "Turtle", "Tortoise", "Snail", "Slug", "Worm", "Ant", "Bee", "Butterfly", "Moth", "Spider", "Scorpion", "Centipede", "Millipede", "Grasshopper", "Cricket", "Dragonfly", "Ladybug", "Firefly", "Praying Mantis", "Cockroach", "Termite", "Flea", "Tick", "Mosquito", "Fly", "Wasp", "Hornet", "Beetle", "Weevil", "Stag Beetle", "Ladybird Beetle", "Dung Beetle", "Japanese Beetle", "Rhinoceros Beetle", "Goliath Beetle", "Atlas Beetle", "Fire Ant", "Carpenter Ant", "Leafcutter Ant", "Army Ant", "Bullet Ant", "Harvester Ant", "Sugar Ant", "Pharaoh Ant", "Thief Ant", "Pavement Ant", "Odorous House Ant", "Little Black Ant", "Bigheaded Ant", "Crazy Ant", "Ghost Ant", "Red Imported Fire Ant", "Southern Fire Ant", "Black Carpenter Ant", "Red Carpenter Ant", "Velvet Ant", "Cow Killer Ant"],
        "Fruits": ["Apple", "Banana", "Orange", "Grapes", "Strawberry", "Blueberry", "Raspberry", "Pineapple", "Mango", "Peach", "Watermelon", "Cantaloupe", "Honeydew", "Kiwi", "Papaya", "Pomegranate", "Plum", "Cherry", "Apricot", "Fig", "Date", "Coconut", "Lemon", "Lime", "Tangerine", "Grapefruit", "Passion Fruit", "Dragon Fruit", "Star Fruit", "Lychee", "Guava", "Persimmon", "Cranberry", "Blackberry", "Clementine", "Nectarine", "Quince", "Rhubarb", "Tamarind", "Jackfruit", "Durian", "Sapodilla", "Soursop", "Longan", "Mangosteen", "Jabuticaba", "Açaí Berry", "Elderberry"],
        "Vegetables": ["Carrot", "Broccoli", "Spinach", "Potato", "Tomato", "Cucumber", "Bell Pepper", "Onion", "Garlic", "Lettuce", "Cabbage", "Cauliflower", "Zucchini", "Eggplant", "Radish", "Beetroot", "Pumpkin", "Squash", "Sweet Potato", "Asparagus", "Artichoke", "Brussels Sprouts", "Celery", "Kale", "Swiss Chard"],
        "Countries": ["United States", "Canada", "Mexico", "Brazil", "Argentina", "United Kingdom", "France", "Germany", "Italy", "Spain", "Portugal", "Russia", "China", "Japan", "India", "Australia", "South Africa", "Egypt", "Nigeria", "Kenya", "Ghana", "Morocco", "Tunisia", "Algeria"],
        "Famous Landmarks": ["Eiffel Tower", "Great Wall of China", "Statue of Liberty", "Taj Mahal", "Colosseum", "Pyramids of Giza", "Machu Picchu", "Sydney Opera House", "Big Ben", "Christ the Redeemer", "Stonehenge", "Acropolis of Athens", "Petra", "Angkor Wat", "Burj Khalifa"],
        "Famous Slogans": ["Just Do It", "Think Different", "I'm Lovin' It", "Have It Your Way", "The Ultimate Driving Machine", "Because You're Worth It", "Melts in Your Mouth, Not in Your Hands", "Taste the Rainbow", "The Happiest Place on Earth", "Finger Lickin' Good", "Expect More. Pay Less.", "Save Money. Live Better.", "Eat Fresh", "The Quicker Picker Upper", "Can You Hear Me Now?"],
        "Before and After": ["Bread and Butter", "Salt and Pepper", "Peanut Butter and Jelly", "Fish and Chips", "Macaroni and Cheese", "Bacon and Eggs", "Milk and Cookies", "Spaghetti and Meatballs", "Coffee and Donuts", "Wine and Cheese", "Tea and Biscuits", "Ham and Cheese", "Chicken and Waffles", "Pasta and Sauce", "Rice and Beans", "Chips and Salsa", "Burger and Fries", "Pizza and Beer", "Tacos and Guacamole", "Hot Dog and Mustard", "Ice Cream and Cake", "Popcorn and Movie", "Soup and Sandwich", "Salad and Dressing", "Steak and Potatoes", "Cereal and Milk", "Bagel and Cream Cheese", "Pancakes and Syrup"],
        "Things people say": ["Break a leg", "Bite the bullet", "Burn the midnight oil", "Hit the hay", "Kick the bucket", "Let the cat out of the bag", "Piece of cake", "Spill the beans", "Under the weather", "When pigs fly", "You can't judge a book by its cover", "A blessing in disguise", "A dime a dozen", "Actions speak louder than words", "Add insult to injury", "Barking up the wrong tree", "Beating around the bush", "Better late than never", "Bite off more than you can chew", "Burning the candle at both ends", "Caught between a rock and a hard place", "Cost an arm and a leg", "Cut to the chase", "Don't count your chickens before they hatch", "Don't put all your eggs in one basket", "Every cloud has a silver lining", "Get a taste of your own medicine", "Give someone the cold shoulder", "Go back to the drawing board", "Hit the nail on the head", "In the heat of the moment", "It takes two to tango", "Jump on the bandwagon", "Kill two birds with one stone", "Let sleeping dogs lie", "Miss the boat", "No pain, no gain", "On cloud nine", "Once in a blue moon", "Out of the frying pan and into the fire", "Piece of cake", "Put all your eggs in one basket", "Read between the lines", "See eye to eye", "Sit on the fence", "Speak of the devil", "Steal someone's thunder", "Take it with a grain of salt", "The ball is in your court", "The best of both worlds", "The early bird catches the worm", "The elephant in the room", "Throw in the towel", "Turn a blind eye"],
        "90's TV Shows": ["Friends", "The Fresh Prince of Bel-Air", "Seinfeld", "The X-Files", "Buffy the Vampire Slayer", "The Simpsons", "Full House", "Saved by the Bell", "Dawson's Creek", "The Nanny", "The Office", "Frasier", "Twin Peaks", "Three's Company", "Cheers", "ER", "Gilligan's Island", "The Golden Girls", "The Wonder Years", "Family Matters"],
        "2000's Hits Songs": ["Hey Ya", "Umbrella", "Crazy in Love", "I Gotta Feeling", "Poker Face", "Rolling in the Deep", "Single Ladies Put a Ring on It", "Hotline Bling", "Shape of You", "Uptown Funk", "Call Me Maybe", "Tik Tok", "Party in the USA", "Bad Romance", "Hips Don't Lie", "Toxic", "Since U Been Gone", "Complicated", "Mr. Brightside", "Seven Nation Army", "In Da Club", "Lose Yourself", "Gold Digger", "Ignition Remix", "Hot in Herre", "Yeah!", "Crank That Soulja Boy", "I Will Always Love You", "My Heart Will Go On", "I Don't Want to Miss a Thing", "Livin' la Vida Loca", "Bye Bye Bye", "Oops I Did It Again", "All the Small Things", "Mr. Brightside", "Boulevard of Broken Dreams"],
        "Things around the house": ["Couch", "Television", "Refrigerator", "Microwave", "Oven", "Stove", "Dishwasher", "Washing Machine", "Dryer", "Bed", "Dresser", "Closet", "Bookshelf", "Coffee Table", "Dining Table", "Chairs", "Desk", "Lamp", "Curtains", "Rug", "Carpet", "Wall Art", "Clock", "Mirror", "Toaster", "Blender", "Vacuum Cleaner", "Iron", "Ironing Board", "Shower", "Bathtub", "Toilet", "Sink", "Faucet", "Towel Rack", "Soap Dispenser", "Toothbrush Holder", "Trash Can", "Laundry Basket", "Broom", "Mop", "Bucket", "Plunger", "First Aid Kit", "Fire Extinguisher", "Smoke Detector", "Carbon Monoxide Detector", "Light Switch", "Power Outlet", "Extension Cord", "Surge Protector", "Remote Control", "Game Console", "Computer", "Printer", "Router", "Modem", "Cable Box", "DVD Player", "Blu Ray Player", "Sound System", "Speakers", "Headphones", "Smartphone", "Tablet", "Laptop"],
    }
    spin_colors = [RED, GREEN, BLUE, YELLOW, RED, GREEN, BLUE, YELLOW] # Color list for wheel
    text_color = WHITE
    bg_color = DARK_PURPLE
    rect_width = 40
    rect_height = 50
    num_players = 0

    # --- Intro Screen with Spinning Wheel Prop ---
    show_intro_screen(screen, spin_colors, text_color)

    # --- Player Setup ---
    while num_players < 1 or num_players > 3:
        screen.fill(bg_color)
        display_message(screen, "WHEEL OF FORTUNE", FONT_XXLARGE, text_color, (SCREEN_WIDTH // 2, 100))
        pygame.display.flip()
        num_players = int(get_text_input(screen, "Enter number of players (1-3):", FONT_MEDIUM, text_color, bg_color, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), overlap=True))

    players = []
    for i in range(num_players):
        screen.fill(bg_color)
        display_message(screen, f"WHEEL OF FORTUNE", FONT_XLARGE, text_color, (SCREEN_WIDTH // 2, 100))
        pygame.display.flip()
        player_name = get_text_input(screen, f"Enter name for Player {i + 1}:", FONT_MEDIUM, text_color, bg_color, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), overlap=True)
        players.append({'name': player_name, 'score': 0, 'total_score': 0})

    current_player_index = 0
    game_over = False
    round_num = 1

    # --- Game Loop ---
    while not game_over:
        screen.fill(bg_color)
        category = choose_category(screen, categories, FONT_MEDIUM, text_color, bg_color)
        puzzle = generate_puzzle(category, puzzles)
        revealed = create_revealed_array(puzzle)
        wheel_angle = 0
        current_player = players[current_player_index]

        # --- Round Loop ---
        round_over = False
        guessed_letters = set()
        while not round_over:
            screen.fill(bg_color)  # Clear the screen at the start of each turn
            display_message(screen, f"Round {round_num}", FONT_LARGE, text_color, (SCREEN_WIDTH // 2, 50))
            display_current_player(screen, current_player['name'], FONT_MEDIUM, text_color, (20, 20))
            display_player_info(screen, players[0], FONT_MEDIUM, text_color, (20, 60))  # Player 1 info
            if num_players > 1:
                display_player_info(screen, players[1], FONT_MEDIUM, text_color, (20, 100))  # Player 2 info
            if num_players > 2:
                display_player_info(screen, players[2], FONT_MEDIUM, text_color, (20, 140))  # Player 3 info

            draw_wheel(screen, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2), 370, wheel_angle, WHEEL_VALUES, spin_colors, text_color)
            if not all(revealed):
                display_board(screen, puzzle, revealed, FONT_MEDIUM, text_color, rect_width, rect_height, WORD_DISPLAY_X, SCREEN_WIDTH) #show the board
            
            # Display category
            
            # display_message(screen,"Category: " + category, FONT_MEDIUM, text_color, (WORD_DISPLAY_X + 150,  SCREEN_HEIGHT // 4))

            # --- Info section (top right) ---
            info_x = WORD_DISPLAY_X
            info_y = 150
            info_w = 600
            info_h = 200
            draw_info_section(
                screen, info_x, info_y, info_w, info_h,
                player_name=current_player['name'],
                player_score=current_player['score'],
                spin_value=spin_value if 'spin_value' in locals() else None,
                font=FONT_MEDIUM,
                category=category,
            )

            # --- Game Options ---
             
            mouse_pos = pygame.mouse.get_pos()
            

            if has_unrevealed_vowels(puzzle, revealed):
                buy_vowel_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT * 3 // 4, 300, 50)
                draw_button(screen, buy_vowel_button, "Buy Vowel (-$250)", FONT_MEDIUM, text_color, HIGHLIGHT_COLOR, mouse_pos, button_id="buy_vowel")
            else:
                buy_vowel_button = None

            if has_unrevealed_consonants(puzzle, revealed):
                spin_button = pygame.Rect(SCREEN_WIDTH // 2 + 250, SCREEN_HEIGHT * 3 // 4, 200, 50)
                draw_button(screen, spin_button, "Spin Wheel", FONT_MEDIUM, text_color, HIGHLIGHT_COLOR, mouse_pos, button_id="spin")
            else:
                spin_button = None

            solve_puzzle_button = pygame.Rect(SCREEN_WIDTH // 2 + 500, SCREEN_HEIGHT * 3 // 4, 210, 50)
            draw_button(screen, solve_puzzle_button, "Solve Puzzle", FONT_MEDIUM, text_color, HIGHLIGHT_COLOR, mouse_pos, button_id="solve")

            # --- New Game Button (top right) ---
            new_game_button = pygame.Rect(SCREEN_WIDTH - 220, 30, 180, 50)
            draw_button(screen, new_game_button, "New Game", FONT_MEDIUM, text_color, HIGHLIGHT_COLOR, mouse_pos, button_id="new_game")

            pygame.display.flip()

            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if spin_button and spin_button.collidepoint(mouse_pos):
                        button_select_sound.play()  # Play sound on selection
                        wheel_angle = spin_wheel(screen, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2), 370, WHEEL_VALUES, wheel_angle, 3, spin_colors, text_color)
                        spin_value = get_wheel_value(wheel_angle, WHEEL_VALUES)
                        action, current_player_index = handle_spin_result(screen, current_player, spin_value, puzzle, revealed, FONT_MEDIUM, text_color, players, current_player_index, wheel_sound, bankrupt_sound, lose_turn_sound, category=category, guessed_letters=guessed_letters)
                        if action == 'BANKRUPT' or action == 'LOSE A TURN' or action == 'INCORRECT':
                            current_player_index = switch_player(current_player_index, players)
                            current_player = players[current_player_index]
                        elif action == 'CORRECT':
                            pass
                        elif action == 'INVALID':
                            pass
                    elif buy_vowel_button and buy_vowel_button.collidepoint(mouse_pos):
                        button_select_sound.play()  # Play sound on selection
                        vowel_bought = handle_buy_vowel(screen, current_player, puzzle, revealed, FONT_MEDIUM, text_color, bg_color, buy_vowel_sound, guessed_letters=guessed_letters)
                        if not vowel_bought:
                            current_player_index = switch_player(current_player_index, players)
                            current_player = players[current_player_index]
                    elif solve_puzzle_button.collidepoint(mouse_pos):
                        button_select_sound.play()  # Play sound on selection
                        solved = handle_solve_puzzle(screen,current_player, puzzle, revealed, FONT_MEDIUM, text_color, bg_color)
                        if solved:
                            round_over = True
                    elif new_game_button.collidepoint(mouse_pos):
                        button_select_sound.play()
                        main()  # Restart the game
                        return

            # --- Check for puzzle solved after every action ---
            if all(revealed):
                display_board(screen, puzzle, revealed, FONT_MEDIUM, text_color, rect_width, rect_height, WORD_DISPLAY_X, SCREEN_WIDTH) #show the board
                round_over = True
                pygame.display.flip()

        # Determine round winner
        round_winner = max(players, key=lambda p: p['score'])
        round_winner['total_score'] += round_winner['score']
        display_round_winner(screen, round_winner, FONT_XLARGE, YELLOW)
        pygame.display.flip()
        time.sleep(5)

        # Reset scores for the next round
        reset_round(players)
        round_num += 1

        if round_num > 3:  # Play 3 rounds
            game_over = True

    # Determine overall winner (highest score after 3 rounds)
    overall_winner = max(players, key=lambda p: p['total_score'])
    screen.fill(bg_color)
    display_message(screen, "Game Over!", FONT_XLARGE, text_color, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    display_message(screen, f"Overall Winner: {overall_winner['name']} with ${overall_winner['total_score']}!", FONT_XLARGE, YELLOW, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    pygame.display.flip()
    time.sleep(5)

    pygame.quit()
    
if __name__ == "__main__":
    pygame.mixer.music.play(-1)  # Loop the music
    main()
