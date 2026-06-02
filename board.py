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
        self.__white_pieces = []
        self.__black_pieces = []
        self.__window = window
        self.__wood_texture_path = ASSETS/"wood.png"
        self.__wood_texture = None

    def set_pieces(self):
        self.__white_pieces = [
            Rook("white", (0,0)),
            Knight("white", (1,0)),
            Bishop("white", (2,0)),
            King("white", (3,0)),
            Queen("white", (4,0)),
            Bishop("white", (5,0)),
            Knight("white", (6,0)),
            Rook("white", (7,0))
        ] + [Pawn("white", (i,1)) for i in range(8)]
        self.__black_pieces = [
            Rook("black", (0,7)),
            Knight("black", (1,7)),
            Bishop("black", (2,7)),
            King("black", (3,7)),
            Queen("black", (4,7)),
            Bishop("black", (5,7)),
            Knight("black", (6,7)),
            Rook("black", (7,7))
        ] + [Pawn("black", (i,6)) for i in range(8)]
    
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
        
        for piece in self.__white_pieces+self.__black_pieces:
            piece.draw(self.__window, self.__screen_pos, self.__square_size)

