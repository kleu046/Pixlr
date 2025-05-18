import pygame 
from Color import Color

class ColorTiles(pygame.Rect):
    def __init__(self, x, y, width, height, color, text_color=None):
        super().__init__(x, y, width, height)
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, surface, selected_color) -> None:

        if self.color.name == 'WHITE':
            pygame.draw.rect(surface, Color.BLACK, self)
            pygame.draw.rect(surface, self.color, self.inflate(-2, -2))
        else:
            pygame.draw.rect(surface, self.color, self)
        if self.text_color:
            text_surf = self.font.render(
                self.color.name, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.center)
            surface.blit(text_surf, text_rect)

        if selected_color == self.color:
            pygame.draw.rect(surface, Color.BLACK, self.inflate(4, 4), 2)

    def is_clicked(self, pos) -> bool:
        if self.collidepoint(pos):
            return True
        return False


class DrawingTiles(ColorTiles):
    def __init__(self, x, y, width, height, color=Color.WHITE, text_color=None):
        super().__init__(x, y, width, height, color, text_color)

    def draw(self, surface, capture=False) -> None:
        if capture:
            pygame.draw.rect(surface, self.color, self)
        else:
            pygame.draw.rect(surface, Color.LIGHT_METAL, self)
            pygame.draw.rect(surface, self.color, self.inflate(-2, -2))

    def is_clicked(self, pos):
        if self.collidepoint(pos):
            return True
        return False


class Buttons(ColorTiles):
    def __init__(self, x, y, width, height, color, text_color, text):
        super().__init__(x, y, width, height, color, text_color)
        self.text = text
        self.font = pygame.font.SysFont(None, 16)

    def is_clicked(self, pos):
        if self.collidepoint(pos):
            return True
        return False

    def draw(self, surface) -> None:
        if self.text_color and self.text:
            pygame.draw.rect(surface, self.color, self, 1)
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.center)
            surface.blit(text_surf, text_rect)