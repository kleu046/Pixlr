"""
Prescribe, compute and stores game configuration and parameters
"""
from dataclasses import dataclass, field
from itertools import cycle
from Color import Color

@dataclass
class GameConfig:
    """
    App configuration dataclass
    """
    app_width: int # 800

    font_size: int = field(init=False) # 14

    grid_size_options: tuple[int, int, int] = (16, 22, 8)
    cycle_grid_sizes:  cycle = cycle(grid_size_options)
    drawing_board_size: int = next(cycle_grid_sizes)
    drawing_tile_size: int = field(init=False) # 25
    n_palette: int = len(list(Color))
    n_color_palette_rows: int = 3
    n_colors_in_a_row: int = n_palette // n_color_palette_rows
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
        self.check_width_constraint(665, 1004)

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
        Reset GameConfig

        Returns:
            _description_
        """
        cls._instance = None
        return cls(*args, **kwargs)

    def next_grid_size(self) -> None:
        """
        Get next grid size

        Returns:
            _description_
        """
        self.drawing_board_size = next(self.cycle_grid_sizes)


    def check_width_constraint(self, min_width, max_width) -> None:
        """
        Check if app_width is within the constraint
        """
        if self.app_width < min_width:
            self.app_width = min_width
        elif self.app_width > max_width:
            self.app_width = max_width

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
        return [(i % self.n_colors_in_a_row) * self.color_tile_size + self.x_offset for i in range(self.n_palette)], \
            [i // self.n_colors_in_a_row *(self.color_tile_size + int(self.margin / 2)) + self.margin for i in range(self.n_palette)]

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
            (self.n_palette // self.n_colors_in_a_row) * self.color_tile_size + self.margin * 2 +
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
