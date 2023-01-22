import pathlib

from arcade import load_texture
from themes.current_theme import *

assets_path = pathlib.Path(__file__).resolve().parent / "tiny_dungeon"

filenames = [
    "tile_0048.png",  # Floor
    "tile_0098.png",  # Player
    "tile_0029.png",
    "tile_0060.png",
    "tile_0000.png",  # WALL
    "tile_0060.png",
    "tile_0060.png",
    "tile_0060.png",
    "tile_0060.png",
    "tile_0045.png",
    "tile_0060.png",
    "tile_0040.png",  # Visible wall
    "tile_0050.png",  # Floor shadowed
    "tile_0015.png",  # Wall right
    "tile_0013.png",  # Wall left
    "tile_0132.png",  # Wall mid
    "tile_0026.png",  # Wall top
    "tile_0059.png",  # Bottom right corner
    "tile_0057.png",  # Bottom left corner
    "tile_0133.png",  # Short wall
    "tile_0058.png",  # Narrow NS wall
    "tile_0134.png",  # Right wall corner
    "tile_0135.png",  # Top cap
    "tile_0136.png",  # Left short wall
    "tile_0137.png",  # Center wall cross
    "tile_0138.png",  # Bottom left corner
    "tile_0139.png",  # Bottom left corner filled
    "tile_0140.png",  # Wall short right
    "tile_0141.png",  # Bottom end cap
    "tile_0026.png",  # Top wall
    "tile_0005.png",  # Top wall right corner
    "tile_0004.png",  # Top wall left corner
    "tile_0015.png",  # Left edge wall
    "tile_0013.png",  # Right edge wall
    "tile_0049.png",  # Floor variation 1
    "tile_0042.png",  # Floor variation 2
    "tile_0051.png",  # Shadow variation


]

# Load  the textures our sprites use on game start-up.
textures = [load_texture(str(assets_path / filename)) for filename in filenames]
