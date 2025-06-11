import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Constants
GRID_SIZE = 8
SQUARE_SIZE = 60
MARGIN = 2
WINDOW_SIZE = GRID_SIZE * SQUARE_SIZE + (GRID_SIZE + 1) * MARGIN
GOOD = True
# Colors
BG_COLOR = (30, 30, 30)
SQUARE_COLOR = (70, 130, 180)

# Set up display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 300))
pygame.display.set_caption("8x8 Grid")

# Initialize grid
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Initialize score
score = 0
font = pygame.font.SysFont('Arial', 30)  # Choose a font and size

class Block:
    def __init__(self, shape, color=(255, 215, 0), x=0, y=0):
        self.shape = shape
        self.color = color
        self.rows = len(shape)
        self.cols = len(shape[0]) if self.rows > 0 else 0
        self.x = x
        self.y = y

    def draw(self, surface, square_size, margin):
        for r, row in enumerate(self.shape):
            for c, cell in enumerate(row):
                if cell:
                    x = self.x + c * (square_size + margin)
                    y = self.y + r * (square_size + margin)
                    pygame.draw.rect(surface, self.color, (x, y, square_size, square_size))

    def collidepoint(self, pos, square_size, margin):
        px, py = pos
        width = self.cols * square_size + (self.cols - 1) * margin
        height = self.rows * square_size + (self.rows - 1) * margin
        return self.x <= px <= self.x + width and self.y <= py <= self.y + height

    def move_ip(self, dx, dy):
        self.x += dx
        self.y += dy

    def can_place_on_grid(self, grid, grid_size, square_size, margin):
        start_col = max(0, min((self.x - margin) // (square_size + margin), grid_size - self.cols))
        start_row = max(0, min((self.y - margin) // (square_size + margin), grid_size - self.rows))


        for r in range(self.rows):
            for c in range(self.cols):
                if self.shape[r][c]:
                    row = start_row + r
                    col = start_col + c
                    if not (0 <= row < grid_size and 0 <= col < grid_size):
                        return False
                    if grid[row][col] != 0:
                        return False
        return True
    
    def snap_to_grid(self, square_size, margin):
        self.x = round((self.x - MARGIN) / (square_size + margin)) * (square_size + margin) + MARGIN
        self.y = round((self.y - MARGIN) / (square_size + margin)) * (square_size + margin) + MARGIN
        

    def place_on_grid(self, grid, grid_size, square_size, margin):
        start_col = (self.x - MARGIN) // (square_size + margin)
        start_row = (self.y - MARGIN) // (square_size + margin)

        for r in range(self.rows):
            for c in range(self.cols):
                if self.shape[r][c]:
                    grid[start_row + r][start_col + c] = 1

        #DEBUGGING
        for row in grid:
            print(row)
        print(" ")
        print(" ")

def chk_for_complete(grid):
    global score
    rows_to_clear = []
    cols_to_clear = []

    # Check rows
    for i, row in enumerate(grid):
        if all(cell == 1 for cell in row):
            rows_to_clear.append(i)

    # Check columns
    for j in range(len(grid[0])):
        if all(grid[i][j] == 1 for i in range(len(grid))):
            cols_to_clear.append(j)

    # Clear rows
    for i in rows_to_clear:
        for j in range(len(grid[0])):
            grid[i][j] = 0
        score += 10

    # Clear columns
    for j in cols_to_clear:
        for i in range(len(grid)):
            grid[i][j] = 0
        score += 10

def can_block_fit_anywhere(grid, block_shape):
    grid_size = len(grid)
    block_rows = len(block_shape)
    block_cols = len(block_shape[0])

    for start_row in range(grid_size - block_rows + 1):
        for start_col in range(grid_size - block_cols + 1):
            # Check if block fits at (start_row, start_col)
            fits = True
            for r in range(block_rows):
                for c in range(block_cols):
                    if block_shape[r][c] == 1 and grid[start_row + r][start_col + c] != 0:
                        fits = False
                        break
                if not fits:
                    break
            if fits:
                return True  # Found at least one spot
    return False  # No spot found

# Create a 1x3 block and draw it below the grid
block_shapes = [
    # 1x3 line
    [[1, 1, 1]],
    # 3x1 vertical line
    [[1], [1], [1]],
    # 2x2 square
    [[1, 1],
     [1, 1]],
    # L-shape
    [[1, 0],
     [1, 0],
     [1, 1]],
    # Reverse L-shape
    [[0, 1],
     [0, 1],
     [1, 1]],
    # T-shape
    [[1, 1, 1],
     [0, 1, 0]],
    # S-shape
    [[0, 1, 1],
     [1, 1, 0]],
    # Z-shape
    [[1, 1, 0],
     [0, 1, 1]],
    # 1x1 block
    [[1]],
    # 2x1 block
    [[1, 1]],
    # 1x2 block
    [[1], [1]],
    # 3x2 rectangle
    [[1, 1],
     [1, 1],
     [1, 1]],
    # 2x3 rectangle
    [[1, 1, 1],
     [1, 1, 1]],
    # U-shape
    [[1, 0, 1],
     [1, 1, 1]],
    # Plus shape
    [[0, 1, 0],
     [1, 1, 1],
     [0, 1, 0]],
    # Big L
    [[1, 0, 0],
     [1, 0, 0],
     [1, 1, 1]],
    # Big reverse L
    [[0, 0, 1],
     [0, 0, 1],
     [1, 1, 1]],
    # 4x1 line
    [[1, 1, 1, 1]],
    # 1x4 line
    [[1], [1], [1], [1]],
]
SHAPE_COUNT = len(block_shapes)

# Assign a color for each block 
block_colors = [
    (255, 215, 0),    # gold
    (0, 191, 255),    # deep sky blue
    (50, 205, 50),    # lime green
    (255, 69, 0),     # orange red
    (138, 43, 226),   # blue violet
    (255, 140, 0),    # dark orange
    (0, 206, 209),    # dark turquoise
    (255, 105, 180),  # hot pink
    (255, 255, 255),  # white
    (128, 128, 128),  # gray
    (255, 0, 0),      # red
    (0, 255, 0),      # green
    (0, 0, 255),      # blue
    (255, 255, 0),    # yellow
    (0, 255, 255),    # cyan
    (255, 0, 255),    # magenta
    (210, 180, 140),  # tan
    (0, 128, 128),    # teal
    (128, 0, 128),    # purple
    (255, 20, 147),   # deep pink
]

# Create a list of Block instances
currentblocks = []
for i in range(3):
    shape = block_shapes[random.randint(0, SHAPE_COUNT - 1)]
    color = block_colors[i % len(block_colors)]
    x = MARGIN + i * 150  # spacing between blocks
    y = WINDOW_SIZE + 40
    currentblocks.append(Block(shape, color, x, y))


# Main loop
active_block = None
running = True

while running:
    screen.fill(BG_COLOR)
    
    # Draw grid
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = MARGIN + col * (SQUARE_SIZE + MARGIN)
            y = MARGIN + row * (SQUARE_SIZE + MARGIN)
            pygame.draw.rect(screen, SQUARE_COLOR, (x, y, SQUARE_SIZE, SQUARE_SIZE))
    
    # Draw placed blocks based on grid state
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if grid[row][col]:
                x = MARGIN + col * (SQUARE_SIZE + MARGIN)
                y = MARGIN + row * (SQUARE_SIZE + MARGIN)
                pygame.draw.rect(screen, (200, 200, 200), (x, y, SQUARE_SIZE, SQUARE_SIZE))

    # Draw movable blocks
    for block in currentblocks:
        block.draw(screen, SQUARE_SIZE, MARGIN)

    # Spawn new blocks only when all are placed
    if len(currentblocks) == 0:
        for i in range(3):  # Spawn 3 new blocks
            shape = block_shapes[random.randint(0, SHAPE_COUNT - 1)]
            color = block_colors[i % len(block_colors)]
            x = MARGIN + i * 150  # spacing between blocks
            y = WINDOW_SIZE + 40
            currentblocks.append(Block(shape, color, x, y))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, block in enumerate(currentblocks):
                if block.collidepoint(event.pos, SQUARE_SIZE, MARGIN):
                    active_block = i
                    mouse_x, mouse_y = event.pos
                    offset_x = block.x - mouse_x
                    offset_y = block.y - mouse_y
                    # Save original position to revert if placement fails
                    block.orig_x = block.x
                    block.orig_y = block.y


        elif event.type == pygame.MOUSEMOTION and active_block is not None:
            mouse_x, mouse_y = event.pos
            currentblocks[active_block].x = mouse_x + offset_x
            currentblocks[active_block].y = mouse_y + offset_y

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if active_block is not None:
                block = currentblocks[active_block]
                if block.can_place_on_grid(grid, GRID_SIZE, SQUARE_SIZE, MARGIN):
                    block.snap_to_grid(SQUARE_SIZE, MARGIN)
                    block.place_on_grid(grid, GRID_SIZE, SQUARE_SIZE, MARGIN)
                    score += sum(sum(row) for row in block.shape)
                    currentblocks.pop(active_block)
                    chk_for_complete(grid)
                    
                    # Only check for game over after successful placement
                    if len(currentblocks) > 0:
                        all_cant_fit = True
                        for block in currentblocks:
                            if can_block_fit_anywhere(grid, block.shape):
                                all_cant_fit = False
                                break
                        
                        if all_cant_fit:
                            BG_COLOR = (200, 0, 0)
                            game_over_text = font.render('Game Over!', True, (255, 255, 255))
                            game_over_rect = game_over_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE + 150))
                            screen.blit(game_over_text, game_over_rect)
                            pygame.display.flip()
                            pygame.time.wait(5000)
                            running = False
                else:
                    # Revert block to original position
                    block.x = block.orig_x
                    block.y = block.orig_y
            active_block = None

    # Draw score at the bottom
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    score_rect = score_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE + 280))  # Moved further down
    screen.blit(score_text, score_rect)
    pygame.display.flip()

pygame.quit()
sys.exit()
