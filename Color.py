from enum import StrEnum

class Color(StrEnum):
    """
    Class that inherits StrEnum to hold colors used in the app
    """

    # Skin Tones
    LIGHT_SKIN = '#FFE0BD'
    FAIR_SKIN = '#FFCD94'
    TAN_SKIN = '#EAC086'
    BROWN_SKIN = '#C68642'
    DARK_BROWN = '#8D5524'
    VERY_DARK_SKIN = '#4B2E1A'

    # Hair & Eyes
    BLACK = '#000020'
    DARK_GRAY = '#4B4B4B'
    BROWN = '#A0522D'
    BLONDE = '#FFD700'
    SILVER = '#A9A9A9'
    AUBURN = '#5B3C11'

    # Clothing
    CRIMSON = '#8B0000'
    RED = '#DC143C'
    ORANGE = '#FFA500'
    YELLOW = '#FFFF00'
    DARK_GREEN = '#006400'
    BRIGHT_GREEN = '#00FF00'
    NAVY = '#00008B'
    ROYAL_BLUE = '#4169E1'
    PURPLE = '#8A2BE2'
    PINK = '#FF69B4'
    SLATE_GRAY = '#708090'
    OFF_WHITE = '#FFFFAA'

    # Metal/Utility/Outline
    STEEL = '#B0C4DE'
    LIGHT_METAL = '#C0C0C0'
    GOLD = '#FFEB3B'
    OUTLINE = '#2F2F2F'

    # Environment
    DIRT = '#8B4513'
    WATER = '#00CED1'
    STONE = '#7D7D75'
    GRASS = '#66BB66'

    # lighter set
    # lighter skin tones
    LIGHT_SKIN_L = '#FFF1E3'
    FAIR_SKIN_L = '#FFE4C8'
    TAN_SKIN_L = '#F8DDB5'
    BROWN_SKIN_L = '#E6B988'
    DARK_BROWN_L = '#C38C5A'
    VERY_DARK_SKIN_L = '#8A5B3A'

    # lighter hair & eyes
    BLACK_L = '#404060'
    DARK_GRAY_L = '#909090'
    BROWN_L = '#C98B60'
    BLONDE_L = '#E6E600'
    SILVER_L = '#E6E6E6'
    AUBURN_L = '#996B3A'

    # lighter clothing
    CRIMSON_L = '#C83232'
    RED_L = '#F2757F'
    ORANGE_L = '#FFCC66'
    YELLOW_L = '#FFFF44'
    DARK_GREEN_L = '#44AA44'
    BRIGHT_GREEN_L = '#99FF99'
    NAVY_L = '#4C4CBB'
    ROYAL_BLUE_L = '#92AFFF'
    PURPLE_L = '#C78DF2'
    PINK_L = '#FFA3D3'
    SLATE_GRAY_L = '#AAB9C2'
    OFF_WHITE_L = '#FFFFCC'

    # lighter metal/utility/outline
    STEEL_L = '#D8E4F0'
    LIGHT_METAL_L = '#EAEAEA'
    GOLD_L = '#FFE066'
    OUTLINE_L = '#6A6A6A'

    # lighter environment
    DIRT_L = '#B46A3B'
    WATER_L = '#66E8E9'
    STONE_L = '#BFBFB7'
    GRASS_L = '#A8EFA8'

    # lightest skin tones
    LIGHT_SKIN_LL = '#FFF8F1'
    FAIR_SKIN_LL = '#FFEEDC'
    TAN_SKIN_LL = '#FAEACF'
    BROWN_SKIN_LL = '#F1D4B1'
    DARK_BROWN_LL = '#D7AB82'
    VERY_DARK_SKIN_LL = '#B07B59'

    # lightest hair & eyes
    BLACK_LL = '#606080'
    DARK_GRAY_LL = '#B0B0B0'
    BROWN_LL = '#DEB9A1'
    BLONDE_LL = '#FFF799'
    SILVER_LL = '#F5F5F5'
    AUBURN_LL = '#B98B5B'

    # lightest clothing
    CRIMSON_LL = '#E05B5B'
    RED_LL = '#F8A7AE'
    ORANGE_LL = '#FFE599'
    YELLOW_LL = '#FFFF99'
    DARK_GREEN_LL = '#77CC77'
    BRIGHT_GREEN_LL = '#CCFFCC'
    NAVY_LL = '#8080DD'
    ROYAL_BLUE_LL = '#BFD1FF'
    PURPLE_LL = '#E3BDF8'
    PINK_LL = '#FFC7E5'
    SLATE_GRAY_LL = '#C6D1D8'
    OFF_WHITE_LL = '#FFFFF5'

    # lightest metal/utility/outline
    STEEL_LL = '#EAF1F8'
    LIGHT_METAL_LL = '#E0E0E0'
    GOLD_LL = '#FFFCCD'
    OUTLINE_LL = '#D1D1D1'

    # lightest environment
    DIRT_LL = '#C98A5C'
    WATER_LL = '#99F2F3'
    STONE_LL = '#DCDCD6'
    GRASS_LL = '#CFF8CF'

    # eraser
    WHITE = '#FFFFFF'
