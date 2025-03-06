import pygame
import random
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
class GameState(Enum):
    MENU = "menu"
    SELECTING = "selecting"
    SHOW_CHOICES = "show_choices"
    MINUS_ONE = "minus_one"
    RESULT = "result"
    BATTLE = "battle"

class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (200, 0, 0)
    RED_HOVER = (255, 100, 100)
    BLUE = (0, 0, 200)
    BLUE_HOVER = (100, 100, 255)
    GREEN = (0, 200, 0)
    GREEN_HOVER = (100, 255, 100)
    GRAY = (180, 180, 180)
    GRAY_HOVER = (220, 220, 220)

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rock Paper Scissors Minus One")

# Fonts
FONT = pygame.font.Font(None, 36)
BIG_FONT = pygame.font.Font(None, 48)

# Load Images
def load_image(filename):
    try:
        image = pygame.image.load(filename)
        return pygame.transform.scale(image, (150, 150))
    except pygame.error as e:
        print(f"Error loading {filename}: {e}")
        pygame.quit()
        exit()

ROCK_IMG = load_image("rock.png")
PAPER_IMG = load_image("paper.png")
SCISSORS_IMG = load_image("scissors.png")
IMAGES = {"Rock": ROCK_IMG, "Paper": PAPER_IMG, "Scissors": SCISSORS_IMG}

# Button Class
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.callback = callback

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect)
        text_surface = FONT.render(self.text, True, Colors.BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if (event.type == pygame.MOUSEBUTTONDOWN and 
            self.rect.collidepoint(event.pos) and 
            self.callback):
            self.callback()
            return True
        return False

# Game Setup
OPTIONS = ["Rock", "Paper", "Scissors"]
player_hands = []
computer_hands = []
user_sets_won = 0
computer_sets_won = 0
current_set = 1
max_sets = 1
wins_needed = 1
game_state = GameState.MENU
clock = pygame.time.Clock()
player_removed = None
computer_removed = None

# Animation variables
battle_timer = 0
player_x = 100
computer_x = WIDTH - 250
battle_complete = False

# Buttons initialization
def start_game(sets):
    global max_sets, game_state, wins_needed
    max_sets = sets
    wins_needed = (sets + 1) // 2
    game_state = GameState.SELECTING

CHOICE_BUTTONS = [
    Button(100, 400, 150, 50, "Rock", Colors.RED, Colors.RED_HOVER, 
           lambda: player_hands.append("Rock") if len(player_hands) < 2 else None),
    Button(325, 400, 150, 50, "Paper", Colors.BLUE, Colors.BLUE_HOVER,
           lambda: player_hands.append("Paper") if len(player_hands) < 2 else None),
    Button(550, 400, 150, 50, "Scissors", Colors.GREEN, Colors.GREEN_HOVER,
           lambda: player_hands.append("Scissors") if len(player_hands) < 2 else None)
]

MENU_BUTTONS = [
    Button(100, 200, 150, 50, "Best of 1", Colors.GRAY, Colors.GRAY_HOVER, lambda: start_game(1)),
    Button(325, 200, 150, 50, "Best of 3", Colors.GRAY, Colors.GRAY_HOVER, lambda: start_game(3)),
    Button(550, 200, 150, 50, "Best of 5", Colors.GRAY, Colors.GRAY_HOVER, lambda: start_game(5))
]

# Game Logic
def determine_winner(player, computer):
    if player == computer:
        return "Tie"
    winning_combos = {("Rock", "Scissors"), ("Paper", "Rock"), ("Scissors", "Paper")}
    return "Player" if (player, computer) in winning_combos else "Computer"

# Main game loop
running = True
keep_buttons = []

while running:
    screen.fill(Colors.WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == GameState.MENU:
            for button in MENU_BUTTONS:
                button.handle_event(event)
                
        elif game_state == GameState.SELECTING:
            for button in CHOICE_BUTTONS:
                button.handle_event(event)
            if (event.type == pygame.KEYDOWN and 
                event.key == pygame.K_SPACE and 
                len(player_hands) == 2):
                computer_hands = random.sample(OPTIONS, 2)
                game_state = GameState.SHOW_CHOICES
                
        elif game_state == GameState.SHOW_CHOICES:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                keep_buttons = [
                    Button(200, 400, 150, 50, player_hands[0], Colors.GRAY, Colors.GRAY_HOVER,
                           lambda: (globals().update({'player_removed': player_hands.pop(1), 'game_state': GameState.RESULT}))),
                    Button(360, 400, 150, 50, player_hands[1], Colors.GRAY, Colors.GRAY_HOVER,
                           lambda: (globals().update({'player_removed': player_hands.pop(0), 'game_state': GameState.RESULT})))
                ]
                game_state = GameState.MINUS_ONE
                
        elif game_state == GameState.MINUS_ONE:
            for button in keep_buttons:
                if button.handle_event(event):
                    computer_removed = computer_hands.pop(random.randrange(len(computer_hands)))
                    keep_buttons.clear()  # Disable buttons after one is clicked
                    
        elif game_state == GameState.RESULT:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                battle_timer = 0
                player_x = 100
                computer_x = WIDTH - 250
                battle_complete = False
                game_state = GameState.BATTLE
                
        elif game_state == GameState.BATTLE:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and battle_complete:
                winner = determine_winner(player_hands[0], computer_hands[0])
                if winner == "Player":
                    user_sets_won += 1
                elif winner == "Computer":
                    computer_sets_won += 1
                
                if user_sets_won >= wins_needed or computer_sets_won >= wins_needed:
                    running = False
                else:
                    current_set += 1
                    player_hands.clear()
                    computer_hands.clear()
                    player_removed = None
                    computer_removed = None
                    game_state = GameState.SELECTING

    # Rendering and Animation
    if game_state == GameState.MENU:
        text = BIG_FONT.render("Choose Best of:", True, Colors.BLACK)
        screen.blit(text, text.get_rect(center=(WIDTH//2, 100)))
        for button in MENU_BUTTONS:
            button.draw(screen)
            
    elif game_state == GameState.SELECTING:
        text = BIG_FONT.render(f"Set {current_set}: Choose Two Hands", True, Colors.BLACK)
        screen.blit(text, text.get_rect(center=(WIDTH//2, 100)))
        for button in CHOICE_BUTTONS:
            button.draw(screen)
        if len(player_hands) == 2:
            text = FONT.render("Hands Selected! Press SPACE", True, Colors.BLACK)
            screen.blit(text, text.get_rect(center=(WIDTH//2, 500)))
            
    elif game_state == GameState.SHOW_CHOICES:
        text = BIG_FONT.render("Both Players Chose!", True, Colors.BLACK)
        screen.blit(text, text.get_rect(center=(WIDTH//2, 50)))
        
        # Position player's options on the far left
        for i, player_hand in enumerate(player_hands):
            screen.blit(IMAGES[player_hand], (50 + i*180, 250))  # Far left, spaced out
        
        # Position computer's options on the far right, within screen bounds
        for i, comp_hand in enumerate(computer_hands):
            screen.blit(IMAGES[comp_hand], (WIDTH - 350 + i*180, 250))  # Far right, spaced out, within 800px
        
        text = FONT.render("Press SPACE to remove one hand", True, Colors.BLACK)
        screen.blit(text, text.get_rect(center=(WIDTH//2, 500)))
        
    elif game_state == GameState.MINUS_ONE:
        text = BIG_FONT.render("Choose Hand to Keep!", True, Colors.BLACK)
        screen.blit(text, text.get_rect(center=(WIDTH//2, 50)))
        for i, hand in enumerate(player_hands):
            screen.blit(IMAGES[hand], (200 + i*120, 250))
        for button in keep_buttons:
            button.draw(screen)
            
    elif game_state == GameState.RESULT:
        text = BIG_FONT.render(f"Set {current_set} Result", True, Colors.BLACK)
        screen.blit(text, text.get_rect(center=(WIDTH//2, 50)))
        
        if (player_hands and len(player_hands) == 1 and 
            computer_hands and len(computer_hands) == 1 and 
            player_removed and computer_removed):
            text = FONT.render(f"You removed: {player_removed}", True, Colors.BLACK)
            screen.blit(text, text.get_rect(center=(WIDTH//2, 120)))
            text = FONT.render(f"CPU removed: {computer_removed}", True, Colors.BLACK)
            screen.blit(text, text.get_rect(center=(WIDTH//2, 150)))
            
            text = FONT.render("Final:", True, Colors.BLACK)
            screen.blit(text, text.get_rect(center=(WIDTH//2, 200)))
            
            # Position player's final option on the far left
            if player_hands[0] in IMAGES:
                screen.blit(IMAGES[player_hands[0]], (50, 230))  # Far left, within screen
            
            # Position computer's final option on the far right
            if computer_hands[0] in IMAGES:
                screen.blit(IMAGES[computer_hands[0]], (650, 230))  # Far right, within screen
            
            text = FONT.render("Press SPACE for Battle!", True, Colors.BLACK)
            screen.blit(text, text.get_rect(center=(WIDTH//2, 450)))
        
        text = FONT.render(f"Best of {max_sets}: You {user_sets_won} - {computer_sets_won} CPU", 
                          True, Colors.BLACK)
        screen.blit(text, text.get_rect(center=(WIDTH//2, 350)))
        
    elif game_state == GameState.BATTLE:
        winner = determine_winner(player_hands[0], computer_hands[0])
        battle_timer += 1
        
        if battle_timer < 60:
            player_x += (WIDTH/2 - 250 - player_x) * 0.1
            computer_x += (WIDTH/2 + 100 - computer_x) * 0.1
        elif battle_timer < 90 and winner != "Tie":
            if winner == "Player":
                player_x += 10
            else:
                computer_x -= 10
        elif battle_timer >= 90:
            battle_complete = True
        
        if battle_timer < 90 or winner == "Tie" or winner == "Player":
            screen.blit(IMAGES[player_hands[0]], (player_x, HEIGHT//2 - 75))
        if battle_timer < 90 or winner == "Tie" or winner == "Computer":
            screen.blit(IMAGES[computer_hands[0]], (computer_x, HEIGHT//2 - 75))
        
        if battle_complete:
            winner_text = "Tie Game!" if winner == "Tie" else f"{winner} Wins!"
            text = FONT.render(winner_text, True, Colors.BLACK)
            screen.blit(text, text.get_rect(center=(WIDTH//2, 150)))
            
            text = FONT.render(f"Best of {max_sets}: You {user_sets_won} - {computer_sets_won} CPU", 
                              True, Colors.BLACK)
            screen.blit(text, text.get_rect(center=(WIDTH//2, 200)))
            
            text = FONT.render("Press ENTER for next set", True, Colors.BLACK)
            screen.blit(text, text.get_rect(center=(WIDTH//2, 500)))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()