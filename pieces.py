from pathlib import Path
import pygame

CWD = Path.cwd()
ASSETS = CWD / "assets"

class Piece:
    def __init__(self, white, start_pos):
        self.white = white
        self._colour = "white" if white else "black"
        self._captured = False
        self._moved = False
        self.board_pos = start_pos
        self._IMAGE_PATH = ASSETS/f"{self._colour}-pawn.png"
        self._image = None

        self.moves = 0
        self.last_move_count_moved = -1
    
    def draw(self, window, board_screen_pos, square_size):
        x_pos = board_screen_pos[0] + self.board_pos[0]*square_size
        y_pos = board_screen_pos[1] + self.board_pos[1]*square_size
        if self._image == None:
            self._image = pygame.image.load(self._IMAGE_PATH).convert_alpha()
            self._image = pygame.transform.scale(self._image, (square_size, square_size))
        
        window.blit(self._image, (x_pos, y_pos))

class Pawn(Piece):
    def __init__(self, white, start_pos):
        super().__init__(white, start_pos)
        self.en_passant_possible = False

class Rook(Piece):
    def __init__(self, white, start_pos):
        super().__init__(white, start_pos)
        self._IMAGE_PATH = ASSETS/f"{self._colour}-rook.png"

class Knight(Piece):
    def __init__(self, white, start_pos):
        super().__init__(white, start_pos)
        self._IMAGE_PATH = ASSETS/f"{self._colour}-knight.png"

class Bishop(Piece):
    def __init__(self, white, start_pos):
        super().__init__(white, start_pos)
        self._IMAGE_PATH = ASSETS/f"{self._colour}-bishop.png"

class Queen(Piece):
    def __init__(self, white, start_pos):
        super().__init__(white, start_pos)
        self._IMAGE_PATH = ASSETS/f"{self._colour}-queen.png"

class King(Piece):
    def __init__(self, white, start_pos):
        super().__init__(white, start_pos)
        self._IMAGE_PATH = ASSETS/f"{self._colour}-king.png"