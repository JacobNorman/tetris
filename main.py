import pygame
import sys
import random
from itertools import chain
import numpy as np

BACKGROUND_COLOUR = (179, 230, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (102, 204, 102)
YELLOW = (255, 255, 0)
RED = (255, 51, 0)
BLUE = (25, 25, 255)
PINK = (255, 51, 153)
PURPLE = (204, 51, 255)
ORANGE = (255, 102, 51)
COLOURS = [RED, BLUE, PINK, PURPLE, ORANGE, GREEN, YELLOW, BLACK]

# CLASSES --------------------------------------------------------------------------------------------------------------


class Display:
    ''' Class to hold display variables. '''
    def __init__(self, width, height):
        self.size = [width, height]
        self.g_size = [width, 6 * height / 7]
        self.block_size = [self.g_size[0] / 11, self.g_size[1] / 22]
        self.block_spacing = [self.block_size[0] / 11, 2 * self.block_size[1] / 12]


class Tetrimino:
    ''' Class to make block objects that will move down the screen throughout game. '''

    def __init__(self, tetrimino_type, colour):
        self.tetrimino_type = tetrimino_type
        self.colour = COLOURS[colour]
        self.block_positions = []
        self.orientation = 0

    def initialize_tetrimino(self):
        if self.tetrimino_type == 0:  # Square
            self.block_positions = [4, 5, 14, 15]
        if self.tetrimino_type == 1:  # L Shape
            self.block_positions = [6, 14, 15, 16]
        if self.tetrimino_type == 2:  # Zig zag
            self.block_positions = [3, 4, 14, 15]
        if self.tetrimino_type == 3:  # Line
            self.block_positions = [4, 5, 6, 7]
        if self.tetrimino_type == 4:  # T shape
            self.block_positions = [4, 13, 14, 15]

    def move_tetrimino(self, blocks, direction):
        increment = 0
        if direction == "down":
            increment = 10
        elif direction == "left":
            increment = -1
        elif direction == "right":
            increment = 1

        for i in range(0, len(self.block_positions)):
            blocks[self.block_positions[i]].colour = BACKGROUND_COLOUR
            self.block_positions[i] += increment
        for i in range(0, len(self.block_positions)):
            blocks[self.block_positions[i]].colour = self.colour

    def check_for_edge(self, tetrimino_to_check, edge_to_check):
        ''' Checks if there is space either left, right or below a tetrimino to move and returns False if there is no space and True otherwise'''
        for position in self.block_positions:

            # Check for surface edges
            if edge_to_check == 'l' and position % 10 == 0:
                return True
            if edge_to_check == 'r' and position % 10 == 9:
                return True
            if edge_to_check == 'b' and position + 10 > 199:
                return True
        
            # Check for other tetriminos
            for tetrimino in tetrimino_to_check[:-1]:
                if edge_to_check == 'l' and any(position - 1 == entree for entree in tetrimino.block_positions):
                    return True
                if edge_to_check == 'r' and any(position + 1 == entree for entree in tetrimino.block_positions):
                    return True
                if edge_to_check == 'b' and any(position + 10 == entree for entree in tetrimino.block_positions):
                    return True

    def rotate_tetrimino(self, background):

        with open(r'C:\Users\jaken\PycharmProjects\tetris\block_info.txt', 'r') as reader:
            tetrimino_rotations = np.asarray([line.split() for line in reader]).reshape([5, 4, 4]).astype(int)

        for position in self.block_positions:
            background[position].colour = BACKGROUND_COLOUR

        for i in range(0, 4):
            self.block_positions[i] += tetrimino_rotations[self.tetrimino_type, self.orientation, i]
        self.orientation = (1 + self.orientation) % 4

        for position in self.block_positions:
            background[position].colour = self.colour

    def remove_blocks(self, positions_to_remove, all_tetriminos):
        line_numbers = np.unique(np.asarray([position // 10 for position in positions_to_remove]))
        for line_number in line_numbers:

            line = [line_number * 10 + i for i in range(0, 10)]
            tetrimino_positions = self.block_positions
            tetrimino_positions = [pos for pos in tetrimino_positions if pos not in line]

            # If blocks at the top or bottom of a tetrimino need to be removed, these can be removed as expected. If
            # blocks are in the middle of a tetrimino, the tetrimino is split and a new tetrimino object is created.
            
            if tetrimino_positions == []:
                return True
            elif all([position // 10 >= line_number for position in tetrimino_positions]) or all([position // 10 <= line_number for position in tetrimino_positions]):
                self.block_positions = tetrimino_positions
                return False
            else:
                self.block_positions = [tetrimino_position for tetrimino_position in tetrimino_positions if
                                        tetrimino_position // 10 > line_number]
                all_tetriminos.append(Tetrimino("partial", COLOURS.index(self.colour)))
                all_tetriminos[-1].block_positions = [tetrimino_position for tetrimino_position in tetrimino_positions
                                                      if tetrimino_position // 10 < line_number]
                return False


class BackgroundBlocks:
    ''' Class to make background blocks.'''
    def __init__(self, colour, position, size):
        self.colour = colour
        self.position = position
        self.size = size

    def draw_block(self):
        # pygame.draw.rect(window, self.colour, (int(self.position[0]), int(self.position[1]), int(self.size[0]),
        #                                        int(self.size[1])))
        draw_round_rect(window, self.colour, pygame.Rect(int(self.position[0]), int(self.position[1]),
                                                         int(self.size[0]), int(self.size[1])), 0, 2, 2)


class MenuText:
    def __init__(self, text, colour, position, font, size):
        self.colour = colour
        self.position = position
        self.size = size
        self.font = font
        self.font_object = pygame.font.SysFont(self.font, self.size, True)
        self.text = text
        self.text_object = self.font_object.render(self.text, 1, self.colour)
        self.box = self.text_object.get_rect(center=self.position)

    def display_text(self):
        self.font_object = pygame.font.SysFont(self.font, self.size, True)
        self.text_object = self.font_object.render(self.text, 1, self.colour)
        self.text_object = self.font_object.render(self.text, 1, self.colour)
        window.blit(self.text_object, self.box)
        return


class GameMode:
    def __init__(self, difficulty):
        self.difficulty = "Easy"
        self.time_delay = 500
        self.multiplier = 1

    def change_difficulty(self, difficulty):

        self.difficulty = difficulty

        if difficulty == "Easy":
            self.time_delay = 500
            self.multiplier = 1
        elif difficulty == "Hard":
            self.time_delay = 250
            self.multiplier = 3
        elif difficulty == "Insane":
            self.time_delay = 70
            self.multiplier = 5


# PROCESS FUNCTIONS ----------------------------------------------------------------------------------------------------

def make_blocks():
    blocks_list = []

    for j in range(0, 20):
        for i in range(0, 10):
            blocks_list.append(BackgroundBlocks(BACKGROUND_COLOUR, (display.block_spacing[0]
                                                                    + i * (display.block_spacing[0]
                                                                           + display.block_size[0]),
                                                                    display.block_spacing[1] + j
                                                                    * (display.block_spacing[1]
                                                                       + display.block_size[1])),
                                                display.block_size))

    return blocks_list


def check_space_for_new_tetrimino(all_tetriminos):
    ''' Check no existing blocks occupy space that new block will be created in. Note that all_blocks contains the new
    # block. Returns True if there is space for the new block and False otherwise. '''
    for tetrimino in all_tetriminos[:-1]:
        for block_position in tetrimino.block_positions:
            if block_position in all_tetriminos[-1].block_positions:
                return False
    return True


def make_menu_text():
    start_text = MenuText("Start", WHITE, (int(display.size[0] / 2), int(9 * display.size[1] / 20))
                          , 'broadway', 30)
    score_text = MenuText("Scores", WHITE, (int(display.size[0] / 2), int(10 * display.size[1] / 20)), 'broadway',
                          30)
    quit_text = MenuText("Quit", WHITE, (int(display.size[0] / 2), int(11 * display.size[1] / 20)), 'broadway', 30)
    easy_text = MenuText("Easy", YELLOW, (int(display.size[0] / 6), int(13 * display.size[1] / 20)), 'broadway', 20)
    hard_text = MenuText("Hard", WHITE, (int(display.size[0] / 2), int(13 * display.size[1] / 20)), 'broadway', 20)
    insane_text = MenuText("Insane", WHITE, (int(5*display.size[0] / 6), int(13 * display.size[1] / 20)), 'broadway', 20)

    return start_text, score_text, quit_text, easy_text, hard_text, insane_text


def make_game_over_text():
    game_over_text = MenuText("GAME OVER", WHITE, (int(display.size[0] / 2), int(7 * display.size[1] / 20))
                          , 'broadway', 35)
    score_text = MenuText("Score: "+str(read_scores()[0]), WHITE, (int(display.size[0] / 2), int(8 * display.size[1] / 20))
                              , 'broadway', 35)
    main_menu_text = MenuText("MAIN MENU", WHITE, (int(display.size[0] / 2), int(10 * display.size[1] / 20)), 'broadway',
                          25)
    quit_text = MenuText("QUIT", WHITE, (int(display.size[0] / 2), int(11 * display.size[1] / 20)), 'broadway',
                            25)

    return game_over_text, score_text, main_menu_text, quit_text


def make_high_score_text():
    text_items = [MenuText("High Scores", WHITE, (int(display.size[0] / 2), int(3 * display.size[1] / 20))
                           , 'broadway', 35),
                  MenuText("MAIN MENU", WHITE, (int(display.size[0] / 2), int(11 * display.size[1] / 20)),
                           'broadway', 25)]

    for score_item in read_scores()[1]:
        text_items.append(MenuText("Score: " + str(score_item), WHITE,
                              (int(display.size[0] / 2), int((4 + len(text_items)) * display.size[1] / 20))
                              , 'broadway', 35))

    return text_items


def change_menu_colour(text_objects, m_position):
    for text_object in text_objects:
        if text_object.box.collidepoint(m_position):
            text_object.colour = YELLOW
        else:
            text_object.colour = WHITE


def menu_click_item(text_objects, m_position):
    for text_object in text_objects:
        if text_object.box.collidepoint(m_position):
            return text_object.text


def read_scores():
    with open(r'scores.txt', 'r') as reader:
        line = reader.read().splitlines()
        data = []
        for lines in line:
            data.append(lines.split(' '))
        data = list(chain.from_iterable(data))
        data = [int(i) for i in data]
        latest_score = data[-1]
        data.sort(reverse=True)
        if len(data) < 5:
            return latest_score, data
        else:
            return latest_score, data[:4]


def draw_round_rect(surface, color, rect, width, xr, yr):
    clip = surface.get_clip()

    # left and right
    surface.set_clip(clip.clip(rect.inflate(0, -yr * 2)))
    pygame.draw.rect(surface, color, rect.inflate(1 - width, 0), width)

    # top and bottom
    surface.set_clip(clip.clip(rect.inflate(-xr * 2, 0)))
    pygame.draw.rect(surface, color, rect.inflate(0, 1 - width), width)

    # top left corner
    surface.set_clip(clip.clip(rect.left, rect.top, xr, yr))
    pygame.draw.ellipse(surface, color, pygame.Rect(rect.left, rect.top, 2 * xr, 2 * yr), width)

    # top right corner
    surface.set_clip(clip.clip(rect.right - xr, rect.top, xr, yr))
    pygame.draw.ellipse(surface, color, pygame.Rect(rect.right - 2 * xr, rect.top, 2 * xr, 2 * yr), width)

    # bottom left
    surface.set_clip(clip.clip(rect.left, rect.bottom - yr, xr, yr))
    pygame.draw.ellipse(surface, color, pygame.Rect(rect.left, rect.bottom - 2 * yr, 2 * xr, 2 * yr), width)

    # bottom right
    surface.set_clip(clip.clip(rect.right - xr, rect.bottom - yr, xr, yr))
    pygame.draw.ellipse(surface, color, pygame.Rect(rect.right - 2 * xr, rect.bottom - 2 * yr, 2 * xr, 2 * yr), width)

    surface.set_clip(clip)


def check_block_occupied(block_position, all_tetriminos):
    # Returns True if block is occupied
    for tetrimino in all_tetriminos:
        if np.any(np.asarray(tetrimino.block_positions) == block_position):
            return True
    return False


def check_line_occupied(line_number, all_tetriminos):
    for i in range(0, 10):
        if not check_block_occupied(line_number*10 + i, all_tetriminos):
            return False
    return True


def remove_line(all_tetriminos, bg_blocks):
    any_lines_removed = False
    all_block_positions = [tetrimino.block_positions for tetrimino in all_tetriminos]
    line_to_check = np.unique(np.asarray(sum(all_block_positions, []))//10)

    for line in line_to_check:
        blocks_in_line = np.arange(line*10, line*10 + 10)
        if check_line_occupied(line, all_tetriminos):
            any_lines_removed = True
            i = 0
            tetriminos_to_remove = []
            for tetrimino in all_tetriminos:                
                block_removed = tetrimino.remove_blocks(blocks_in_line, all_tetriminos)
                if block_removed:
                    tetriminos_to_remove.append(i)
                i +=1
            tetriminos_to_remove.reverse()
      
            for j in tetriminos_to_remove:
                del all_tetriminos[j]
            for block_number in blocks_in_line:
                bg_blocks[block_number].colour = BACKGROUND_COLOUR

    return any_lines_removed


def move_tetrimino_from_keypress(keys, tetriminos_list, bg_blocks):
    # Disables key repititions
    pygame.key.set_repeat()

    left = tetriminos_list[-1].check_for_edge(tetriminos_list, 'l')
    right = tetriminos_list[-1].check_for_edge(tetriminos_list, 'r')
    bottom = tetriminos_list[-1].check_for_edge(tetriminos_list, 'b')

    if keys == "down" and not bottom:
        tetriminos_list[-1].move_tetrimino(bg_blocks, "down")
    elif keys == "left" and not left:
        tetriminos_list[-1].move_tetrimino(bg_blocks, "left")
    elif keys == "right" and not right:
        tetriminos_list[-1].move_tetrimino(bg_blocks, "right")


def rotate_tetrimino_from_keypress(tetriminos_list, bg_blocks):
    tetriminos_list[-1].rotate_tetrimino(bg_blocks)


def move_all_blocks_down(tetriminos_list, bg_blocks):
    
    moved_tetriminos = 1
    while moved_tetriminos > 0:
        moved_tetriminos = 0
        for tetrimino in tetriminos_list:
            other_tetriminos = [x for x in tetriminos_list if x != tetrimino]
            if not tetrimino.check_for_edge(other_tetriminos, 'b'):
                tetrimino.move_tetrimino(bg_blocks, "down")
                moved_tetriminos +=1
        

def make_new_tetrimino(tetriminos_list, _total_tetriminos):
    tetriminos_list.append(Tetrimino(random.randint(0, 4), random.randint(0, 6)))
    tetriminos_list[-1].initialize_tetrimino()
    return _total_tetriminos + 1


def make_game_menu_text(score):
    pause_text = MenuText("Pause", WHITE, (int(3*display.size[0] / 4), int(display.g_size[1] + 0.7*(display.size[1]
                                                                                                    - display.g_size[1])
                                                                           )), 'broadway', 25)

    score_text = MenuText(f"Score: {score}", WHITE, (int(display.size[0] / 4), int(display.g_size[1] + 0.7*(display.size[1]
                                                                                                - display.g_size[1]))),
                         'broadway', 25)

    return pause_text, score_text


def make_pause_menu_text(score):
    play_text = MenuText("Play", WHITE, (int(display.size[0] / 2), int(9 * display.size[1] / 20))
                          , 'broadway', 30)
    main_menu_text = MenuText("Main Menu", WHITE, (int(display.size[0] / 2), int(10 * display.size[1] / 20)), 'broadway',
                          30)
    score_text = MenuText(f"Score: {score}", WHITE, (int(display.size[0] / 2), int(11 * display.size[1] / 20)), 'broadway', 30)

    return play_text, main_menu_text, score_text


def draw_pause_menu_background():
    s = pygame.Surface((1000, 750))  # the size of your rect
    s.set_alpha(128)  # alpha level
    s.fill((255, 255, 255))  # this fills the entire surface
    window.blit(s, (0, 0))  # (0,0) are the top-left coordinates
    draw_round_rect(window, (47, 79, 79), pygame.Rect(int(0.05 * display.size[0]), int(0.025 * display.size[1]),
                                                      int(0.9 * display.size[0]), int(0.95 * display.size[1])),
                    0, 32, 32)
    return


def draw_text_items(text_items):
    for text_item in text_items:
        text_item.display_text()


# GAME SCREEN FUNCTIONS ------------------------------------------------------------------------------------------------

def game():

    game_score = 0
    line_just_removed = False
    run_game = True
    pause = False
    split_blocks = 0

    # Make necessary objects for game
    background_blocks = make_blocks()
    tetriminos = []
    total_tetriminos = make_new_tetrimino(tetriminos, 0)
    start_menu_items = make_game_menu_text(game_score)
    pause_menu_items = make_pause_menu_text(game_score)

    # Use two timers. One controls automatic movement down the screen and other for player input.
    auto_move_clock = pygame.time.get_ticks()
    player_move_clock = pygame.time.get_ticks()
    player_rotate_clock = pygame.time.get_ticks()

    while run_game:
        window.fill((0, 0, 0))

        delay = 0
        rotate_block = False
        move_delay = 0
        move_block = ""

        auto_move_passed_time = pygame.time.get_ticks() - auto_move_clock
        player_move_passed_time = pygame.time.get_ticks() - player_move_clock
        player_rotate_passed_time = pygame.time.get_ticks() - player_rotate_clock
        # --------------------------------------------------------------------------------------------------------------
        # Automatic movement (down screen):
        # --------------------------------------------------------------------------------------------------------------

        if auto_move_passed_time > game_mode.time_delay and not pause:
            auto_move_clock = pygame.time.get_ticks()

            # If a line has just been removed, all blocks must be moved down, a new tetrimino made and any more full
            # lines should be deleted.
            if line_just_removed:
                move_all_blocks_down(tetriminos, background_blocks)
                
                if not remove_line(tetriminos, background_blocks):
                    total_tetriminos = make_new_tetrimino(tetriminos, total_tetriminos)
                    line_just_removed = False

                if not check_space_for_new_tetrimino(tetriminos):  # Exits the game if no space to put new block.
                    with open(r'C:\Users\jaken\PycharmProjects\tetris\scores.txt', 'a') as writer:
                        writer.write(str(game_score) + '\n')
                    return "Game Over"

            # Otherwise, the current tetrimino should be moved down if possible and any full lines removed. If the
            # tetrimino can't be moved down a new tetrimino is made if there is space. If there is no space, the game
            # is over.
            elif tetriminos[-1].check_for_edge(tetriminos, 'b'):
                if remove_line(tetriminos, background_blocks):
                    line_just_removed = True

                else:
                    total_tetriminos = make_new_tetrimino(tetriminos, total_tetriminos)
                    if not check_space_for_new_tetrimino(tetriminos):  # Exits the game if no space to put new block.
                        with open(r'C:\Users\jaken\PycharmProjects\tetris\scores.txt', 'a') as writer:
                            writer.write(str(game_score) + '\n')
                        return "Game Over"
            else:
                tetriminos[-1].move_tetrimino(background_blocks, "down")

        # --------------------------------------------------------------------------------------------------------------
        # Player movement:
        # --------------------------------------------------------------------------------------------------------------
        elif not tetriminos[-1].check_for_edge(tetriminos, 'b') and not pause and not line_just_removed:
            delay += player_rotate_passed_time
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                rotate_block = True
            if delay > 400 and rotate_block:
                player_rotate_clock = pygame.time.get_ticks()
                rotate_tetrimino_from_keypress(tetriminos, background_blocks)
                delay = 0
                rotate_block = False

            move_delay += player_move_passed_time
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                keys = pygame.key.get_pressed()
                move_block = "down"
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                keys = pygame.key.get_pressed()
                move_block = "right"
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                keys = pygame.key.get_pressed()
                move_block = "left"
            if move_delay > 100 and move_block != "":
                player_move_clock = pygame.time.get_ticks()
                move_tetrimino_from_keypress(move_block, tetriminos, background_blocks)
                move_block = ""
                move_delay = 0

        # --------------------------------------------------------------------------------------------------------------
        # Mouse click responses:
        # --------------------------------------------------------------------------------------------------------------

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            mouse_position = pygame.mouse.get_pos()
            if pause:
                change_menu_colour(pause_menu_items[0:2], mouse_position)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    menu_response = menu_click_item(pause_menu_items[:2], mouse_position)
                    if menu_response == "Play":
                        pause = not pause
                    elif menu_response == "Main Menu":
                        return "MAIN MENU"
            else:
                change_menu_colour([start_menu_items[0]], mouse_position)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    menu_response = menu_click_item([start_menu_items[0]], mouse_position)
                    if menu_response == "Pause":
                        pause = not pause

        # --------------------------------------------------------------------------------------------------------------
        # Draw objects to screen:
        # --------------------------------------------------------------------------------------------------------------
        window.fill((0, 0, 0))

        for block in background_blocks:
            block.draw_block()

        start_menu_items = make_game_menu_text(game_score)
        draw_text_items(start_menu_items)

        if pause:
            pause_menu_items = make_pause_menu_text(game_score)
            draw_pause_menu_background()
            draw_text_items(pause_menu_items)

        game_score = (total_tetriminos - 1)*game_mode.multiplier
        pygame.display.update()


def main_menu():
    h = True
    menu_items = make_menu_text()
    game_mode.change_difficulty("Easy")
    while h:
        pygame.time.delay(100)
        window.fill((0, 0, 0))

        for menu_item in menu_items:
            menu_item.display_text()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            mouse_position = pygame.mouse.get_pos()
            change_menu_colour(menu_items[:3], mouse_position)

            if event.type == pygame.MOUSEBUTTONDOWN:
                menu_response = menu_click_item(menu_items, mouse_position)
                game_mode.change_difficulty(menu_response)
                if menu_response == "Easy":
                    menu_items[3].colour = YELLOW
                    menu_items[4].colour = WHITE
                    menu_items[5].colour = WHITE
                    break
                if menu_response == "Hard":
                    menu_items[3].colour = WHITE
                    menu_items[4].colour = YELLOW
                    menu_items[5].colour = WHITE
                    break
                if menu_response == "Insane":
                    menu_items[3].colour = WHITE
                    menu_items[4].colour = WHITE
                    menu_items[5].colour = YELLOW
                    break
                else:
                    return menu_click_item(menu_items, mouse_position)

        pygame.display.update()

    return "Start game"


def game_over():
    h = True

    game_over_items = make_game_over_text()

    while h:
        pygame.time.delay(game_mode.time_delay)
        window.fill((0, 0, 0))

        for item in game_over_items:
            item.display_text()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            mouse_position = pygame.mouse.get_pos()
            change_menu_colour(game_over_items[2:], mouse_position)

            if event.type == pygame.MOUSEBUTTONDOWN:
                return menu_click_item(game_over_items[2:], mouse_position)

        pygame.display.update()

    return "Start game"


def high_scores():
    h = True

    high_score_items = make_high_score_text()

    while h:
        pygame.time.delay(game_mode.time_delay)
        window.fill((0, 0, 0))

        for item in high_score_items:
            item.display_text()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            mouse_position = pygame.mouse.get_pos()
            change_menu_colour([high_score_items[1]], mouse_position)

            if event.type == pygame.MOUSEBUTTONDOWN:
                return menu_click_item([high_score_items[1]], mouse_position)

        pygame.display.update()

    return "Start game"


# INITIALIZE WINDOW ----------------------------------------------------------------------------------------------------
pygame.init()
display = Display(300, 700)
game_mode = GameMode("Easy")
window = pygame.display.set_mode(display.size)
clock = pygame.time.Clock()
pygame.display.set_caption('Tetris')
clock = pygame.time.Clock()

# GAME LOGIC -----------------------------------------------------------------------------------------------------------
screen_selection = main_menu()
loop = True

while loop:
    if screen_selection == "Start game" or screen_selection == "Start":
        screen_selection= game()
    elif screen_selection == "Menu" or screen_selection == "MAIN MENU":
        screen_selection = main_menu()
    elif screen_selection == "Scores":
        screen_selection = high_scores()
    elif screen_selection == "Quit" or screen_selection == "QUIT":
        pygame.quit()
        quit()
    elif screen_selection == "Game Over":
        screen_selection = game_over()
