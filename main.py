"""
A pixel art designing app
"""
from itertools import cycle
from datetime import datetime
from enum import StrEnum
import sys
import pickle

from PIL import Image
import pygame
from Color import Color
from Tiles import ColorTiles, DrawingTiles, Buttons


GRID_SIZE_OPTIONS = [16, 22, 28, 8]
CYCLE_GRID_SIZES = cycle(GRID_SIZE_OPTIONS)
DRAWING_TILE_SIZE = 25
N_COLOR_TILES = len(list(Color))
N_COLOR_PALETTE_ROWS = 3
N_COLORS_IN_A_ROW = N_COLOR_TILES // N_COLOR_PALETTE_ROWS
MARGIN = 10
N_SAVE_SLOTS: int = 5

APP_WIDTH: int = 800
COLOR_TITLE_SIZE: int = int(
    round((APP_WIDTH - MARGIN * 2) / N_COLORS_IN_A_ROW, 0))
APP_HEIGHT: int = (
    # palette space
    (N_COLOR_TILES // N_COLORS_IN_A_ROW) * COLOR_TITLE_SIZE + MARGIN * 2 +
    max(GRID_SIZE_OPTIONS) * DRAWING_TILE_SIZE + MARGIN * 2 +  # drawing space
    200  # label space
)

TOTAL_ROW_WIDTH = N_COLORS_IN_A_ROW * COLOR_TITLE_SIZE

X_OFFSET = (APP_WIDTH - TOTAL_ROW_WIDTH) // 2

COLOR_TILE_X_POS: list[int] = [(i % N_COLORS_IN_A_ROW) * COLOR_TITLE_SIZE + X_OFFSET for i in range(N_COLOR_TILES)]
COLOR_TILE_Y_POS: list[int] = [i // N_COLORS_IN_A_ROW *(COLOR_TITLE_SIZE + 5) + 10 for i in range(N_COLOR_TILES)]

SAVE_SLOT_HEIGHT: int = 30
SAVE_SLOT_WIDTH: int = int(round((APP_WIDTH - MARGIN * 2) / N_SAVE_SLOTS, 0))
SAVE_SLOT_X_POS: list[int] = [i * SAVE_SLOT_WIDTH + X_OFFSET for i in range(N_SAVE_SLOTS)]
SAVE_SLOT_Y_POS: int = APP_HEIGHT - MARGIN * 14

SAVE_LABEL_TEXT = 'Ctrl + S:          Save to file'
CLEAR_LABEL_TEXT = 'Ctrl + Shift + K:  Clear grid'
LOAD_LABEL_TEXT = 'Ctrl + Shift + L:  Load progress'
SAVE_PROGRESS_LABEL_TEXT = 'Ctrl + Shift + A:  Save progress'

MESSAGE_PROMPT: str = '>>>'


def add_transparency_channel_to_captured_drawing(path):
    img = Image.open(path).convert('RGBA')

    data = img.getdata()
    newData = []
    for item in data:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)

    img.save(path, "PNG")


def reset_msg_label(msg_label_text, color_label_surface, font):
    msg_label_surface = font.render(msg_label_text, True, (0, 0, 0))
    msg_label_rect = color_label_surface.get_rect(
        bottomleft=(MARGIN * 3, APP_HEIGHT - MARGIN * 2))

    return msg_label_surface, msg_label_rect


def reset_color_label(color_label_text, font):
    color_label_surface = font.render(color_label_text, True, (0, 0, 0))
    color_label_rect = color_label_surface.get_rect(bottomleft=(MARGIN * 3, APP_HEIGHT - MARGIN * 6))

    return color_label_surface, color_label_rect


def reset_drawing_tiles(num_of_drawing_tiles, font) -> tuple[list[DrawingTiles], pygame.Surface, pygame.Rect]:
    print(
        f'Reset drawing tiles to {num_of_drawing_tiles} * {num_of_drawing_tiles}...')
    drawing_tiles: list[DrawingTiles] = []

    # Create DrawingTiles
    for i in range(num_of_drawing_tiles):
        for j in range(num_of_drawing_tiles):
            tile = DrawingTiles(
                x=i * DRAWING_TILE_SIZE +
                int(APP_WIDTH - num_of_drawing_tiles * DRAWING_TILE_SIZE) / 2,
                y=j * DRAWING_TILE_SIZE + 150,
                width=DRAWING_TILE_SIZE,
                height=DRAWING_TILE_SIZE)
            drawing_tiles.append(tile)

    change_grid_label_text = f'Ctrl + Shift + G: Change grid size | Current: {num_of_drawing_tiles}'
    change_grid_label_surface = font.render(change_grid_label_text, True, (0, 0, 0))
    change_grid_label_rect = change_grid_label_surface.get_rect(bottomleft=(MARGIN * 3, APP_HEIGHT - MARGIN * 4))

    return drawing_tiles, change_grid_label_surface, change_grid_label_rect


def reset_save_slots(save_slot):
    save_slots: list[Buttons] = []
    for i in range(N_SAVE_SLOTS):
        if i == save_slot:
            save_slot_color = Color.RED
        else:
            save_slot_color = Color.BLACK_L
        slot = Buttons(x=SAVE_SLOT_X_POS[i],
                       y=SAVE_SLOT_Y_POS,
                       width=SAVE_SLOT_WIDTH,
                       height=SAVE_SLOT_HEIGHT,
                       color=save_slot_color,
                       text_color=save_slot_color,
                       text=f'Slot {i}')
        save_slots.append(slot)

    return save_slots


def create_color_tiles(padding=5):
    color_tiles: list[ColorTiles] = []
    for i, color in enumerate(Color):
        tile = ColorTiles(x=COLOR_TILE_X_POS[i], 
                          y=COLOR_TILE_Y_POS[i],
                          width=COLOR_TITLE_SIZE - padding, 
                          height=COLOR_TITLE_SIZE, 
                          color=color)
        color_tiles.append(tile)
    return color_tiles


def main():

    pygame.init()  # pylint: disable=no-member
    pygame.display.set_caption("Pixlr")
    clock: pygame.time.Clock = pygame.time.Clock()
    screen: pygame.Surface = pygame.display.set_mode((APP_WIDTH, APP_HEIGHT))
    font = pygame.font.SysFont(None, 14)

    _save_slot: int = 0
    _selected_color: Color = Color.WHITE

    save_label_surface = font.render(SAVE_LABEL_TEXT, True, (0, 0, 0))
    save_label_rect = save_label_surface.get_rect(bottomleft=(APP_WIDTH // 2, APP_HEIGHT - MARGIN * 4))

    clear_label_surface = font.render(CLEAR_LABEL_TEXT, True, (0, 0, 0))
    clear_label_rect = clear_label_surface.get_rect(bottomleft=(APP_WIDTH // 2, APP_HEIGHT - MARGIN * 2))

    load_label_surface = font.render(LOAD_LABEL_TEXT, True, (0, 0, 0))
    load_label_rect = load_label_surface.get_rect(bottomleft=(APP_WIDTH // 2, APP_HEIGHT - MARGIN * 8))

    save_progress_label_surface = font.render(SAVE_PROGRESS_LABEL_TEXT, True, (0, 0, 0))
    save_progress_label_rect = save_progress_label_surface.get_rect(bottomleft=(APP_WIDTH // 2, APP_HEIGHT - MARGIN * 6))

    color_label_surface, color_label_rect = reset_color_label('Hover on a color to display color name and HEX code', font)

    msg_label_surface, msg_label_rect = reset_msg_label(f'{MESSAGE_PROMPT} Messages are displayed here', color_label_surface, font)

    color_tiles: list[ColorTiles] = create_color_tiles(padding=5)

    save_slots: list[Buttons] = reset_save_slots(
        _save_slot)     # Create save slots

    change_grid_label_surface: pygame.surface.Surface  # pylint: disable=c-extension-no-member
    change_grid_label_rect: pygame.Rect

    num_of_drawing_tiles = next(CYCLE_GRID_SIZES)
    drawing_tiles, change_grid_label_surface, change_grid_label_rect = reset_drawing_tiles(
        num_of_drawing_tiles, font)

    running = True
    capture_drawing = False
    clearing_image = False
    saving_work = False
    loading_work = False

    def get_hover_tile(tiles: list[ColorTiles] | list[DrawingTiles], cursor_pos: tuple[float, float]) -> ColorTiles | None:
        for t in tiles:
            if t.collidepoint(cursor_pos):
                return t
        return None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # pylint: disable=no-member
                running = False

            # select colour or colouring in
            elif event.type == pygame.MOUSEBUTTONDOWN or pygame.mouse.get_pressed()[0]: # pylint: disable=no-member
                for ct in color_tiles:
                    if ct.is_clicked(event.pos):
                        _selected_color = ct.color
                        # print(f"{ct.color=}")
                for dt in drawing_tiles:
                    if dt.is_clicked(event.pos):
                        dt.color = _selected_color
                        # print(f"{ct.color=}")
                for sl in save_slots:
                    if sl.is_clicked(event.pos):
                        _save_slot = int(sl.text.split(' ')[1])
                        save_slots = reset_save_slots(_save_slot)
                        break
                msg_label_surface, msg_label_rect = reset_msg_label(MESSAGE_PROMPT, color_label_surface, font)  # wipe prev message after click

            elif event.type == pygame.MOUSEMOTION: # pylint: disable=no-member
                hovered = False
                if color_tile := get_hover_tile(color_tiles, event.pos):
                    hovered = True
                    color_label_surface, color_label_rect = reset_color_label(f'{color_tile.color.name}: {color_tile.color}', font)
                elif drawing_tile := get_hover_tile(drawing_tiles, event.pos):
                    hovered = True
                    color_label_surface, color_label_rect = reset_color_label(f'{drawing_tile.color.name}: {drawing_tile.color}', font)
                if not hovered:
                    color_label_surface, color_label_rect = reset_color_label('', font)

            elif event.type == pygame.KEYDOWN: # pylint: disable=no-member
                # mod key set up
                ctrl_shift = (event.mod & pygame.KMOD_CTRL) and (event.mod & pygame.KMOD_SHIFT) and not (event.mod & ~(pygame.KMOD_CTRL | pygame.KMOD_SHIFT)) # pylint: disable=no-member
                ctrl = event.mod & pygame.KMOD_CTRL and not (event.mod & ~pygame.KMOD_CTRL) # pylint: disable=no-member
                keydown_match_message: str = ''

                # change grid size
                if event.key == pygame.K_g and ctrl_shift: # pylint: disable=no-member
                    num_of_drawing_tiles = next(CYCLE_GRID_SIZES)
                    drawing_tiles, change_grid_label_surface, change_grid_label_rect = reset_drawing_tiles(num_of_drawing_tiles, font)
                    keydown_match_message = f'{MESSAGE_PROMPT} Grid changed!'

                # save image
                elif event.key == pygame.K_s and ctrl: # only ctrl and not other modifiers # pylint: disable=no-member
                    print('Saving image into file...')
                    keydown_match_message = f'{MESSAGE_PROMPT} Saving image...'
                    # pygame.display.update()
                    capture_drawing = True

                # saving work in the chosen slot
                elif event.key == pygame.K_a and ctrl_shift: # pylint: disable=no-member
                    # print('Saving your work...')
                    keydown_match_message = f'{MESSAGE_PROMPT} Saving your work...'
                    saving_work = True

                # loading work saved in chosen slot
                elif event.key == pygame.K_l and ctrl_shift: # pylint: disable=no-member
                    # print('Loading your work...')
                    keydown_match_message = f'{MESSAGE_PROMPT} Loading your work...'
                    loading_work = True

                # clearing the grid
                elif event.key == pygame.K_k and ctrl_shift: # pylint: disable=no-member
                    # print('Clearing image...')
                    keydown_match_message = f'{MESSAGE_PROMPT} Clearing image...'
                    clearing_image = True

                if keydown_match_message != '': # if keydown matches above, print message on screen
                    msg_label_surface, msg_label_rect = reset_msg_label(keydown_match_message, color_label_surface, font)

        # taking actions after registering matched keydown
        action_complete_message: str = ''


        if saving_work:
            drawing_tile_colors = [dt.color for dt in drawing_tiles]
            with open(f'save_{_save_slot}.pkl', 'wb') as f:
                pickle.dump(drawing_tile_colors, f)
            # print('Your work is saved!')
            action_complete_message = f'{MESSAGE_PROMPT} Your work is saved!'
            saving_work = False

        if loading_work:
            try:
                with open(f'save_{_save_slot}.pkl', 'rb') as f:
                    saved_tile_colors = pickle.load(f)
                try:  # add logic to handle incorrect grid size for loading or automatically change to correct grid size
                    for i, dt in enumerate(drawing_tiles):
                        dt.color = saved_tile_colors[i]
                    action_complete_message = f'{MESSAGE_PROMPT} Your work is loaded!'
                except Exception as e:
                    action_complete_message = f"{MESSAGE_PROMPT} {e:}: 'Error loading your work'"
                # pygame.display.update()
            except FileNotFoundError as e:
                # print(f'Nothing saved in slot {_save_slot}')
                action_complete_message = f'{MESSAGE_PROMPT} {e:} Nothing saved in slot {_save_slot}'
            finally:
                loading_work = False

        if clearing_image:
            for dt in drawing_tiles:
                dt.color = Color.WHITE
            # print('Image cleared!')
            action_complete_message = f'{MESSAGE_PROMPT} Image cleared!'
            clearing_image = False


        screen.fill((255, 255, 255))

        for ct in color_tiles:
            ct.draw(screen, _selected_color)  # Draw the color tiles

        for dt in drawing_tiles:
            dt.draw(screen, capture_drawing)  # Draw the drawing tiles

        for sl in save_slots:
            sl.draw(screen)


        if capture_drawing:
            min_x = int(
                (APP_WIDTH - num_of_drawing_tiles * DRAWING_TILE_SIZE) / 2)
            min_y = 150

            capture_width = num_of_drawing_tiles * DRAWING_TILE_SIZE
            capture_height = num_of_drawing_tiles * DRAWING_TILE_SIZE

            capture_rect = pygame.Rect(
                min_x, min_y, capture_width, capture_height)

            drawing_surface = screen.subsurface(capture_rect).copy()

            now = datetime.now()
            now = now.strftime("%Y%m%d_%H%M%S")
            save_filename = f'drawing_{now}.png'

            pygame.image.save(drawing_surface, save_filename)

            add_transparency_channel_to_captured_drawing(f'drawing_{now}.png')

            # print('Image saved!')
            action_complete_message = f'{MESSAGE_PROMPT} Image saved to {save_filename}!'
            capture_drawing = False

        # update message after taking action
        if action_complete_message != '':
            msg_label_surface, msg_label_rect = reset_msg_label(action_complete_message, color_label_surface, font)

        screen.blit(save_label_surface, save_label_rect)
        screen.blit(clear_label_surface, clear_label_rect)
        screen.blit(load_label_surface, load_label_rect)
        screen.blit(change_grid_label_surface, change_grid_label_rect)
        screen.blit(save_progress_label_surface, save_progress_label_rect)
        screen.blit(color_label_surface, color_label_rect)
        screen.blit(msg_label_surface, msg_label_rect)

        pygame.display.update()

        clock.tick(60)

    pygame.quit()  # pylint: disable=no-member
    sys.exit()


if __name__ == "__main__":
    main()
