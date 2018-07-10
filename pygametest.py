import pygame
from time import sleep


pygame.init()
(display_width, display_height) = (1280, 1040)
screen = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('AV cleanliness super smart mega system 3000')
black = (0,0,0)
white = (255,255,255)
red = (0,0,255)
green = (0,255,0)
screen.fill(black)
pygame.display.flip()

sleep(5)
# running = True
# while running:
#   for event in pygame.event.get():
#     if event.type == pygame.QUIT:
#       running = False

pygame.quit()
quit()
