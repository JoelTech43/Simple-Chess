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
        self.__wood_texture = None #will hold the texture when later loaded/created.

        self.__piece_selected = False 
        self.__selected_coord = (-1, -1)
        self.__target_coords = list() # list of tuples. each tuple contains a tuple and a boolean. tuple is target coord, boolean is special move - true if en passant, castling or pawn promotion as more to do.

        self.__white_turn = True
        self.__move_count = 0 #an overall move counter - pieces store the move_count when they were last moved to tell when they were moved for certain things like en passant.

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
        
        self.__white_turn = True
        self.__move_count = 0
    
    def draw_game(self):
        for i in range(8):
            for j in range(8):
                if (i+j)%2 == 0: #white squares
                    pygame.draw.rect(self.__window, (255,255,255), pygame.Rect(self.__screen_pos[0]+j*self.__square_size, self.__screen_pos[1]+i*self.__square_size, self.__square_size, self.__square_size))
                else:
                    if self.__wood_texture == None: #if wood not loaded
                        self.__wood_texture = pygame.image.load(self.__wood_texture_path).convert()
                        self.__wood_texture = pygame.transform.scale(self.__wood_texture, (self.__square_size, self.__square_size))
                    self.__window.blit(self.__wood_texture, (self.__screen_pos[0]+j*self.__square_size, self.__screen_pos[1]+i*self.__square_size))
        
        for row in self.__board:
            for square in row:
                if square != None:
                    square.draw(self.__window, self.__screen_pos, self.__square_size)
    
    def en_passant_possible(self, coord): #returns a list of targets that can be taken with en passant with the pawn at this coord.
        square = self.__board[coord[1]][coord[0]] #the square of the pawn.
        targets = [] 

        if type(square) == Pawn: #double check it is a pawn
            if square.white and coord[1] == 4: #if white pawn, must be this row as that's where black pawns jump to.
                if coord[0] >= 1: #not on left edge
                    left = (coord[0]-1, coord[1]) #coord to left of pawn
                    left_square = self.__board[left[1]][left[0]]
                    if type(left_square) == Pawn:
                        if left_square.moves == 1 and left_square.last_move_count_moved == self.__move_count-1 and self.__board[coord[1]+1][coord[0]-1] == None: #if left pawn has only moved once, and this was on the previous turn and the space to move into is free.
                            targets.append(((coord[0]-1, coord[1]+1), True)) #adds the coordinate that our pawn will move to, along with a True boolean to flag that it is a special move

                if coord[0] <= 6: #not on right edge
                    right = (coord[0]+1, coord[1]) #coord to right of pawn
                    right_square = self.__board[right[1]][right[0]]
                    if type(right_square) == Pawn:
                        if right_square.moves == 1 and right_square.last_move_count_moved == self.__move_count-1 and self.__board[coord[1]+1][coord[0]+1] == None:
                            targets.append(((coord[0]+1, coord[1]+1), True))
            
            elif (not square.white) and coord[1] == 3: #same checks for black
                if coord[0] >= 1:
                    left = (coord[0]-1, coord[1])
                    left_square = self.__board[left[1]][left[0]]
                    if type(left_square) == Pawn:
                        if left_square.moves == 1 and left_square.last_move_count_moved == self.__move_count-1 and self.__board[coord[1]-1][coord[0]-1] == None:
                            targets.append(((coord[0]-1, coord[1]-1), True))

                if coord[0] <= 6:
                    right = (coord[0]+1, coord[1])
                    right_square = self.__board[right[1]][right[0]]
                    if type(right_square) == Pawn:
                        if right_square.moves == 1 and right_square.last_move_count_moved == self.__move_count-1 and self.__board[coord[1]-1][coord[0]+1] == None:
                            targets.append(((coord[0]+1, coord[1]-1), True))
        return targets

    def castle_possible(self, coord): #returns King target coords if able to castle
        square = self.__board[coord[1]][coord[0]]
        targets = []
        checks = []

        if type(square) == King:
            if square.white: 
                left_rook = self.__board[0][0]
                right_rook = self.__board[0][7]
                if square.moves == 0 and type(left_rook) == Rook and self.__board[0][1] == None and self.__board[0][2] == None: # if left rook is a rook, and king hasn't moved, and spaces between are clear.
                    if left_rook.moves == 0: #if left rook has never moved
                        white_in_check, black_in_check = self.check_4_checks() #process of moving king to each position, checking for checks, and then moving rook (and checking for checks)
                        checks.append(white_in_check)
                        self.__board[0][3], self.__board[0][2] = self.__board[0][2], self.__board[0][3] #move king one to left
                        self.__board[0][2].board_pos = (2,0)
                        white_in_check, black_in_check = self.check_4_checks()
                        checks.append(white_in_check)
                        self.__board[0][2], self.__board[0][1] = self.__board[0][1], self.__board[0][2] #move king one to left
                        self.__board[0][1].board_pos = (1,0)
                        white_in_check, black_in_check = self.check_4_checks()
                        checks.append(white_in_check)
                        self.__board[0][0], self.__board[0][2] = self.__board[0][2], self.__board[0][0] #move rook to position
                        self.__board[0][2].board_pos = (2,0)
                        white_in_check, black_in_check = self.check_4_checks()
                        checks.append(white_in_check)

                        self.__board[0][0], self.__board[0][2] = self.__board[0][2], self.__board[0][0] #move rook to og position
                        self.__board[0][3], self.__board[0][1] = self.__board[0][1], self.__board[0][3] #move king to og position
                        self.__board[0][0].board_pos = (0,0)
                        self.__board[0][3].board_pos = (3,0)

                        if not(True in checks): #if not currently in check and isn't at any subsequent position.
                            targets.append(((1,0), True)) # king final coord, True as is special move.
                
                if square.moves == 0 and type(right_rook) == Rook and self.__board[0][4] == None and self.__board[0][5] == None and self.__board[0][6] == None:
                    if left_rook.moves == 0:
                        white_in_check, black_in_check = self.check_4_checks()
                        checks.append(white_in_check)
                        self.__board[0][3], self.__board[0][4] = self.__board[0][4], self.__board[0][3] #move king one to right
                        self.__board[0][4].board_pos = (4,0)
                        white_in_check, black_in_check = self.check_4_checks()
                        checks.append(white_in_check)
                        self.__board[0][4], self.__board[0][5] = self.__board[0][5], self.__board[0][4] #move king one to right
                        self.__board[0][5].board_pos = (5,0)
                        white_in_check, black_in_check = self.check_4_checks()
                        checks.append(white_in_check)
                        self.__board[0][7], self.__board[0][4] = self.__board[0][4], self.__board[0][7] #move rook to position
                        self.__board[0][4].board_pos = (4,0)
                        white_in_check, black_in_check = self.check_4_checks()
                        checks.append(white_in_check)

                        self.__board[0][7], self.__board[0][4] = self.__board[0][4], self.__board[0][7] #move rook to og position
                        self.__board[0][3], self.__board[0][5] = self.__board[0][5], self.__board[0][3] #move king to og position
                        self.__board[0][7].board_pos = (7,0)
                        self.__board[0][3].board_pos = (3,0)

                        if not(True in checks):
                            targets.append(((5,0), True))
            else:
                left_rook = self.__board[7][0]
                right_rook = self.__board[7][7]
                if square.moves == 0 and type(left_rook) == Rook and self.__board[7][1] == None and self.__board[7][2] == None:
                    if left_rook.moves == 0:
                        white_in_check, black_in_check = self.check_4_checks()
                        checks.append(black_in_check)
                        self.__board[7][3], self.__board[7][2] = self.__board[7][2], self.__board[7][3] #move king one to left
                        self.__board[7][2].board_pos = (2,7)
                        white_in_check, black_in_check = self.check_4_checks()
                        checks.append(black_in_check)
                        self.__board[7][2], self.__board[7][1] = self.__board[7][1], self.__board[7][2] #move king one to left
                        self.__board[7][1].board_pos = (1,7)
                        white_in_check, black_in_check = self.check_4_checks()
                        checks.append(black_in_check)
                        self.__board[7][0], self.__board[7][2] = self.__board[7][2], self.__board[7][0] #move rook to position
                        self.__board[7][2].board_pos = (2,7)
                        white_in_check, black_in_check = self.check_4_checks()
                        checks.append(black_in_check)

                        self.__board[7][0], self.__board[7][2] = self.__board[7][2], self.__board[7][0] #move rook to og position
                        self.__board[7][3], self.__board[7][1] = self.__board[7][1], self.__board[7][3] #move king to og position
                        self.__board[7][0].board_pos = (0,7)
                        self.__board[7][3].board_pos = (3,7)

                        if not(True in checks):
                            targets.append(((1,7), True))
                
                if square.moves == 0 and type(right_rook) == Rook and self.__board[7][4] == None and self.__board[7][5] == None and self.__board[7][6] == None:
                    if left_rook.moves == 0:
                        white_in_check, black_in_check = self.check_4_checks()
                        checks.append(black_in_check)
                        self.__board[7][3], self.__board[7][4] = self.__board[7][4], self.__board[7][3] #move king one to right
                        self.__board[7][4].board_pos = (4,7)
                        white_in_check, black_in_check = self.check_4_checks()
                        checks.append(black_in_check)
                        self.__board[7][4], self.__board[7][5] = self.__board[7][5], self.__board[7][4] #move king one to right
                        self.__board[7][5].board_pos = (5,7)
                        white_in_check, black_in_check = self.check_4_checks()
                        checks.append(black_in_check)
                        self.__board[7][7], self.__board[7][4] = self.__board[7][4], self.__board[7][7] #move rook to position
                        self.__board[7][4].board_pos = (4,7)
                        white_in_check, black_in_check = self.check_4_checks()
                        checks.append(black_in_check)

                        self.__board[7][7], self.__board[7][4] = self.__board[7][4], self.__board[7][7] #move rook to og position
                        self.__board[7][3], self.__board[7][5] = self.__board[7][5], self.__board[7][3] #move king to og position
                        self.__board[7][7].board_pos = (7,7)
                        self.__board[7][3].board_pos = (3,7)

                        if not(True in checks):
                            targets.append(((5,7), True))
        
        return targets

    def screen_coord_2_cell_coord(self, screen_x, screen_y):
        if self.__screen_pos[0]<=screen_x<=self.__screen_pos[0]+self.__size_px and self.__screen_pos[1]<=screen_y<=self.__screen_pos[1]+self.__size_px: #if in board
            rel_screen_x, rel_screen_y = screen_x-self.__screen_pos[0], screen_y-self.__screen_pos[1] #screen position with (0,0) as top left of board
            return (rel_screen_x//self.__square_size, rel_screen_y//self.__square_size) #DIV with square size to get coord.
        else:
            return (-1,-1) #not in board

    def get_target_coords(self, coord, attacking_mode=False): #does not include checking if target would leave own king in check. Normal mode gives all positions pieces can move too. Attacking mode affects pawns as it returns the diagonals they attack (instead of normal moves) even if no pieces are present. Also discounts castling as can't attack.
        square = self.__board[coord[1]][coord[0]]
        white = square.white if square != None else None

        target_coords = []

        if type(square) == Pawn:
            target_coords.extend(self.en_passant_possible(coord))
            if white:
                if 0 <= coord[1] <= 6:
                    if self.__board[coord[1]+1][coord[0]] == None and not attacking_mode:
                        target_coords.append(((coord[0],coord[1]+1), False))
                    if 0 <= coord[0] <= 6:
                        if type(self.__board[coord[1]+1][coord[0]+1]) in (King, Queen, Knight, Bishop, Rook, Pawn):
                            if not self.__board[coord[1]+1][coord[0]+1].white:
                                target_coords.append(((coord[0]+1,coord[1]+1), False))
                        elif attacking_mode:
                            target_coords.append(((coord[0]+1,coord[1]+1), False))
                        
                    if 1 <= coord[0] <= 7:
                        if type(self.__board[coord[1]+1][coord[0]-1]) in (King, Queen, Knight, Bishop, Rook, Pawn):
                            if not self.__board[coord[1]+1][coord[0]-1].white:
                                target_coords.append(((coord[0]-1,coord[1]+1), False))
                        elif attacking_mode:
                            target_coords.append(((coord[0]-1,coord[1]+1), False))
                    
                if 0 <= coord[1] <= 5 and not attacking_mode:
                    if (not square._moved) and self.__board[coord[1]+1][coord[0]] == None:
                        if self.__board[coord[1]+2][coord[0]] == None:
                            target_coords.append(((coord[0],coord[1]+2), False))
            else:
                if 1 <= coord[1] <= 7:
                    if self.__board[coord[1]-1][coord[0]] == None and not attacking_mode:
                        target_coords.append(((coord[0],coord[1]-1), False))
                    if 0 <= coord[0] <= 6:
                        if type(self.__board[coord[1]-1][coord[0]+1]) in (King, Queen, Knight, Bishop, Rook, Pawn):
                            if self.__board[coord[1]-1][coord[0]+1].white:
                                target_coords.append(((coord[0]+1,coord[1]-1), False))
                        elif attacking_mode:
                            target_coords.append(((coord[0]+1,coord[1]-1), False))

                    if 1 <= coord[0] <= 7:
                        if type(self.__board[coord[1]-1][coord[0]-1]) in (King, Queen, Knight, Bishop, Rook, Pawn):
                            if self.__board[coord[1]-1][coord[0]-1].white:
                                target_coords.append(((coord[0]-1,coord[1]-1), False))
                        elif attacking_mode:
                            target_coords.append(((coord[0]-1,coord[1]-1), False))

                if 2 <= coord[1] <= 7 and not attacking_mode:
                    if (not square._moved) and self.__board[coord[1]-1][coord[0]] == None:
                        if self.__board[coord[1]-2][coord[0]] == None:
                            target_coords.append(((coord[0],coord[1]-2), False))
        
        elif type(square) == Rook:
            checking_square_coord = (coord[0], coord[1]+1)
            while checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check below rook
                target_coords.append((checking_square_coord, False))
                checking_square_coord = (checking_square_coord[0], checking_square_coord[1]+1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7:
                if self.__board[checking_square_coord[1]][checking_square_coord[0]].white == (not white):
                    target_coords.append((checking_square_coord, False))
            
            checking_square_coord = (coord[0], coord[1]-1)
            while checking_square_coord[1] >= 0 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check above rook
                target_coords.append((checking_square_coord, False))
                checking_square_coord = (checking_square_coord[0], checking_square_coord[1]-1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7:
                if self.__board[checking_square_coord[1]][checking_square_coord[0]].white == (not white):
                    target_coords.append((checking_square_coord, False))
            
            checking_square_coord = (coord[0]+1, coord[1])
            while checking_square_coord[0] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check to right of rook
                target_coords.append((checking_square_coord, False))
                checking_square_coord = (checking_square_coord[0]+1, checking_square_coord[1])
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7:
                if self.__board[checking_square_coord[1]][checking_square_coord[0]].white == (not white):
                    target_coords.append((checking_square_coord, False))
            
            checking_square_coord = (coord[0]-1, coord[1])
            while checking_square_coord[0] >= 0 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check to left of rook
                target_coords.append((checking_square_coord, False))
                checking_square_coord = (checking_square_coord[0]-1, checking_square_coord[1])
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7:
                if self.__board[checking_square_coord[1]][checking_square_coord[0]].white == (not white):
                    target_coords.append((checking_square_coord, False))
        
        elif type(square) == Bishop:
            checking_square_coord = (coord[0]+1, coord[1]+1)
            while checking_square_coord[1] <= 7 and checking_square_coord[0] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check below-right of bishop
                target_coords.append((checking_square_coord, False))
                checking_square_coord = (checking_square_coord[0]+1, checking_square_coord[1]+1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7:
                if self.__board[checking_square_coord[1]][checking_square_coord[0]].white == (not white):
                    target_coords.append((checking_square_coord, False))
            
            checking_square_coord = (coord[0]+1, coord[1]-1)
            while checking_square_coord[1] >= 0 and checking_square_coord[0] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check above-right of bishop
                target_coords.append((checking_square_coord, False))
                checking_square_coord = (checking_square_coord[0]+1, checking_square_coord[1]-1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7:
                if self.__board[checking_square_coord[1]][checking_square_coord[0]].white == (not white):
                    target_coords.append((checking_square_coord, False))
            
            checking_square_coord = (coord[0]-1, coord[1]+1)
            while checking_square_coord[1] <= 7 and checking_square_coord[0] >= 0 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check to below-left of bishop
                target_coords.append((checking_square_coord, False))
                checking_square_coord = (checking_square_coord[0]-1, checking_square_coord[1]+1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7:
                if self.__board[checking_square_coord[1]][checking_square_coord[0]].white == (not white):
                    target_coords.append((checking_square_coord, False))
            
            checking_square_coord = (coord[0]-1, coord[1]-1)
            while checking_square_coord[1] >= 0 and checking_square_coord[0] >= 0 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check to above-left of bishop
                target_coords.append((checking_square_coord, False))
                checking_square_coord = (checking_square_coord[0]-1, checking_square_coord[1]-1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7:
                if self.__board[checking_square_coord[1]][checking_square_coord[0]].white == (not white):
                    target_coords.append((checking_square_coord, False))
        
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
                if 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
                    if (self.__board[target[1]][target[0]] == None or self.__board[target[1]][target[0]].white == (not white)):
                        target_coords.append((target, False))

        elif type(square) == Queen:
            checking_square_coord = (coord[0], coord[1]+1)
            while checking_square_coord[1] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check below rook
                target_coords.append((checking_square_coord, False))
                checking_square_coord = (checking_square_coord[0], checking_square_coord[1]+1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7:
                if self.__board[checking_square_coord[1]][checking_square_coord[0]].white == (not white):
                    target_coords.append((checking_square_coord, False))
            
            checking_square_coord = (coord[0], coord[1]-1)
            while checking_square_coord[1] >= 0 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check above rook
                target_coords.append((checking_square_coord, False))
                checking_square_coord = (checking_square_coord[0], checking_square_coord[1]-1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7:
                if self.__board[checking_square_coord[1]][checking_square_coord[0]].white == (not white):
                    target_coords.append((checking_square_coord, False))
            
            checking_square_coord = (coord[0]+1, coord[1])
            while checking_square_coord[0] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check to right of rook
                target_coords.append((checking_square_coord, False))
                checking_square_coord = (checking_square_coord[0]+1, checking_square_coord[1])
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7:
                if self.__board[checking_square_coord[1]][checking_square_coord[0]].white == (not white):
                    target_coords.append((checking_square_coord, False))
            
            checking_square_coord = (coord[0]-1, coord[1])
            while checking_square_coord[0] >= 0 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check to left of rook
                target_coords.append((checking_square_coord, False))
                checking_square_coord = (checking_square_coord[0]-1, checking_square_coord[1])
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7:
                if self.__board[checking_square_coord[1]][checking_square_coord[0]].white == (not white):
                    target_coords.append((checking_square_coord, False))
            
            checking_square_coord = (coord[0]+1, coord[1]+1)
            while checking_square_coord[1] <= 7 and checking_square_coord[0] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check below-right of bishop
                target_coords.append((checking_square_coord, False))
                checking_square_coord = (checking_square_coord[0]+1, checking_square_coord[1]+1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7:
                if self.__board[checking_square_coord[1]][checking_square_coord[0]].white == (not white):
                    target_coords.append((checking_square_coord, False))
            
            checking_square_coord = (coord[0]+1, coord[1]-1)
            while checking_square_coord[1] >= 0 and checking_square_coord[0] <= 7 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check above-right of bishop
                target_coords.append((checking_square_coord, False))
                checking_square_coord = (checking_square_coord[0]+1, checking_square_coord[1]-1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7:
                if self.__board[checking_square_coord[1]][checking_square_coord[0]].white == (not white):
                    target_coords.append((checking_square_coord, False))
            
            checking_square_coord = (coord[0]-1, coord[1]+1)
            while checking_square_coord[1] <= 7 and checking_square_coord[0] >= 0 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check to below-left of bishop
                target_coords.append((checking_square_coord, False))
                checking_square_coord = (checking_square_coord[0]-1, checking_square_coord[1]+1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7:
                if self.__board[checking_square_coord[1]][checking_square_coord[0]].white == (not white):
                    target_coords.append((checking_square_coord, False))
            
            checking_square_coord = (coord[0]-1, coord[1]-1)
            while checking_square_coord[1] >= 0 and checking_square_coord[0] >= 0 and self.__board[checking_square_coord[1]][checking_square_coord[0]] == None: #check to above-left of bishop
                target_coords.append((checking_square_coord, False))
                checking_square_coord = (checking_square_coord[0]-1, checking_square_coord[1]-1)
            if 0 <= checking_square_coord[0] <= 7 and 0 <= checking_square_coord[1] <= 7:
                if self.__board[checking_square_coord[1]][checking_square_coord[0]].white == (not white):
                    target_coords.append((checking_square_coord, False))
        
        elif type(square) == King:
            if not attacking_mode:
                target_coords.extend(self.castle_possible(coord))
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
                if 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
                    if (self.__board[target[1]][target[0]] == None or self.__board[target[1]][target[0]].white == (not white)):
                        target_coords.append((target, False))
        
        return target_coords

    def handle_mouse_click(self, mouse_x, mouse_y):
        cell_coord = self.screen_coord_2_cell_coord(mouse_x, mouse_y)
        if self.__piece_selected:
            actual_targets = [a[0] for a in self.__target_coords]
            selected_square = self.__board[self.__selected_coord[1]][self.__selected_coord[0]]
            if cell_coord in actual_targets:
                ind = actual_targets.index(cell_coord)

                if self.__target_coords[ind][1] == False: #if not a special move.
                    temp = self.__board[cell_coord[1]][cell_coord[0]]
                    self.__board[cell_coord[1]][cell_coord[0]] = self.__board[self.__selected_coord[1]][self.__selected_coord[0]]
                    self.__board[self.__selected_coord[1]][self.__selected_coord[0]] = None
                    self.__board[cell_coord[1]][cell_coord[0]].board_pos = cell_coord
                    self.__board[cell_coord[1]][cell_coord[0]].moves += 1
                    temp_move_count = self.__board[cell_coord[1]][cell_coord[0]].last_move_count_moved
                    self.__board[cell_coord[1]][cell_coord[0]].last_move_count_moved = self.__move_count
                    self.__white_turn = not self.__white_turn
                    self.__move_count += 1

                    white_in_check, black_in_check = self.check_4_checks()
                    if (not self.__white_turn and white_in_check) or ((self.__white_turn) and black_in_check): #look at not self.__white_turn when looking if white is in check as it is switched to black's turn as soon as white move made so if it is black's turn, white must have just moved. Vice versa for black.
                        self.__board[self.__selected_coord[1]][self.__selected_coord[0]] = self.__board[cell_coord[1]][cell_coord[0]]
                        self.__board[self.__selected_coord[1]][self.__selected_coord[0]].board_pos = self.__selected_coord
                        self.__board[self.__selected_coord[1]][self.__selected_coord[0]].moves -= 1
                        self.__board[self.__selected_coord[1]][self.__selected_coord[0]].last_move_count_moved = temp_move_count
                        self.__board[cell_coord[1]][cell_coord[0]] = temp
                        self.__white_turn = not self.__white_turn
                        self.__move_count -= 1
                
                elif type(selected_square) == Pawn:
                    if self.__white_turn:
                        if cell_coord[1] == 7:
                            ... #white pawn promotion
                        else:
                            pawn = self.__board[self.__selected_coord[1]][self.__selected_coord[0]]
                            other = self.__board[cell_coord[1]-1][cell_coord[0]]
                            self.__board[cell_coord[1]][cell_coord[0]] = pawn
                            self.__board[self.__selected_coord[1]][self.__selected_coord[0]] = None
                            self.__board[cell_coord[1]-1][cell_coord[0]] = None
                            self.__board[cell_coord[1]][cell_coord[0]].board_pos = cell_coord
                            self.__board[cell_coord[1]][cell_coord[0]].moves += 1
                            temp_move_count = self.__board[cell_coord[1]][cell_coord[0]].last_move_count_moved
                            self.__board[cell_coord[1]][cell_coord[0]].last_move_count_moved = self.__move_count
                            self.__white_turn = not self.__white_turn
                            self.__move_count += 1

                            white_in_check, black_in_check = self.check_4_checks()
                            if (not self.__white_turn) and white_in_check:
                                self.__board[self.__selected_coord[1]][self.__selected_coord[0]] = pawn
                                self.__board[cell_coord[1]-1][cell_coord[0]] = other
                                self.__board[cell_coord[1]][cell_coord[0]] = None
                                self.__board[self.__selected_coord[1]][self.__selected_coord[0]].board_pos = cell_coord
                                self.__board[self.__selected_coord[1]][self.__selected_coord[0]].moves -= 1
                                self.__board[self.__selected_coord[1]][self.__selected_coord[0]].last_move_count_moved = temp_move_count
                                self.__white_turn = not self.__white_turn
                                self.__move_count -= 1
                            
                    else:
                        if cell_coord[1] == 0:
                            ... #black pawn promotion
                        else:
                            pawn = self.__board[self.__selected_coord[1]][self.__selected_coord[0]]
                            other = self.__board[cell_coord[1]+1][cell_coord[0]]
                            self.__board[cell_coord[1]][cell_coord[0]] = pawn
                            self.__board[self.__selected_coord[1]][self.__selected_coord[0]] = None
                            self.__board[cell_coord[1]+1][cell_coord[0]] = None
                            self.__board[cell_coord[1]][cell_coord[0]].board_pos = cell_coord
                            self.__board[cell_coord[1]][cell_coord[0]].moves += 1
                            temp_move_count = self.__board[cell_coord[1]][cell_coord[0]].last_move_count_moved
                            self.__board[cell_coord[1]][cell_coord[0]].last_move_count_moved = self.__move_count
                            self.__white_turn = not self.__white_turn
                            self.__move_count += 1

                            white_in_check, black_in_check = self.check_4_checks()
                            if self.__white_turn and black_in_check:
                                self.__board[self.__selected_coord[1]][self.__selected_coord[0]] = pawn
                                self.__board[cell_coord[1]+1][cell_coord[0]] = other
                                self.__board[cell_coord[1]][cell_coord[0]] = None
                                self.__board[self.__selected_coord[1]][self.__selected_coord[0]].board_pos = cell_coord
                                self.__board[self.__selected_coord[1]][self.__selected_coord[0]].moves -= 1
                                self.__board[self.__selected_coord[1]][self.__selected_coord[0]].last_move_count_moved = temp_move_count
                                self.__white_turn = not self.__white_turn
                                self.__move_count -= 1
                
                elif type(selected_square) == King:
                    if self.__white_turn:
                        if cell_coord[0] == 1:
                            self.__board[0][3], self.__board[0][1] = self.__board[0][1], self.__board[0][3]
                            self.__board[0][1].board_pos = (1,0)
                            self.__board[0][1].moves += 1
                            self.__board[0][1].last_move_count_moved = self.__move_count

                            self.__board[0][0], self.__board[0][2] = self.__board[0][2], self.__board[0][0]
                            self.__board[0][2].board_pos = (2,0)
                            self.__board[0][2].moves += 1
                            self.__board[0][2].last_move_count_moved = self.__move_count

                            self.__white_turn = not self.__white_turn
                            self.__move_count += 1
                        else:
                            self.__board[0][3], self.__board[0][5] = self.__board[0][5], self.__board[0][3]
                            self.__board[0][5].board_pos = (5,0)
                            self.__board[0][5].moves += 1
                            self.__board[0][5].last_move_count_moved = self.__move_count

                            self.__board[0][7], self.__board[0][4] = self.__board[0][4], self.__board[0][7]
                            self.__board[0][4].board_pos = (4,0)
                            self.__board[0][4].moves += 1
                            self.__board[0][4].last_move_count_moved = self.__move_count

                            self.__white_turn = not self.__white_turn
                            self.__move_count += 1
                    else:
                        if cell_coord[0] == 1:
                            self.__board[7][3], self.__board[7][1] = self.__board[7][1], self.__board[7][3]
                            self.__board[7][1].board_pos = (1,7)
                            self.__board[7][1].moves += 1
                            self.__board[7][1].last_move_count_moved = self.__move_count

                            self.__board[7][0], self.__board[7][2] = self.__board[7][2], self.__board[7][0]
                            self.__board[7][2].board_pos = (2,7)
                            self.__board[7][2].moves += 1
                            self.__board[7][2].last_move_count_moved = self.__move_count

                            self.__white_turn = not self.__white_turn
                            self.__move_count += 1
                        else:
                            self.__board[7][3], self.__board[7][5] = self.__board[7][5], self.__board[7][3]
                            self.__board[7][5].board_pos = (5,7)
                            self.__board[7][5].moves += 1
                            self.__board[7][5].last_move_count_moved = self.__move_count

                            self.__board[7][7], self.__board[7][4] = self.__board[7][4], self.__board[7][7]
                            self.__board[7][4].board_pos = (4,7)
                            self.__board[7][4].moves += 1
                            self.__board[7][4].last_move_count_moved = self.__move_count

                            self.__white_turn = not self.__white_turn
                            self.__move_count += 1

            self.__piece_selected = False
            self.__selected_coord = (-1, -1)
            self.__target_coords.clear()
            
        else:
            square = self.__board[cell_coord[1]][cell_coord[0]]
            if square != None:
                if square.white and self.__white_turn:
                    self.__piece_selected = True
                    self.__selected_coord = cell_coord
                    self.__target_coords = self.get_target_coords(cell_coord)
                elif (not square.white) and (not self.__white_turn):
                    self.__piece_selected = True
                    self.__selected_coord = cell_coord
                    self.__target_coords = self.get_target_coords(cell_coord)

    def get_board(self):
        return self.__board

    def check_4_checkmates(self, last_turn_white):
        
        #check if any move can block/evade check
        checkmate = True

        for row in self.__board:
            for square in row:
                if square in [King, Queen, Rook, Knight, Bishop, Pawn]:
                    if square.white != last_turn_white:
                        target_coords = self.get_target_coords(square.board_pos)
                        for coord, special in target_coords:
                            if not special and checkmate:
                                temp = self.__board[coord[1]][coord[0]]
                                self.__board[coord[1]][coord[0]] = self.__board[square.board_pos]
                                self.__board[square.board_pos] = None
                                white_in_check, black_in_check = self.check_4_checks()
                                if (last_turn_white and not black_in_check) or (not last_turn_white and not white_in_check):
                                    checkmate = False
                                self.__board[square.board_pos] = self.__board[coord[1]][coord[0]]
                                self.__board[coord[1]][coord[0]] = temp
                            elif square in [Pawn] and special and not square.get_moved() and checkmate:
                                if square.white:
                                    if square.coord[1] == 7:
                                        ... #promotion
                                    else:
                                        pawn = self.__board[square.board_pos[1]][square.board_pos[0]]
                                        other = self.__board[coord[1]-1][coord[0]]
                                        self.__board[coord[1]][coord[0]] = pawn
                                        self.__board[square.board_pos[1]][square.board_pos[0]] = None
                                        self.__board[coord[1]-1][coord[0]] = None
                                        if (last_turn_white and not black_in_check) or (not last_turn_white and not white_in_check):
                                            checkmate = False
                                        self.__board[square.board_pos[1]][square.board_pos[0]] = pawn
                                        self.__board[coord[1]-1][coord[0]] = other
                                        self.__board[coord[1]][coord[0]] = None
                                else:
                                    if square.coord[1] == 0:
                                        ... #promotion
                                    else:
                                        pawn = self.__board[square.board_pos[1]][square.board_pos[0]]
                                        other = self.__board[coord[1]+1][coord[0]]
                                        self.__board[coord[1]][coord[0]] = pawn
                                        self.__board[square.board_pos[1]][square.board_pos[0]] = None
                                        self.__board[coord[1]+1][coord[0]] = None
                                        if (last_turn_white and not black_in_check) or (not last_turn_white and not white_in_check):
                                            checkmate = False
                                        self.__board[square.board_pos[1]][square.board_pos[0]] = pawn
                                        self.__board[coord[1]+1][coord[0]] = other
                                        self.__board[coord[1]][coord[0]] = None

        return 
    
    def check_4_checks(self):
        white_king_coord = None
        black_king_coord = None

        white_target_coords = set() #set of coordinates that white pieces are targetting
        black_target_coords = set() #set of coords that black pieces are targetting
        for row in self.get_board():
            for square in row:
                if type(square) == King:
                    if square.white:
                        white_king_coord = square.board_pos
                        white_target_coords.update(self.get_target_coords(square.board_pos, attacking_mode=True))
                    else:
                        black_king_coord = square.board_pos
                        black_target_coords.update(self.get_target_coords(square.board_pos, attacking_mode=True))
                elif type(square) in [Queen, Knight, Bishop, Rook, Pawn]:
                    if square.white:
                        white_target_coords.update(self.get_target_coords(square.board_pos, attacking_mode=True))
                    else:
                        black_target_coords.update(self.get_target_coords(square.board_pos, attacking_mode=True))

        # return white_king_coord in black_target_coords, black_king_coord in white_target_coords
        return any(black_target_coord == white_king_coord for black_target_coord, _ in black_target_coords), any(white_target_coord == black_king_coord for white_target_coord, _ in white_target_coords)