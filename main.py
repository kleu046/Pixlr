"""
A pixel art designing app
"""
from itertools import cycle
from datetime import datetime
import pickle
import io

from PIL import Image
import pygame
from Color import Color
from Tiles import ColorTile, DrawingTile, Button


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


def add_alpha_channel_and_save_captured_drawing(surface: pygame.Surface, path: str) -> None:
    """
    Take a pygame.Surface object, add alpha channel and save it to a png image file

    Arguments:
        surface -- *pygame.Surface* object - image to be saved
        path -- file path as *str* including file name and extension (png)
    """
    buffer = io.BytesIO()
    pygame.image.save(surface, buffer, 'PNG')
    buffer.seek(0)

    img = Image.open(buffer).convert('RGBA')

    data = img.getdata()
    new_data = []

    for pixel in data:
        if pixel[0] == 255 and pixel[1] == 255 and pixel[2] == 255:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(pixel)

    img.putdata(new_data)
    img.save(path, 'PNG')


def reset_msg_label(msg_label_text: str, color_label_surface: pygame.Surface, font: pygame.font.Font) -> tuple[pygame.Surface, pygame.Rect]:
    """
    reset and redraw message label that display system messages

    Arguments:
        msg_label_text -- mesage as *str*
        color_label_surface -- *pygame.Surface* for message to be drawn on
        font -- *pygame.font.Font* for the message

    Returns:
        msg_label_surface - *pygame.Surface* with the message text
        msg_label_rect - *pygame.Rect* object for msg_label_surface
    """
    msg_label_surface = font.render(msg_label_text, True, (0, 0, 0))
    msg_label_rect = color_label_surface.get_rect(
        bottomleft=(MARGIN * 3, APP_HEIGHT - MARGIN * 2))

    return msg_label_surface, msg_label_rect


def reset_color_label(color_label_text: str, font: pygame.font.Font) -> tuple[pygame.Surface, pygame.Rect]:
    """
    reset and redraw color name and hex code on label

    Arguments:
        color_label_text -- *str* text containing colour name and hex code
        font -- *pygame.font.Font* for the label text

    Returns:
        color_label_surface - *pygame.Surface* with the message text, i.e. color name and hex code
        color_label_rect - *pygame.Rect* object for color_label_text
    """
    color_label_surface = font.render(color_label_text, True, (0, 0, 0))
    color_label_rect = color_label_surface.get_rect(bottomleft=(MARGIN * 3, APP_HEIGHT - MARGIN * 6))

    return color_label_surface, color_label_rect


def reset_drawing_tiles(drawing_board_size: int, font: pygame.font.Font) -> tuple[list[DrawingTile], pygame.Surface, pygame.Rect]:
    """
    Redraw drawing tiles according to drawing_board_size

    Arguments:
        drawing_board_size -- *int* number of tiles on one size of the square drawing board
        font -- *pygame.font.Font* font to display drawing board size

    Returns:
        drawing_tiles - *list[DrawingTile]* redrawn drawing tiles
        change_grid_label_surface - *pygame.Surface* for grid label text to be drawn on
        change_grid_label_rect - *pygame.Rect* object for change_grid_label_surface
    """
    # print(f'Reset drawing tiles to {drawing_board_size} * {drawing_board_size}...')
    drawing_tiles: list[DrawingTile] = []

    # Create DrawingTile
    for i in range(drawing_board_size):
        for j in range(drawing_board_size):
            tile = DrawingTile(
                x=i * DRAWING_TILE_SIZE +
                int(APP_WIDTH - drawing_board_size * DRAWING_TILE_SIZE) / 2,
                y=j * DRAWING_TILE_SIZE + 150,
                width=DRAWING_TILE_SIZE,
                height=DRAWING_TILE_SIZE)
            drawing_tiles.append(tile)

    change_grid_label_text = f'Ctrl + Shift + G: Change grid size | Current: {drawing_board_size}'
    change_grid_label_surface = font.render(change_grid_label_text, True, (0, 0, 0))
    change_grid_label_rect = change_grid_label_surface.get_rect(bottomleft=(MARGIN * 3, APP_HEIGHT - MARGIN * 4))

    return drawing_tiles, change_grid_label_surface, change_grid_label_rect


def reset_save_slots(selected_save_slot: int) -> list[Button]:
    """
    Redraw save slot buttons based on selected save slot

    Arguments:
        selected_save_slot -- index of save slot as *int*

    Returns:
        save_slots - *list[Button]*
    """
    save_slots: list[Button] = []
    for i in range(N_SAVE_SLOTS):
        if i == selected_save_slot:
            save_slot_color = Color.RED
        else:
            save_slot_color = Color.BLACK_L
        slot = Button(x=SAVE_SLOT_X_POS[i],
                       y=SAVE_SLOT_Y_POS,
                       width=SAVE_SLOT_WIDTH,
                       height=SAVE_SLOT_HEIGHT,
                       color=save_slot_color,
                       text_color=save_slot_color,
                       text=f'Slot {i}')
        save_slots.append(slot)

    return save_slots


def create_color_tiles(padding: int = 5) -> list[ColorTile]:
    """
    Create color palette

    Keyword Arguments:
        padding -- spacing between tiles as *int* (default: {5})

    Returns:
        color_tiles that makes up the palette as *list[ColorTile]*
    """
    color_tiles: list[ColorTile] = []
    for i, color in enumerate(Color):
        tile = ColorTile(x=COLOR_TILE_X_POS[i],
                          y=COLOR_TILE_Y_POS[i],
                          width=COLOR_TITLE_SIZE - padding,
                          height=COLOR_TITLE_SIZE,
                          color=color)
        color_tiles.append(tile)
    return color_tiles


def get_hover_tile(tiles: list[ColorTile] | list[DrawingTile], cursor_pos: tuple[float, float]) -> ColorTile | DrawingTile | None:
    """
    Takes Tiles and a cursor position (x, y) as argument to determine which tile the cursor is hovering over

    Arguments:
        tiles -- list of tiles as *list[ColorTile]* or *list[DrawingTile]*
        cursor_pos -- cursor position as *tuple[float, float]*,
            for example, user can pass in event.pos from event.type == pygame.MOUSEMOTION
            where event is an event in pygame.event.get()

    Returns:
        t -- tile where cursor is hovering over
    """
    for t in tiles:
        if t.collidepoint(cursor_pos):
            return t
    return None


def get_save_filename() -> str:
    """
    Generate a filename based on current time

    Returns:
        filename to be used for saving a drawing as str
    """
    now = datetime.now()
    return f'drawing_{now.strftime("%Y%m%d_%H%M%S")}.png'


def get_capture_rect(drawing_board_size: int) -> pygame.Rect:
    """
    Compute pygame.Rect for the drawing board area for capturing the drawing

    Arguments:
        drawing_board_size -- number of tiles on one side of the square drawing board as *int*

    Returns:
        a *pygame.Rect* object representing the position of the drawing board
    """
    min_x = int(
        (APP_WIDTH - drawing_board_size * DRAWING_TILE_SIZE) / 2)
    min_y = 150

    capture_width = drawing_board_size * DRAWING_TILE_SIZE
    capture_height = drawing_board_size * DRAWING_TILE_SIZE

    return pygame.Rect(
        min_x, min_y, capture_width, capture_height)

def get_clicked_colour(event_pos: tuple[int, int], color_tiles: list[ColorTile]) -> Color | None:
    """
    Get the selected colour from the colour palette based on event_pos, e.g. pygame.MOUSEBUTTONDOWN event

    Arguments:
        event_pos -- position of event (x, y) as *tuple[int, int]*, e.g. position of mouse click
        color_tiles -- tiles in the color palette as *list[ColorTile]*

    Returns:
        The select colour as *Color* class or *None*
    """
    for ct in color_tiles:
        if ct.is_clicked(event_pos):
            return ct.color
    return None

def get_clicked_save_slot(event_pos: tuple[int, int], save_slots: list[Button]) -> int | None:
    """
    Get the selected save slot based on event_pos, e.g. pygame.MOUSEBUTTONDOWN event

    Arguments:
        event_pos -- position of event (x, y) as *tuple[int, int]*, e.g. position of mouse click
        save_slots -- the save slots as *list[Button]*

    Returns:
        the save slot index or None
    """
    for sl in save_slots:
        if sl.is_clicked(event_pos):
            return int(sl.text.split(' ')[1])
    return None

def save_work(drawing_tiles: list[DrawingTile], save_slot: int) -> None:
    """
    Save the work in progress in *save_slot*

    Arguments:
        drawing_tiles -- the tiles in the drawing board as *list[DrawingTile]*
        save_slot -- index of the save slot to be used
    """
    drawing_tile_colors = [dt.color for dt in drawing_tiles]
    with open(f'save_{save_slot}.pkl', 'wb') as f:
        pickle.dump(drawing_tile_colors, f)

def load_work(save_slot: int):
    """
    loading from pkl file for the *save_slot*

    Arguments:
        save_slot -- index of the save_slot as *int*

    Returns:
        Pickle load data
    """
    with open(f'save_{save_slot}.pkl', 'rb') as f:
        return pickle.load(f)

def redraw_tiles(drawing_tiles: list[DrawingTile], saved_tile_colors: list[Color]) -> list[DrawingTile]:
    """
    redraw tile with the colour of the tiles provided as *list[Color]*

    Arguments:
        drawing_tiles -- list of drawing tiles as *list[DrawingTile]*
        saved_tile_colors -- list of colours as *list[Color]* for filling into *drawing_tiles*

    Returns:
        redrawn drawing_tiles
    """
    for i, dt in enumerate(drawing_tiles):
        dt.color = saved_tile_colors[i]
    return drawing_tiles

def clear_image(drawing_tiles: list[DrawingTile]) -> list[DrawingTile]:
    """
    Clear the drawing board

    Arguments:
        drawing_tiles -- the drawing tiles in the drawing board as *list[DrawingTile]*

    Returns:
        cleared drawing board as list[drawing_tiles]
    """
    for dt in drawing_tiles:
        dt.color = Color.WHITE
    return drawing_tiles

def main():
    """
    main function
    """

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

    color_tiles: list[ColorTile] = create_color_tiles(padding=5)

    save_slots: list[Button] = reset_save_slots(
        _save_slot)     # Create save slots

    change_grid_label_surface: pygame.surface.Surface  # pylint: disable=c-extension-no-member
    change_grid_label_rect: pygame.Rect

    drawing_board_size = next(CYCLE_GRID_SIZES)
    drawing_tiles, change_grid_label_surface, change_grid_label_rect = reset_drawing_tiles(drawing_board_size, font)

    running = True
    capture_drawing = False
    clearing_image = False
    saving_work = False
    loading_work = False


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # pylint: disable=no-member
                running = False

            # select colour or colouring in
            elif event.type == pygame.MOUSEBUTTONDOWN or pygame.mouse.get_pressed()[0]: # pylint: disable=no-member
                # select colour
                if selected_color := get_clicked_colour(event.pos, color_tiles):
                    _selected_color = selected_color

                # colour in
                for dt in drawing_tiles:
                    if dt.is_clicked(event.pos):
                        dt.color = _selected_color
                        # print(f"{ct.color=}")
                        break

                # select save slot
                if selected_save_slot := get_clicked_save_slot(event.pos, save_slots):
                    _save_slot = selected_save_slot
                save_slots = reset_save_slots(_save_slot)

                msg_label_surface, msg_label_rect = reset_msg_label(MESSAGE_PROMPT, color_label_surface, font)  # wipe prev message after click

            elif event.type == pygame.MOUSEMOTION: # pylint: disable=no-member
                hover_tile_label_text = ''
                # check if mouse is hovering over color palette tiles
                if color_tile := get_hover_tile(color_tiles, event.pos):
                    hover_tile_label_text = f'{color_tile.color.name}: {color_tile.color}'

                # check if mouse is hovering over drawing tiles
                elif drawing_tile := get_hover_tile(drawing_tiles, event.pos):
                    hover_tile_label_text = f'{drawing_tile.color.name}: {drawing_tile.color}'

                # update color label with hover tile color
                color_label_surface, color_label_rect = reset_color_label(hover_tile_label_text, font)

            elif event.type == pygame.KEYDOWN: # pylint: disable=no-member
                # mod key set up
                ctrl_shift = event.mod & pygame.KMOD_CTRL and event.mod & pygame.KMOD_SHIFT and not event.mod & ~(pygame.KMOD_CTRL | pygame.KMOD_SHIFT) # pylint: disable=no-member
                ctrl = event.mod & pygame.KMOD_CTRL and not event.mod & ~pygame.KMOD_CTRL # pylint: disable=no-member
                keydown_match_message: str = ''

                # change grid size
                if event.key == pygame.K_g and ctrl_shift: # pylint: disable=no-member
                    drawing_board_size = next(CYCLE_GRID_SIZES)
                    drawing_tiles, change_grid_label_surface, change_grid_label_rect = reset_drawing_tiles(drawing_board_size, font)
                    keydown_match_message = f'{MESSAGE_PROMPT} Grid changed!'

                # save image
                elif event.key == pygame.K_s and ctrl: # only ctrl and not other modifiers # pylint: disable=no-member
                    # print('Saving image into file...')
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
            save_work(drawing_tiles, _save_slot)
            # print('Your work is saved!')
            action_complete_message = f'{MESSAGE_PROMPT} Your work is saved!'
            saving_work = False


        if loading_work:
            # load from pkl file
            try:
                saved_tile_colors = load_work(_save_slot)
                action_complete_message = f'{MESSAGE_PROMPT} Your work is loaded!'
            except FileNotFoundError:
                # print(f'Nothing saved in slot {_save_slot}')
                action_complete_message = f'{MESSAGE_PROMPT} Nothing saved in slot {_save_slot}'

            try:
                drawing_tiles = redraw_tiles(drawing_tiles, saved_tile_colors)
            except UnboundLocalError:
                action_complete_message = f'{MESSAGE_PROMPT} Save slot is empty!'
            except IndexError:
                action_complete_message = f'{MESSAGE_PROMPT} Incorrect grid size! Change grid size to {int(len(saved_tile_colors)**0.5)}'

            loading_work = False


        if clearing_image:
            clear_image(drawing_tiles)
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

        screen.blit(save_label_surface, save_label_rect)
        screen.blit(clear_label_surface, clear_label_rect)
        screen.blit(load_label_surface, load_label_rect)
        screen.blit(change_grid_label_surface, change_grid_label_rect)
        screen.blit(save_progress_label_surface, save_progress_label_rect)
        screen.blit(color_label_surface, color_label_rect)
        screen.blit(msg_label_surface, msg_label_rect)

        pygame.display.update()

        # Saving image to png needs to be after display.update()
        # because we need to remove the grid and just save the drawing
        if capture_drawing:
            # get drawing surface
            drawing_surface = screen.subsurface(get_capture_rect(drawing_board_size)).copy()

            save_filename = get_save_filename()

            add_alpha_channel_and_save_captured_drawing(drawing_surface, save_filename) # generate save filename based on datetime

            # print('Image saved!')
            action_complete_message = f'{MESSAGE_PROMPT} Image saved to {save_filename}!'
            capture_drawing = False

        # update message after taking action
        if action_complete_message != '':
            msg_label_surface, msg_label_rect = reset_msg_label(action_complete_message, color_label_surface, font)

        clock.tick(60)

    pygame.quit()  # pylint: disable=no-member


if __name__ == "__main__":
    main()
