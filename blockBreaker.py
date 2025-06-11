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
font = pygame.font.SysFont('Arial', 30)

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
            fits = True
            for r in range(block_rows):
                for c in range(block_cols):
                    if block_shape[r][c] == 1 and grid[start_row + r][start_col + c] != 0:
                        fits = False
                        break
                if not fits:
                    break
            if fits:
                return True
    return False

def spawn_blocks(grid, count=3):
    new_blocks = []
    attempts = 0
    while len(new_blocks) < count and attempts < 100:
        shape = block_shapes[random.randint(0, SHAPE_COUNT - 1)]
        if can_block_fit_anywhere(grid, shape):
            color = block_colors[len(new_blocks) % len(block_colors)]
            x = MARGIN + len(new_blocks) * 150
            y = WINDOW_SIZE + 40
            new_blocks.append(Block(shape, color, x, y))
        attempts += 1
    return new_blocks


# Create a 1x3 block and draw it below the grid
block_shapes = [
    # Basic shapes (as before)
    [[1, 1, 1]],                 # 1x3 horizontal line
    [[1], [1], [1]],             # 3x1 vertical line
    [[1, 1],                     # 2x2 square
     [1, 1]],
    [[1, 0],                     # L-shape
     [1, 0],
     [1, 1]],
    [[0, 1],                     # Reverse L-shape
     [0, 1],
     [1, 1]],
    [[1, 1, 1],                  # T-shape
     [0, 1, 0]],
    [[0, 1, 1],                  # S-shape
     [1, 1, 0]],
    [[1, 1, 0],                  # Z-shape
     [0, 1, 1]],
    [[1]],                       # 1x1 block
    [[1, 1]],                    # 2x1 horizontal
    [[1], [1]],                  # 1x2 vertical
    [[1, 1],                     # 3x2 vertical rectangle
     [1, 1],
     [1, 1]],
    [[1, 1, 1],                  # 2x3 horizontal rectangle
     [1, 1, 1]],
    [[1, 0, 1],                  # U-shape
     [1, 1, 1]],
    [[0, 1, 0],                  # Plus shape
     [1, 1, 1],
     [0, 1, 0]],
    [[1, 0, 0],                  # Big L-shape
     [1, 0, 0],
     [1, 1, 1]],
    [[0, 0, 1],                  # Big reverse L-shape
     [0, 0, 1],
     [1, 1, 1]],
    [[1, 1, 1, 1]],              # 4x1 horizontal line
    [[1], [1], [1], [1]],        # 1x4 vertical line

    # Obscure / unusual shapes:
    
    # Stair-step shape (3 steps)
    [[1, 0, 0],
     [1, 1, 0],
     [1, 1, 1]],

    # Cross shape (5 blocks in a cross)
    [[0, 1, 0],
     [1, 1, 1],
     [0, 1, 0]],

    # L with a tail shape
    [[1, 0],
     [1, 1],
     [0, 1]],

    # Small zigzag shape
    [[1, 0],
     [1, 1],
     [0, 1]],

    # Fat T shape
    [[1, 1, 1],
     [0, 1, 0],
     [0, 1, 0]],

    # Wide Z shape
    [[1, 1, 0, 0],
     [0, 1, 1, 1]],

    # Block with hole in middle (ring-like)
    [[1, 1, 1],
     [1, 0, 1],
     [1, 1, 1]],

    # Narrow step shape
    [[1, 0],
     [1, 1],
     [0, 1],
     [0, 1]],

    # 3x3 solid block
    [[1, 1, 1],
     [1, 1, 1],
     [1, 1, 1]],

    # L with corner
    [[1, 0, 0],
     [1, 1, 0],
     [0, 1, 1]],

    # Fat S shape
    [[0, 1, 1, 0],
     [1, 1, 1, 1]],

    # Small plus with corner block
    [[0, 1, 0],
     [1, 1, 1],
     [0, 1, 1]],

    # Small pyramid
    [[0, 1, 0],
     [1, 1, 1]],

    # Mini Tetris J
    [[1, 0, 0],
     [1, 1, 1]],

    # Mini Tetris reverse J
    [[0, 0, 1],
     [1, 1, 1]],

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

# Create initial 3 blocks
currentblocks = []
for i in range(3):
    shape = block_shapes[random.randint(0, SHAPE_COUNT - 1)]
    color = block_colors[i % len(block_colors)]
    x = MARGIN + i * 150
    y = WINDOW_SIZE + 40
    currentblocks.append(Block(shape, color, x, y))

# Main loop
active_block = None
running = True

while running:
    screen.fill(BG_COLOR)

    # Draw grid background squares
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = MARGIN + col * (SQUARE_SIZE + MARGIN)
            y = MARGIN + row * (SQUARE_SIZE + MARGIN)
            pygame.draw.rect(screen, SQUARE_COLOR, (x, y, SQUARE_SIZE, SQUARE_SIZE))

    # Draw placed blocks on grid
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if grid[row][col]:
                x = MARGIN + col * (SQUARE_SIZE + MARGIN)
                y = MARGIN + row * (SQUARE_SIZE + MARGIN)
                pygame.draw.rect(screen, (200, 200, 200), (x, y, SQUARE_SIZE, SQUARE_SIZE))

    # Draw draggable blocks
    for block in currentblocks:
        block.draw(screen, SQUARE_SIZE, MARGIN)

    # If all blocks placed, spawn new ones
    if len(currentblocks) == 0:
        currentblocks.extend(spawn_blocks(grid, 3))


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

                    # Check game over: no current blocks AND no new block can fit anywhere
                    if len(currentblocks) == 0:
                        game_over = True
                        for shape in block_shapes:
                            if can_block_fit_anywhere(grid, shape):
                                game_over = False
                                break
                        if game_over:
                            print("Game Over!")
                            running = False
                else:
                    # Revert block position if placement fails
                    block.x = block.orig_x
                    block.y = block.orig_y
                active_block = None

    # Display score
    score_surf = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_surf, (10, WINDOW_SIZE + 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
