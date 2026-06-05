from pieces import Pawn, Rook, Knight, Bishop, Queen, King
import pygame
from pathlib import Path

CWD = Path.cwd()
ASSETS = CWD/"assets"

class Board:
    def __init__(self, size_px, screen_pos, window):
        self.__size_px = size_px
        self.__screen_pos = screen_pos
        self.__square_size = size_px//8
        self.__board = [[None for i in range(8)] for j in range(8)]
        self.__window = window
        self.__wood_texture_path = ASSETS/"wood.png"
        self.__wood_texture = None

    def reset_pieces(self):
        self.__board = [[None for i in range(8)] for j in range(8)]
        self.__board[0][0] = Rook("white", (0,0))
        self.__board[0][1] = Knight("white", (1,0))
        self.__board[0][2] = Bishop("white", (2,0))
        self.__board[0][3] = King("white", (3,0))
        self.__board[0][4] = Queen("white", (4,0))
        self.__board[0][5] = Bishop("white", (5,0))
        self.__board[0][6] = Knight("white", (6,0))
        self.__board[0][7] = Rook("white", (7,0))
        for i in range(8):
            self.__board[1][i] = Pawn("white", (i,1))

        self.__board[7][0] = Rook("black", (0,7))
        self.__board[7][1] = Knight("black", (1,7))
        self.__board[7][2] = Bishop("black", (2,7))
        self.__board[7][3] = King("black", (3,7))
        self.__board[7][4] = Queen("black", (4,7))
        self.__board[7][5] = Bishop("black", (5,7))
        self.__board[7][6] = Knight("black", (6,7))
        self.__board[7][7] = Rook("black", (7,7))
        for i in range(8):
            self.__board[6][i] = Pawn("black", (i,6))
    
    def draw_game(self):
        for i in range(8):
            for j in range(8):
                if (i+j)%2 == 0:
                    pygame.draw.rect(self.__window, (255,255,255), pygame.Rect(self.__screen_pos[0]+j*self.__square_size, self.__screen_pos[1]+i*self.__square_size, self.__square_size, self.__square_size))
                else:
                    if self.__wood_texture == None:
                        self.__wood_texture = pygame.image.load(self.__wood_texture_path).convert()
                        self.__wood_texture = pygame.transform.scale(self.__wood_texture, (self.__square_size, self.__square_size))
                    self.__window.blit(self.__wood_texture, (self.__screen_pos[0]+j*self.__square_size, self.__screen_pos[1]+i*self.__square_size))
        
        for row in self.__board:
            for square in row:
                if square != None:
                    square.draw(self.__window, self.__screen_pos, self.__square_size)
    
    def handle_mouse_click(self, mouse_x, mouse_y):
        #Figure out which cell, check if cell occupied, take relevant action.
        pass