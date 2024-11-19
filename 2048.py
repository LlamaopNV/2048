import pygame
import random
import sys


pygame.init()
pygame.font.init()


GRID_SIZE = 4
TILE_SIZE = 100
MARGIN = 10
WINDOW_HEIGHT = GRID_SIZE * TILE_SIZE + (GRID_SIZE + 1) * MARGIN
BUTTON_HEIGHT = 50
SCORE_HEIGHT = 50
LOG_HEIGHT = 100
WINDOW_SIZE = (
GRID_SIZE * TILE_SIZE + (GRID_SIZE + 1) * MARGIN, WINDOW_HEIGHT + BUTTON_HEIGHT + SCORE_HEIGHT + LOG_HEIGHT)
FONT = pygame.font.Font(None, 50)
SMALL_FONT = pygame.font.Font(None, 30)
SCREEN = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption('2048 Game')

# Colors
BACKGROUND_COLOR = (187, 173, 160)
EMPTY_TILE_COLOR = (205, 193, 180)
BUTTON_COLOR = (119, 110, 101)
BUTTON_TEXT_COLOR = (255, 255, 255)
TEXT_COLOR = (255, 255, 255)
LOG_TEXT_COLOR = (0, 0, 0)
LOG_BG_COLOR = (230, 230, 230)
TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}

def initialize_board():
    board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    add_new_tile(board)
    add_new_tile(board)
    return board


def add_new_tile(board):
    empty_tiles = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] == 0]
    if empty_tiles:
        r, c = random.choice(empty_tiles)
        board[r][c] = 2 if random.random() < 0.9 else 4


def draw_board(board, score, score_increment):
    SCREEN.fill(BACKGROUND_COLOR)  # Clear the screen with the background color
    # Draw score label
    score_text = FONT.render(f"Score: {score}", True, TEXT_COLOR)
    SCREEN.blit(score_text, (WINDOW_SIZE[0] // 2 - score_text.get_width() // 2 - 50, 10))

    if score_increment > 0:
        increment_text = FONT.render(f"+{score_increment}", True, (0, 255, 0))
        SCREEN.blit(increment_text, (WINDOW_SIZE[0] // 2 + score_text.get_width() // 2, 10))

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            value = board[r][c]
            tile_color = TILE_COLORS.get(value, EMPTY_TILE_COLOR)
            rect = pygame.Rect(
                c * TILE_SIZE + (c + 1) * MARGIN,
                r * TILE_SIZE + (r + 1) * MARGIN + SCORE_HEIGHT,
                TILE_SIZE, TILE_SIZE
            )
            pygame.draw.rect(SCREEN, tile_color, rect)
            if value != 0:
                text = FONT.render(str(value), True, (119, 110, 101))
                text_rect = text.get_rect(center=rect.center)
                SCREEN.blit(text, text_rect)

    button_rect = pygame.Rect(WINDOW_SIZE[0] // 2 - 50, WINDOW_HEIGHT + 10 + SCORE_HEIGHT, 100, 30)
    pygame.draw.rect(SCREEN, BUTTON_COLOR, button_rect)
    button_text = FONT.render("Reset", True, BUTTON_TEXT_COLOR)
    text_rect = button_text.get_rect(center=button_rect.center)
    SCREEN.blit(button_text, text_rect)
    return button_rect


def draw_log(log):
    log_rect = pygame.Rect(0, WINDOW_SIZE[1] - LOG_HEIGHT, WINDOW_SIZE[0], LOG_HEIGHT)
    pygame.draw.rect(SCREEN, LOG_BG_COLOR, log_rect)
    y_offset = WINDOW_SIZE[1] - LOG_HEIGHT + 10
    for entry in log[-3:]:
        log_text = SMALL_FONT.render(entry, True, LOG_TEXT_COLOR)
        SCREEN.blit(log_text, (10, y_offset))
        y_offset += 30


def rotate_board(board, clockwise=True):
    if clockwise:
        return [list(row) for row in zip(*board[::-1])]
    else:
        return [list(row)[::-1] for row in zip(*board)]


def move_and_merge(board, direction):
    moved = False
    score_increment = 0
    for _ in range(direction):
        board = rotate_board(board)  # Rotate to handle movement in desired direction
    for i in range(GRID_SIZE):
        row = [tile for tile in board[i] if tile != 0]  # Remove zeros
        new_row = []
        skip = False
        for j in range(len(row)):
            if skip:
                skip = False
                continue
            if j < len(row) - 1 and row[j] == row[j + 1]:
                merged_value = row[j] * 2
                new_row.append(merged_value)
                score_increment += merged_value
                skip = True
            else:
                new_row.append(row[j])
        new_row += [0] * (GRID_SIZE - len(new_row))  # Fill remaining spaces with zeros
        if board[i] != new_row:
            moved = True
        board[i] = new_row
    for _ in range((4 - direction) % 4):  # Rotate back to original orientation
        board = rotate_board(board, clockwise=False)
    return moved, board, score_increment


def main():
    board = initialize_board()
    score = 0
    score_increment = 0
    running = True
    clock = pygame.time.Clock()
    log = []

    while running:
        previous_board = [row[:] for row in board]
        button_rect = draw_board(board, score, score_increment)
        draw_log(log)
        pygame.display.update()
        score_increment = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                moved = False
                increment = 0
                input_key = ""
                if event.key == pygame.K_LEFT:
                    moved, board, increment = move_and_merge(board, 0)  # 0 rotations for left
                    input_key = "Left"
                elif event.key == pygame.K_RIGHT:
                    moved, board, increment = move_and_merge(board, 2)  # 2 rotations for right
                    input_key = "Right"
                elif event.key == pygame.K_UP:
                    moved, board, increment = move_and_merge(board, 3)  # 3 rotations for up
                    input_key = "Up"
                elif event.key == pygame.K_DOWN:
                    moved, board, increment = move_and_merge(board, 1)  # 1 rotation for down
                    input_key = "Down"
                if moved:
                    score += increment
                    score_increment = increment  # Set the increment to display briefly
                    add_new_tile(board)
                    log.append(f"Move: {input_key}, +{increment} points, Total Score: {score}")
                else:
                    log.append(f"Invalid Move: {input_key}")
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    board = initialize_board()
                    score = 0
                    score_increment = 0
                    log = []  # Clear the log

        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
