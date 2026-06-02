import pygame
from board import Board
pygame.init()

window = pygame.display.set_mode((640,640))
pygame.display.set_caption("Simple Chess")
board = Board(600, (20,20), window)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    window.fill((0,0,0))
    board.set_pieces()
    board.draw_game()
    
    pygame.display.flip()