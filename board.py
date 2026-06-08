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
        self.__board[0][0] = Rook(True, (0,0))
        self.__board[0][1] = Knight(True, (1,0))
        self.__board[0][2] = Bishop(True, (2,0))
        self.__board[0][3] = King(True, (3,0))
        self.__board[0][4] = Queen(True, (4,0))
        self.__board[0][5] = Bishop(True, (5,0))
        self.__board[0][6] = Knight(True, (6,0))
        self.__board[0][7] = Rook(True, (7,0))
        for i in range(8):
            self.__board[1][i] = Pawn(True, (i,1))

        self.__board[7][0] = Rook(False, (0,7))
        self.__board[7][1] = Knight(False, (1,7))
        self.__board[7][2] = Bishop(False, (2,7))
        self.__board[7][3] = King(False, (3,7))
        self.__board[7][4] = Queen(False, (4,7))
        self.__board[7][5] = Bishop(False, (5,7))
        self.__board[7][6] = Knight(False, (6,7))
        self.__board[7][7] = Rook(False, (7,7))
        for i in range(8):
            self.__board[6][i] = Pawn(False, (i,6))
    
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
    
    def screen_coord_2_cell_coord(self, screen_x, screen_y):
        if self.__screen_pos[0]<=screen_x<=self.__screen_pos[0]+self.__size_px and self.__screen_pos[1]<=screen_y<=self.__screen_pos[1]+self.__size_px:
            rel_screen_x, rel_screen_y = screen_x-self.__screen_pos[0], screen_y-self.__screen_pos[1]
            return (rel_screen_x//self.__square_size, rel_screen_y//self.__square_size)
        else:
            return (-1,-1)

    def get_target_coords(self, coord): #does not include checking if target would leave own king in check
        square = self.__board[coord[1]][coord[0]]
        white = square._white if square != None else None

        target_coords = []
        if type(square) == Pawn:
            if white:
                target_coords.append((square._board_pos[0],square._board_pos[1]+1))
                if square._board_pos == square._START_BOARD_POS:
                    target_coords.append((square._board_pos[0],square._board_pos[1]+2))
            else:
                target_coords.append((square._board_pos[0],square._board_pos[1]-1))
                if square._board_pos == square._START_BOARD_POS:
                    target_coords.append((square._board_pos[0],square._board_pos[1]-2))
        
        elif type(square) == Rook:
            checking_square_coord = (coord[0], coord[1]+1)
            while checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check below rook
                target_coords.append(checking_square_coord)
                checking_square_coord = (checking_square_coord[0], checking_square_coord[1]+1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]]._white == (not white):
                target_coords.append(checking_square_coord)
            
            checking_square_coord = (coord[0], coord[1]-1)
            while checking_square_coord[1] >= 0 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check above rook
                target_coords.append(checking_square_coord)
                checking_square_coord = (checking_square_coord[0], checking_square_coord[1]-1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]]._white == (not white):
                target_coords.append(checking_square_coord)
            
            checking_square_coord = (coord[0]+1, coord[1])
            while checking_square_coord[0] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check to right of rook
                target_coords.append(checking_square_coord)
                checking_square_coord = (checking_square_coord[0]+1, checking_square_coord[1])
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]]._white == (not white):
                target_coords.append(checking_square_coord)
            
            checking_square_coord = (coord[0]-1, coord[1])
            while checking_square_coord[0] >= 0 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check to left of rook
                target_coords.append(checking_square_coord)
                checking_square_coord = (checking_square_coord[0]-1, checking_square_coord[1])
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]]._white == (not white):
                target_coords.append(checking_square_coord)
        
        elif type(square) == Bishop:
            checking_square_coord = (coord[0]+1, coord[1]+1)
            while checking_square_coord[1] <= 7 and checking_square_coord[0] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check below-right of bishop
                target_coords.append(checking_square_coord)
                checking_square_coord = (checking_square_coord[0]+1, checking_square_coord[1]+1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]]._white == (not white):
                target_coords.append(checking_square_coord)
            
            checking_square_coord = (coord[0]+1, coord[1]-1)
            while checking_square_coord[1] >= 0 and checking_square_coord[0] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check above-right of bishop
                target_coords.append(checking_square_coord)
                checking_square_coord = (checking_square_coord[0]+1, checking_square_coord[1]-1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]]._white == (not white):
                target_coords.append(checking_square_coord)
            
            checking_square_coord = (coord[0]-1, coord[1]+1)
            while checking_square_coord[1] <= 7 and checking_square_coord[0] >= 0 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check to below-left of bishop
                target_coords.append(checking_square_coord)
                checking_square_coord = (checking_square_coord[0]-1, checking_square_coord[1]+1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]]._white == (not white):
                target_coords.append(checking_square_coord)
            
            checking_square_coord = (coord[0]-1, coord[1]-1)
            while checking_square_coord[1] >= 0 and checking_square_coord[0] >= 0 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check to above-left of bishop
                target_coords.append(checking_square_coord)
                checking_square_coord = (checking_square_coord[0]-1, checking_square_coord[1]-1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]]._white == (not white):
                target_coords.append(checking_square_coord)
        
        elif type(square) == Knight:
            targets = [
                (coord[0]-2, coord[1]-1),
                (coord[0]-2, coord[1]+1),
                (coord[0]+2, coord[1]-1),
                (coord[0]+2, coord[1]+1),
                (coord[0]-1, coord[1]-2),
                (coord[0]+1, coord[1]-2),
                (coord[0]-1, coord[1]+2),
                (coord[0]+1, coord[1]+2),
                ]
            
            for target in targets:
                if 0 <= target[0] <= 8 and 0 <= target[1] <= 8 and (self.__board[target[1]][target[0]] == None or self.__board[target[1]][target[0]]._white == (not white)):
                    target_coords.append(target)

        elif type(square) == Queen:
            checking_square_coord = (coord[0], coord[1]+1)
            while checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check below rook
                target_coords.append(checking_square_coord)
                checking_square_coord = (checking_square_coord[0], checking_square_coord[1]+1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]]._white == (not white):
                target_coords.append(checking_square_coord)
            
            checking_square_coord = (coord[0], coord[1]-1)
            while checking_square_coord[1] >= 0 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check above rook
                target_coords.append(checking_square_coord)
                checking_square_coord = (checking_square_coord[0], checking_square_coord[1]-1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]]._white == (not white):
                target_coords.append(checking_square_coord)
            
            checking_square_coord = (coord[0]+1, coord[1])
            while checking_square_coord[0] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check to right of rook
                target_coords.append(checking_square_coord)
                checking_square_coord = (checking_square_coord[0]+1, checking_square_coord[1])
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]]._white == (not white):
                target_coords.append(checking_square_coord)
            
            checking_square_coord = (coord[0]-1, coord[1])
            while checking_square_coord[0] >= 0 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check to left of rook
                target_coords.append(checking_square_coord)
                checking_square_coord = (checking_square_coord[0]-1, checking_square_coord[1])
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]]._white == (not white):
                target_coords.append(checking_square_coord)
            
            checking_square_coord = (coord[0]+1, coord[1]+1)
            while checking_square_coord[1] <= 7 and checking_square_coord[0] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check below-right of bishop
                target_coords.append(checking_square_coord)
                checking_square_coord = (checking_square_coord[0]+1, checking_square_coord[1]+1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]]._white == (not white):
                target_coords.append(checking_square_coord)
            
            checking_square_coord = (coord[0]+1, coord[1]-1)
            while checking_square_coord[1] >= 0 and checking_square_coord[0] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check above-right of bishop
                target_coords.append(checking_square_coord)
                checking_square_coord = (checking_square_coord[0]+1, checking_square_coord[1]-1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]]._white == (not white):
                target_coords.append(checking_square_coord)
            
            checking_square_coord = (coord[0]-1, coord[1]+1)
            while checking_square_coord[1] <= 7 and checking_square_coord[0] >= 0 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check to below-left of bishop
                target_coords.append(checking_square_coord)
                checking_square_coord = (checking_square_coord[0]-1, checking_square_coord[1]+1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]]._white == (not white):
                target_coords.append(checking_square_coord)
            
            checking_square_coord = (coord[0]-1, coord[1]-1)
            while checking_square_coord[1] >= 0 and checking_square_coord[0] >= 0 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check to above-left of bishop
                target_coords.append(checking_square_coord)
                checking_square_coord = (checking_square_coord[0]-1, checking_square_coord[1]-1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]]._white == (not white):
                target_coords.append(checking_square_coord)
        
        elif type(square) == King:
            targets = [
                (coord[0]-1, coord[1]-1),
                (coord[0]-1, coord[1]),
                (coord[0]-1, coord[1]+1),
                (coord[0], coord[1]-1),
                (coord[0], coord[1]+1),
                (coord[0]+1, coord[1]-1),
                (coord[0]+1, coord[1]),
                (coord[0]+1, coord[1]+1),
                ]
            
            for target in targets:
                if 0 <= target[0] <= 8 and 0 <= target[1] <= 8 and (self.__board[target[1]][target[0]] == None or self.__board[target[1]][target[0]]._white == (not white)):
                    target_coords.append(target)
        
        return target_coords

    def check_4_checks(self, board=None):
        if board == None:
            board = self.__board
        white_king_coord = None
        black_king_coord = None

        white_target_coords = set() #set of coordinates that white pieces are targetting
        black_target_coords = set() #set of coords that black pieces are targetting
        for row in board:
            for square in row:
                if type(square) == King:
                    if square._white:
                        white_king_coord = square._board_pos
                    else:
                        black_king_coord = square._board_pos
                elif type(square) in [Queen, Knight, Bishop, Rook, Pawn]:
                    if square._white:
                        white_target_coords.update(self.get_target_coords(square._board_pos))
                    else:
                        black_target_coords.update(self.get_target_coords(square._board_pos))
        
        return white_king_coord in black_target_coords, black_king_coord in white_target_coords

    def handle_mouse_click(self, mouse_x, mouse_y):
        #Figure out which cell, check if cell occupied, take relevant action.
        cell_coord = self.screen_coord_2_cell_coord(mouse_x, mouse_y)
        