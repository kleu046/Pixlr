"""
A pixel art designing app
"""
import pickle
import io
from datetime import datetime

import pygame
from PIL import Image
from Color import Color
from Tiles import ColorTile, DrawingTile, Button
from GameConfig import GameConfig
from GameUI import GameUI


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


def get_capture_rect(game_config: GameConfig) -> pygame.Rect:
    """
    Compute pygame.Rect for the drawing board area for capturing the drawing

    Arguments:
        drawing_board_size -- number of tiles on one side of the square drawing board as *int*

    Returns:
        a *pygame.Rect* object representing the position of the drawing board
    """
    min_x = int(
        (game_config.app_width - game_config.drawing_board_size * game_config.drawing_tile_size) / 2)
    min_y = 150

    capture_width = game_config.drawing_board_size * game_config.drawing_tile_size
    capture_height = game_config.drawing_board_size * game_config.drawing_tile_size

    return pygame.Rect(
        min_x, min_y, capture_width, capture_height)


def get_clicked_colour(event_pos: tuple[int, int], palette: list[ColorTile]) -> Color | None:
    """
    Get the selected colour from the colour palette based on event_pos, e.g. pygame.MOUSEBUTTONDOWN event

    Arguments:
        event_pos -- position of event (x, y) as *tuple[int, int]*, e.g. position of mouse click
        palette -- tiles in the color palette as *list[ColorTile]*

    Returns:
        The select colour as *Color* class or *None*
    """
    for ct in palette:
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


def save_work(drawing_board: list[DrawingTile], save_slot: int) -> None:
    """
    Save the work in progress in *save_slot*

    Arguments:
        drawing_board -- the tiles in the drawing board as *list[DrawingTile]*
        save_slot -- index of the save slot to be used
    """
    drawing_tile_colors = [dt.color for dt in drawing_board]
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


def clear_image(drawing_board: list[DrawingTile]) -> list[DrawingTile]:
    """
    Clear the drawing board

    Arguments:
        drawing_board -- the drawing tiles in the drawing board as *list[DrawingTile]*

    Returns:
        cleared drawing board as list[drawing_board]
    """
    for dt in drawing_board:
        dt.color = Color.WHITE
    return drawing_board


def main():
    """
    main function
    """
    game_config = GameConfig(app_width = 800)
    ui = GameUI(game_config)

    clock: pygame.time.Clock = pygame.time.Clock()

    active_save_slot: int = 0
    active_color: Color = Color.WHITE
    running = True
    capture_drawing = False
    clearing_image = False
    saving_work = False
    loading_work = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # pylint: disable=no-member
                running = False

            elif event.type == pygame.VIDEORESIZE: # pylint: disable=no-member
                app_width, _ = event.w, event.h
                ui.reset_window(GameConfig.reset(app_width))
                ui.reset_instruction_pane()
                ui.reset_change_grid_size_label()
                ui.reset_color_label()
                ui.reset_msg_label()
                ui.reset_palette()
                ui.reset_drawing_board(ui.drawing_board)
                ui.reset_save_slots(active_save_slot)

            # select colour or colouring in
            elif event.type == pygame.MOUSEBUTTONDOWN or pygame.mouse.get_pressed()[0]: # pylint: disable=no-member
                # select colour
                if clicked_color := get_clicked_colour(event.pos, ui.palette):
                    active_color = clicked_color

                # colour in
                for dt in ui.drawing_board:
                    if dt.is_clicked(event.pos):
                        dt.color = active_color
                        break

                # select save slot
                clicked_save_slot = get_clicked_save_slot(event.pos, ui.save_slots)
                if clicked_save_slot is not None:
                    active_save_slot = clicked_save_slot
                    ui.reset_save_slots(active_save_slot)

                ui.reset_msg_label()

            elif event.type == pygame.MOUSEMOTION: # pylint: disable=no-member
                hover_tile: ColorTile | DrawingTile | None = None
                # check if mouse is hovering over color palette tiles
                if color_tile := get_hover_tile(ui.palette, event.pos):
                    hover_tile = color_tile

                # check if mouse is hovering over drawing tiles
                elif drawing_tile := get_hover_tile(ui.drawing_board, event.pos):
                    hover_tile = drawing_tile

                # update color label with hover tile color
                ui.reset_color_label(hover_tile)

            elif event.type == pygame.KEYDOWN: # pylint: disable=no-member
                # mod key set up
                ctrl_shift = event.mod & pygame.KMOD_CTRL and event.mod & pygame.KMOD_SHIFT and not event.mod & ~(pygame.KMOD_CTRL | pygame.KMOD_SHIFT) # pylint: disable=no-member
                ctrl = event.mod & pygame.KMOD_CTRL and not event.mod & ~pygame.KMOD_CTRL # pylint: disable=no-member
                keydown_match_message: str = ''

                # change grid size
                if event.key == pygame.K_g and ctrl_shift: # pylint: disable=no-member
                    ui.game_config.next_grid_size()
                    ui.reset_change_grid_size_label()
                    ui.reset_drawing_board()
                    keydown_match_message = 'Grid changed!'

                # save image
                elif event.key == pygame.K_s and ctrl: # only ctrl and not other modifiers # pylint: disable=no-member
                    keydown_match_message = 'Saving image...'
                    capture_drawing = True

                # saving work in the chosen slot
                elif event.key == pygame.K_a and ctrl_shift: # pylint: disable=no-member
                    keydown_match_message = 'Saving your work...'
                    saving_work = True

                # loading work saved in chosen slot
                elif event.key == pygame.K_l and ctrl_shift: # pylint: disable=no-member
                    keydown_match_message = 'Loading your work...'
                    loading_work = True

                # clearing the grid
                elif event.key == pygame.K_k and ctrl_shift: # pylint: disable=no-member
                    keydown_match_message = 'Clearing image...'
                    clearing_image = True

                if keydown_match_message != '': # if keydown matches above, print message on ui.screen
                    ui.reset_msg_label(keydown_match_message)

        # taking actions after registering matched keydown
        action_complete_message: str = ''


        if saving_work:
            save_work(ui.drawing_board, active_save_slot)
            action_complete_message = 'Your work is saved!'
            saving_work = False


        if loading_work:
            # load from pkl file
            try:
                saved_tile_colors = load_work(active_save_slot)
                action_complete_message = 'Your work is loaded!'
            except FileNotFoundError:
                action_complete_message = 'Nothing saved in slot {active_save_slot}'
            except UnboundLocalError:
                action_complete_message = 'Save slot is empty!'
            try:
                ui.reset_drawing_board(tile_colors = saved_tile_colors)
                if ui.game_config.drawing_board_size != int(len(saved_tile_colors)**0.5):
                    action_complete_message = f'Incorrect grid size! Change grid size to {int(len(saved_tile_colors)**0.5)}'
            except UnboundLocalError:
                action_complete_message = 'Save slot is empty!'
            except IndexError:
                action_complete_message = f'Incorrect grid size! Change grid size to {int(len(saved_tile_colors)**0.5)}'

            loading_work = False

        if clearing_image:
            clear_image(ui.drawing_board)
            # print('Image cleared!')
            action_complete_message = 'Image cleared!'
            clearing_image = False

        ui.screen.fill((255, 255, 255))

        ui.draw(active_color, capture_drawing)

        pygame.display.update()

        # Saving image to png needs to be after display.update()
        # because we need to remove the grid and just save the drawing
        if capture_drawing:
            # get drawing surface
            drawing_surface = ui.screen.subsurface(get_capture_rect(game_config)).copy()
            save_filename = get_save_filename()
            add_alpha_channel_and_save_captured_drawing(drawing_surface, save_filename) # generate save filename based on datetime
            action_complete_message = f'Image saved to {save_filename}!'
            capture_drawing = False

        # update message after taking action
        if action_complete_message != '':
            ui.reset_msg_label(action_complete_message)

        clock.tick(60)

    pygame.quit()  # pylint: disable=no-member


if __name__ == "__main__":
    main()
