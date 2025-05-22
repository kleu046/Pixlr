"""
A pixel art designing app
"""
import pickle
import io
from itertools import cycle
from datetime import datetime
from dataclasses import dataclass, field

import pygame
from PIL import Image
from Color import Color
from Tiles import ColorTile, DrawingTile, Button

@dataclass
class AppConfig:
    """
    App configuration dataclass
    """
    app_width: int # 800
    
    font_size: int = field(init=False) # 14

    grid_size_options: tuple[int, int, int] = (16, 22, 8)
    cycle_grid_sizes:  cycle = cycle(grid_size_options)
    drawing_tile_size: int = field(init=False) # 25
    n_color_tiles: int = len(list(Color))
    n_color_palette_rows: int = 3
    n_colors_in_a_row: int = n_color_tiles // n_color_palette_rows
    margin: int = field(init=False)
    n_save_slots: int = 5

    color_tile_size: int = field(init=False)
    app_height: int = field(init=False)

    total_row_width: int = field(init=False)

    x_offset: int = field(init=False)

    color_tile_x_pos: list[int] = field(init=False)
    color_tile_y_pos: list[int] = field(init=False)

    save_slot_height: int = field(init=False)
    save_slot_width: int = field(init=False)

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __post_init__(self):
        self.font_size = self.compute_font_size()

        self.drawing_tile_size = self.compute_drawing_tile_size()

        self.margin = self.compute_margin()

        self.color_tile_size = self.compute_color_tile_size()

        self.app_height = self.compute_app_height()

        self.total_row_width = self.compute_total_row_width()

        self.x_offset = self.compute_x_offset()

        self.color_tile_x_pos, self.color_tile_y_pos = self.compute_color_tile_pos()

        self.save_slot_width, self.save_slot_height = self.compute_save_slot_dims()
        self.save_slot_x_pos, self.save_slot_y_pos = self.compute_save_slot_pos()


    @classmethod
    def reset(cls, *args, **kwargs):
        """
        Reset AppConfig

        Returns:
            _description_
        """
        cls._instance = None
        return cls(*args, **kwargs)

    def compute_font_size(self) -> int:
        """
        compute font_size based on app_width

        Returns:
            _description_
        """
        return int(self.app_width / 57)

    def compute_margin(self) -> int:
        """
        compute margin based on app_width

        Returns:
            _description_
        """
        return int(self.app_width / 80)

    def compute_drawing_tile_size(self) -> int:
        """
        compute drawing_tile_size based on app_width and margin
        Returns:
            _description_
        """
        return int(self.app_width / 32)

    def compute_save_slot_pos(self):
        """
        Compute save slot positions

        Returns:
            _description_
        """
        return [i * self.save_slot_width + self.x_offset for i in range(self.n_save_slots)], \
            self.app_height - self.margin * 14

    def compute_save_slot_dims(self):
        """
        Compute save slot height based on margin size and app width

        Returns:
            _description_
        """
        return int(round((self.app_width - self.margin * 2) / self.n_save_slots, 0)), self.margin * 3


    def compute_color_tile_pos(self):
        """
        Compute the x,y positions of color palette tiles

        Returns:
            _description_
        """
        return [(i % self.n_colors_in_a_row) * self.color_tile_size + self.x_offset for i in range(self.n_color_tiles)], \
            [i // self.n_colors_in_a_row *(self.color_tile_size + int(self.margin / 2)) + self.margin for i in range(self.n_color_tiles)]

    def compute_x_offset(self):
        """
        Compute x offset

        Returns:
            _description_
        """
        return (self.app_width - self.total_row_width) // 2

    def compute_total_row_width(self) -> int:
        """
        compute total_row_width based on n_colors_in_a_row and color_tile_size

        Returns:
            _description_
        """
        return self.n_colors_in_a_row * self.color_tile_size

    def compute_app_height(self) -> int:
        """
        compute app_height based on grid_size, drawing_tile_size, margin, n_save_slots

        Returns:
            _description_
        """
        return (
            # palette space
            (self.n_color_tiles // self.n_colors_in_a_row) * self.color_tile_size + self.margin * 2 +
            max(self.grid_size_options) * self.drawing_tile_size + self.margin * 2 +  # drawing space
            200  # label space
        )

    def compute_color_tile_size(self) -> int:
        """
        compute color_tile_size based on app_width and margin
        Returns:
            _description_
        """
        return int(round((self.app_width - self.margin * 2) / self.n_colors_in_a_row, 0))


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


def reset_msg_label(msg_label_text: str, color_label_surface: pygame.Surface, font: pygame.font.Font, app_config: AppConfig) -> tuple[pygame.Surface, pygame.Rect]:
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
        bottomleft=(app_config.margin * 3, app_config.app_height - app_config.margin * 2))

    return msg_label_surface, msg_label_rect


def reset_color_label(color_label_text: str, font: pygame.font.Font, app_config: AppConfig) -> tuple[pygame.Surface, pygame.Rect]:
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
    color_label_rect = color_label_surface.get_rect(bottomleft=(app_config.margin * 3, app_config.app_height - app_config.margin * 6))

    return color_label_surface, color_label_rect


def reset_drawing_tiles(drawing_board_size: int, font: pygame.font.Font, app_config: AppConfig) -> tuple[list[DrawingTile], pygame.Surface, pygame.Rect]:
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
                x = i * app_config.drawing_tile_size +
                int(app_config.app_width - drawing_board_size * app_config.drawing_tile_size) / 2,
                y = j * app_config.drawing_tile_size + int(app_config.app_width / 5.5),
                width = app_config.drawing_tile_size,
                height = app_config.drawing_tile_size)
            drawing_tiles.append(tile)

    change_grid_label_text = f'Ctrl + Shift + G: Change grid size | Current: {drawing_board_size}'
    change_grid_label_surface = font.render(change_grid_label_text, True, (0, 0, 0))
    change_grid_label_rect = change_grid_label_surface.get_rect(bottomleft=(app_config.margin * 3, app_config.app_height - app_config.margin * 4))

    return drawing_tiles, change_grid_label_surface, change_grid_label_rect


def reset_save_slots(selected_save_slot: int, app_config: AppConfig) -> list[Button]:
    """
    Redraw save slot buttons based on selected save slot

    Arguments:
        selected_save_slot -- index of save slot as *int*

    Returns:
        save_slots - *list[Button]*
    """
    save_slots: list[Button] = []
    for i in range(app_config.n_save_slots):
        if i == selected_save_slot:
            save_slot_color = Color.RED
        else:
            save_slot_color = Color.BLACK_L
        slot = Button(x=app_config.save_slot_x_pos[i],
                       y=app_config.save_slot_y_pos,
                       width=app_config.save_slot_width,
                       height=app_config.save_slot_height,
                       color=save_slot_color,
                       text_color=save_slot_color,
                       text=f'Slot {i}')
        save_slots.append(slot)

    return save_slots


def reset_color_tiles(app_config: AppConfig, padding: int = 5) -> list[ColorTile]:
    """
    Create color palette

    Keyword Arguments:
        padding -- spacing between tiles as *int* (default: {5})

    Returns:
        color_tiles that makes up the palette as *list[ColorTile]*
    """
    color_tiles: list[ColorTile] = []
    for i, color in enumerate(Color):
        tile = ColorTile(x=app_config.color_tile_x_pos[i],
                          y=app_config.color_tile_y_pos[i],
                          width=app_config.color_tile_size - padding,
                          height=app_config.color_tile_size,
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


def get_capture_rect(drawing_board_size: int, app_config: AppConfig) -> pygame.Rect:
    """
    Compute pygame.Rect for the drawing board area for capturing the drawing

    Arguments:
        drawing_board_size -- number of tiles on one side of the square drawing board as *int*

    Returns:
        a *pygame.Rect* object representing the position of the drawing board
    """
    min_x = int(
        (app_config.app_width - drawing_board_size * app_config.drawing_tile_size) / 2)
    min_y = 150

    capture_width = drawing_board_size * app_config.drawing_tile_size
    capture_height = drawing_board_size * app_config.drawing_tile_size

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

def reset_instruction_labels(font: pygame.font.Font, app_config: AppConfig):
    save_label_text = 'Ctrl + S:          Save to file'
    clear_label_text = 'Ctrl + Shift + K:  Clear grid'
    load_label_text = 'Ctrl + Shift + L:  Load progress'
    save_progress_label_text = 'Ctrl + Shift + A:  Save progress'

    save_label_surface = font.render(save_label_text, True, (0, 0, 0))
    save_label_rect = save_label_surface.get_rect(bottomleft=(app_config.app_width // 2, app_config.app_height - app_config.margin * 4))

    clear_label_surface = font.render(clear_label_text, True, (0, 0, 0))
    clear_label_rect = clear_label_surface.get_rect(bottomleft=(app_config.app_width // 2, app_config.app_height - app_config.margin * 2))

    load_label_surface = font.render(load_label_text, True, (0, 0, 0))
    load_label_rect = load_label_surface.get_rect(bottomleft=(app_config.app_width // 2, app_config.app_height - app_config.margin * 8))

    save_progress_label_surface = font.render(save_progress_label_text, True, (0, 0, 0))
    save_progress_label_rect = save_progress_label_surface.get_rect(bottomleft=(app_config.app_width // 2, app_config.app_height - app_config.margin * 6))

    return {
        'save_label': (save_label_surface, save_label_rect), 
        'clear_label': (clear_label_surface, clear_label_rect), 
        'load_label': (load_label_surface, load_label_rect), 
        'save_progress_label': (save_progress_label_surface, save_progress_label_rect),
    }

def main():
    """
    main function
    """
    # grid_size_options = [16, 22, 8]
    # cycle_grid_sizes = cycle(grid_size_options)
    # drawing_tile_size = 25
    # n_color_tiles = len(list(Color))
    # n_color_palette_rows = 3
    # n_colors_in_a_row = n_color_tiles // n_color_palette_rows
    # margin = 10
    # n_save_slots: int = 5

    app_width: int = 800
    # color_tile_size: int = int(round((app_width - margin * 2) / n_colors_in_a_row, 0))
    # app_height: int = (
    #     # palette space
    #     (n_color_tiles // n_colors_in_a_row) * color_tile_size + margin * 2 +
    #     max(grid_size_options) * drawing_tile_size + margin * 2 +  # drawing space
    #     200  # label space
    # )

    # total_row_width = n_colors_in_a_row * color_tile_size

    # x_offset = (app_width - total_row_width) // 2

    # color_tile_x_pos: list[int] = [(i % n_colors_in_a_row) * color_tile_size + x_offset for i in range(n_color_tiles)]
    # color_tile_y_pos: list[int] = [i // n_colors_in_a_row *(color_tile_size + 5) + 10 for i in range(n_color_tiles)]

    # save_slot_height: int = margin * 3
    # save_slot_width: int = int(round((app_width - margin * 2) / n_save_slots, 0))
    # save_slot_x_pos: list[int] = [i * save_slot_width + x_offset for i in range(n_save_slots)]
    # save_slot_y_pos: int = app_height - margin * 14

    app_config: AppConfig = AppConfig(app_width = app_width)


    MESSAGE_PROMPT: str = '>>>'

    pygame.init()  # pylint: disable=no-member
    pygame.display.set_caption("Pixlr")
    clock: pygame.time.Clock = pygame.time.Clock()
    screen: pygame.Surface = pygame.display.set_mode((app_config.app_width, app_config.app_height), pygame.RESIZABLE) # pylint: disable=no-member
    font = pygame.font.SysFont(None, app_config.font_size)

    _save_slot: int = 0
    _selected_color: Color = Color.WHITE


    instruction_labels = reset_instruction_labels(font, app_config)

    color_label_surface, color_label_rect = reset_color_label('Hover on a color to display color name and HEX code', font, app_config)

    msg_label_surface, msg_label_rect = reset_msg_label(f'{MESSAGE_PROMPT} Messages are displayed here', color_label_surface, font, app_config)

    color_tiles: list[ColorTile] = reset_color_tiles(app_config, padding = 5)

    save_slots: list[Button] = reset_save_slots(_save_slot, app_config)     # Create save slots

    change_grid_label_surface: pygame.surface.Surface  # pylint: disable=c-extension-no-member
    change_grid_label_rect: pygame.Rect

    drawing_board_size = next(app_config.cycle_grid_sizes)
    drawing_tiles, change_grid_label_surface, change_grid_label_rect = reset_drawing_tiles(drawing_board_size, font, app_config)

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
                app_config = app_config.reset(app_width = app_width)
                instruction_labels = reset_instruction_labels(font, app_config)
                font = pygame.font.SysFont(None, app_config.font_size)
                screen = pygame.display.set_mode((app_config.app_width, app_config.app_height), pygame.RESIZABLE) # pylint: disable=no-member
                color_tiles = reset_color_tiles(app_config, padding = 5)
                drawing_tiles, change_grid_label_surface, change_grid_label_rect = reset_drawing_tiles(drawing_board_size, font, app_config)
                color_label_surface, color_label_rect = reset_color_label('', font, app_config)
                msg_label_surface, msg_label_rect = reset_msg_label(f'{MESSAGE_PROMPT}', color_label_surface, font, app_config)
                save_slots = reset_save_slots(_save_slot, app_config)

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
                save_slots = reset_save_slots(_save_slot, app_config) 

                msg_label_surface, msg_label_rect = reset_msg_label(MESSAGE_PROMPT, color_label_surface, font, app_config)  # wipe prev message after click

            elif event.type == pygame.MOUSEMOTION: # pylint: disable=no-member
                hover_tile_label_text = ''
                # check if mouse is hovering over color palette tiles
                if color_tile := get_hover_tile(color_tiles, event.pos):
                    hover_tile_label_text = f'{color_tile.color.name}: {color_tile.color}'

                # check if mouse is hovering over drawing tiles
                elif drawing_tile := get_hover_tile(drawing_tiles, event.pos):
                    hover_tile_label_text = f'{drawing_tile.color.name}: {drawing_tile.color}'

                # update color label with hover tile color
                color_label_surface, color_label_rect = reset_color_label(hover_tile_label_text, font, app_config)

            elif event.type == pygame.KEYDOWN: # pylint: disable=no-member
                # mod key set up
                ctrl_shift = event.mod & pygame.KMOD_CTRL and event.mod & pygame.KMOD_SHIFT and not event.mod & ~(pygame.KMOD_CTRL | pygame.KMOD_SHIFT) # pylint: disable=no-member
                ctrl = event.mod & pygame.KMOD_CTRL and not event.mod & ~pygame.KMOD_CTRL # pylint: disable=no-member
                keydown_match_message: str = ''

                # change grid size
                if event.key == pygame.K_g and ctrl_shift: # pylint: disable=no-member
                    drawing_board_size = next(app_config.cycle_grid_sizes)
                    drawing_tiles, change_grid_label_surface, change_grid_label_rect = reset_drawing_tiles(drawing_board_size, font, app_config)
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
                    msg_label_surface, msg_label_rect = reset_msg_label(keydown_match_message, color_label_surface, font, app_config)

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

        for label in instruction_labels.values():
            screen.blit(label[0], label[1])

        screen.blit(change_grid_label_surface, change_grid_label_rect)
        screen.blit(color_label_surface, color_label_rect)
        screen.blit(msg_label_surface, msg_label_rect)

        pygame.display.update()

        # Saving image to png needs to be after display.update()
        # because we need to remove the grid and just save the drawing
        if capture_drawing:
            # get drawing surface
            drawing_surface = screen.subsurface(get_capture_rect(drawing_board_size, app_config)).copy()

            save_filename = get_save_filename()

            add_alpha_channel_and_save_captured_drawing(drawing_surface, save_filename) # generate save filename based on datetime

            # print('Image saved!')
            action_complete_message = f'{MESSAGE_PROMPT} Image saved to {save_filename}!'
            capture_drawing = False

        # update message after taking action
        if action_complete_message != '':
            msg_label_surface, msg_label_rect = reset_msg_label(action_complete_message, color_label_surface, font, app_config)

        clock.tick(60)

    pygame.quit()  # pylint: disable=no-member


if __name__ == "__main__":
    main()
