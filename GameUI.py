"""
Manages and draws Game UI
"""
import pygame

from GameConfig import GameConfig
from Tiles import ColorTile, DrawingTile, Button
from Color import Color

class GameUI:
    """
    Game UI class
    """
    def __init__(self, game_config: GameConfig) -> None:
        pygame.init()  # pylint: disable=no-member
        self.game_config = game_config
        self.font = pygame.font.SysFont(None, game_config.font_size)
        self.screen: pygame.Surface = pygame.display.set_mode((game_config.app_width, game_config.app_height), pygame.RESIZABLE) # pylint: disable=no-member
        self.instruction_labels: list[tuple[pygame.Surface, pygame.Rect]] = self.reset_instruction_pane()
        self.change_grid_size_label: tuple[pygame.Surface, pygame.Rect] = self.reset_change_grid_size_label()
        self.color_label: tuple[pygame.Surface, pygame.Rect] = self.reset_color_label()
        self.msg_label: tuple[pygame.Surface, pygame.Rect] = self.reset_msg_label()
        self.palette: list[ColorTile] = self.reset_palette()
        self.drawing_board: list[DrawingTile] = self.reset_drawing_board()
        self.save_slots: list[Button] = self.reset_save_slots()

    def reset_window(self, game_config: GameConfig) -> None:
        """
        Reset GameUI

        Arguments:
            game_config -- *GameConfig* object
        """
        self.game_config = game_config
        self.font = pygame.font.SysFont(None, self.game_config.font_size)
        self.screen = pygame.display.set_mode((self.game_config.app_width, self.game_config.app_height), pygame.RESIZABLE) # pylint: disable=no-member


    def reset_instruction_pane(self) -> list[tuple[pygame.Surface, pygame.Rect]]:
        """
        Reset instruction labels

        Returns:
            --description
        """
        label_texts = {
            'clear_label_text':         'Clear grid: Ctrl + Shift + K',
            'load_label_text':          'Load: Ctrl + Shift + L',
            'save_progress_label_text': 'Save: Ctrl + Shift + A',
            'save_label_text':          'Capture: Ctrl + S',
        }

        instruction_labels = []
        for i, lt in enumerate(label_texts):
            surf = self.font.render(label_texts[lt], True, (0, 0, 0))
            y_offset = 2 + 2 * i
            rect = surf.get_rect(bottomleft=(self.game_config.app_width // 2, self.game_config.app_height - self.game_config.margin * y_offset))
            instruction_labels.append((surf,rect))

        self.instruction_labels = instruction_labels # assign to self.instruction_label directly

        return instruction_labels


    def reset_change_grid_size_label(self) -> tuple[pygame.Surface, pygame.Rect]:
        """
        Reset change grid size label

        Returns:
            --description
        """
        change_grid_label_text = f'Ctrl + Shift + G: Change grid size | Current: {self.game_config.drawing_board_size}'
        change_grid_label_surface = self.font.render(change_grid_label_text, True, (0, 0, 0))
        change_grid_label_rect = change_grid_label_surface.get_rect(bottomleft=(self.game_config.margin * 3, self.game_config.app_height - self.game_config.margin * 4))

        self.change_grid_size_label = (change_grid_label_surface, change_grid_label_rect)

        return change_grid_label_surface, change_grid_label_rect

    def reset_color_label(self, hover_tile: ColorTile | DrawingTile | None = None) -> tuple[pygame.Surface, pygame.Rect]:
        """
        reset and redraw color name and hex code on label

        Returns:
            _description_
        """
        if hover_tile:
            color_label_text = f'{hover_tile.color.name}: {hover_tile.color}'
        else:
            color_label_text = 'Hover over a color to see its name and hex code'
        color_label_surface = self.font.render(color_label_text, True, (0, 0, 0))
        color_label_rect = color_label_surface.get_rect(bottomleft=(self.game_config.margin * 3, self.game_config.app_height - self.game_config.margin * 6))

        self.color_label = (color_label_surface, color_label_rect)

        return color_label_surface, color_label_rect


    def reset_msg_label(self, msg_label_text: str = '', msg_label_prompt='>>>') -> tuple[pygame.Surface, pygame.Rect]:
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
        msg_label_surface = self.font.render(' '.join([msg_label_prompt, msg_label_text]), True, (0, 0, 0))
        msg_label_rect = msg_label_surface.get_rect(bottomleft=(self.game_config.margin * 3, self.game_config.app_height - self.game_config.margin * 2))

        self.msg_label = (msg_label_surface, msg_label_rect)

        return msg_label_surface, msg_label_rect

    def reset_palette(self, padding: int = 5) -> list[ColorTile]:
        """
        Create color palette

        Keyword Arguments:
            padding -- spacing between tiles as *int* (default: {5})

        Returns:
            palette that makes up the palette as *list[ColorTile]*
        """
        palette: list[ColorTile] = []
        for i, color in enumerate(Color):
            tile = ColorTile(x=self.game_config.color_tile_x_pos[i],
                            y=self.game_config.color_tile_y_pos[i],
                            width=self.game_config.color_tile_size - padding,
                            height=self.game_config.color_tile_size,
                            color=color)
            palette.append(tile)

        self.palette = palette

        return palette

    def reset_drawing_board(self, drawing_board: list[DrawingTile] | None = None, tile_colors: list[Color] | None = None) -> list[DrawingTile]:
        """
        Redraw drawing tiles according to drawing_board_size

        Returns:
            drawing_board - *list[DrawingTile]* redraw drawing board if provided. e.g. used when resizing
            tile_colors - *list[Color]* used to reload work saved
        """
        new_drawing_board = []

        # Create DrawingTile
        for i in range(self.game_config.drawing_board_size):
            for j in range(self.game_config.drawing_board_size):
                if tile_colors:
                    color = tile_colors[i * self.game_config.drawing_board_size + j]
                else:
                    color = drawing_board[i * self.game_config.drawing_board_size + j].color if drawing_board else Color.WHITE
                tile = DrawingTile(
                    x = i * self.game_config.drawing_tile_size +
                    int(self.game_config.app_width - self.game_config.drawing_board_size * self.game_config.drawing_tile_size) / 2,
                    y = j * self.game_config.drawing_tile_size + int(self.game_config.app_width / 5.5),
                    width = self.game_config.drawing_tile_size,
                    height = self.game_config.drawing_tile_size,
                    color = color)
                new_drawing_board.append(tile)

        self.drawing_board = new_drawing_board

        return new_drawing_board

    def reset_save_slots(self, active_save_slot: int = 0) -> list[Button]:
        """
        Redraw save slot buttons based on selected save slot

        Arguments:
            selected_save_slot -- index of save slot as *int*

        Returns:
            save_slots - *list[Button]*
        """
        save_slots: list[Button] = []
        for i in range(self.game_config.n_save_slots):
            if i == active_save_slot:
                save_slot_color = Color.RED
            else:
                save_slot_color = Color.BLACK_L
            slot = Button(x=self.game_config.save_slot_x_pos[i],
                        y=self.game_config.save_slot_y_pos,
                        width=self.game_config.save_slot_width,
                        height=self.game_config.save_slot_height,
                        color=save_slot_color,
                        text_color=save_slot_color,
                        text=f'Slot {i}')
            save_slots.append(slot)

        self.save_slots = save_slots

        return save_slots

    def draw(self, active_color: Color, capture_drawing: bool = False) -> None:
        """
        Update UI
        """
        # instruction labels
        for label in self.instruction_labels:
            self.screen.blit(label[0], label[1])

        self.screen.blit(self.change_grid_size_label[0], self.change_grid_size_label[1])

        self.screen.blit(self.color_label[0], self.color_label[1])

        self.screen.blit(self.msg_label[0], self.msg_label[1])

        for tile in self.palette:
            tile.draw(self.screen, active_color)

        for tile in self.drawing_board:
            tile.draw(self.screen, capture_drawing)

        for sl in self.save_slots:
            sl.draw(self.screen)
