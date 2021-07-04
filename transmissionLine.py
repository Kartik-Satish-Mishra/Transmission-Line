import pygame, TL_Classes, os, sys
from pygame.locals import *
from pygame.time import delay

img_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
def get_file(file):
    return os.path.abspath(os.path.join(img_dir, "img", file))

pygame.init()
s_size = (1000, 600)
cell_size = (100, 100)
screen = pygame.display.set_mode(s_size)
font = pygame.font.Font('freesansbold.ttf', 32)

start_bg = pygame.transform.scale(
    pygame.image.load(get_file("frame.png")).convert(),
    s_size
)

start_button = pygame.transform.scale(
    pygame.image.load(get_file("start.jpg")).convert(),
    (200, 120)
)
button_rect = start_button.get_rect()
button_rect.center = (500, 400)

pygame.display.set_caption(get_file("idhar"))

stage_1 = [
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1,  0, -1, -1, -1, -1, -1, -1,  1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    ]

level = TL_Classes.level({
    'stage': stage_1,
    'modulation_technique': 'PAM',
    'frequency': 1*10**3,
    'signal_strength': 14,
    'cost_limit': 200,
    'menu_bar': [2, 3],
    'screen': screen
    })

running = True
object_select = None

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif level.current_frame == 'start':
            if event.type == MOUSEBUTTONDOWN and 420 < event.pos[0] < 580 and 370 < event.pos[1] < 432:
                level.current_frame = 'level'

        elif level.current_frame == 'level':
            if event.type == MOUSEBUTTONDOWN:
                object_select = level.select_block(event.pos)

            elif event.type == MOUSEBUTTONUP and object_select:
                level.update_tile(
                    event.pos[1]//100, event.pos[0]//100, object_select)
                object_select = None
                level.update_cost()

        elif level.current_frame == 'output':
            if event.type == MOUSEBUTTONDOWN:
                level.current_frame = 'level'


    if level.current_frame == 'start':

        screen.blit(start_bg, (0, 0))

        text = font.render('Transmission Line', True, '#27272b')
        text_rect = text.get_rect()
        text_rect.center = (500, 200)
        screen.blit(text, text_rect)

        text = font.render('click start button below to play the game', True, '#0373fc')
        text_rect = text.get_rect()
        text_rect.center = (500, 280)
        screen.blit(text, text_rect)

        screen.blit(start_button, button_rect)

    elif level.current_frame == 'level':
        screen.fill('#00ff00')
        for row in range(level.rows):
            for column in range(level.columns):
                if level.stage[row][column] == -1:
                    continue
                else:
                    screen.blit(level.stage[row][column].image,
                                (100*column, 100*row)
                                )

        if event.type == MOUSEMOTION and object_select:
            screen.blit(TL_Classes.class_list[object_select]().image,
                        (event.pos[0]-(cell_size[0]//2),
                         event.pos[1]-(cell_size[1]//2))
                        )
        level.display_menu()

    elif level.current_frame == 'output':
        level.display_output()

    pygame.display.update()
    delay(25)
pygame.quit()

#