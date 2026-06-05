import pygame
from board import Board
pygame.init()

board_pos = (20, 20)
board_size = 600

window = pygame.display.set_mode((640,640))
pygame.display.set_caption("Simple Chess")
board = Board(board_size, board_pos, window)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if board_pos[0] <= mouse_x <= board_pos[0]+board_size and board_pos[1] <= mouse_y <= board_pos[1]+board_size: #if click is within board area
                board.handle_mouse_click(mouse_x, mouse_y)
            
    window.fill((0,0,0))
    board.reset_pieces()
    board.draw_game()
    
    pygame.display.flip()