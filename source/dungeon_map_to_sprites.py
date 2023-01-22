from typing import List
import random
import arcade

from constants import *
from themes.current_theme import *

from entities.entity import Entity
from entities.lightning_scroll import LightningScroll
from entities.fireball_scroll import FireballScroll
from entities.potion import Potion
from entities.stairs import Stairs
from entities.creature_factory import get_random_monster_by_challenge
from entities.creature_factory import make_monster_sprite
from load_map.dungeon_map import DungeonMap


def dungeon_map_to_sprites(game_map: DungeonMap) -> arcade.SpriteList:
    """ Take a grid of numbers and convert to sprites. """
    sprite_list = arcade.SpriteList(use_spatial_hash=True, spatial_hash_cell_size=16)

    # Take the tiles and make sprites out of them
    for row in range(game_map.map_height):
        for column in range(game_map.map_width):
            sprite = None
            reversed_row = game_map.map_height - row
            #
            # if reversed_row == 13 and column == 34:
            #     print("Ping")

            is_empty = False
            tile = game_map.tiles[row][column]
            if (tile.corridor or tile.room) and not tile.door:
                is_empty = True

            left_empty = False
            if column > 0:
                tile = game_map.tiles[row][column - 1]
                if (tile.corridor or tile.room) and not tile.door:
                    left_empty = True

            right_empty = False
            if column < game_map.map_width - 1:
                tile = game_map.tiles[row][column + 1]
                if (tile.corridor or tile.room) and not tile.door:
                    right_empty = True

            below_empty = False
            if row < game_map.map_height - 1:
                tile = game_map.tiles[row + 1][column]
                if (tile.corridor or tile.room) and not tile.door:
                    below_empty = True

            above_empty = False
            if row > 0:
                tile = game_map.tiles[row - 1][column]
                if (tile.corridor or tile.room) and not tile.door:
                    above_empty = True

            nw_empty = False
            if row > 0 and column > 0:
                tile = game_map.tiles[row - 1][column - 1]
                if (tile.corridor or tile.room) and not tile.door:
                    nw_empty = True

            ne_empty = False
            if row > 0 and column < game_map.map_width - 1:
                tile = game_map.tiles[row - 1][column + 1]
                if (tile.corridor or tile.room) and not tile.door:
                    ne_empty = True

            sw_empty = False
            if row < game_map.map_height - 1 and column > 0:
                tile = game_map.tiles[row + 1][column - 1]
                if (tile.corridor or tile.room) and not tile.door:
                    sw_empty = True

            se_empty = False
            if row < game_map.map_height - 1 and column < game_map.map_width - 1:
                tile = game_map.tiles[row + 1][column + 1]
                if (tile.corridor or tile.room) and not tile.door:
                    se_empty = True

            if reversed_row == 13 and column == 34:
                print()
                print(nw_empty, above_empty, ne_empty)
                print(left_empty, is_empty, right_empty)
                print(sw_empty, below_empty, se_empty)

            # if reversed_row == 13 and column == 34:
            #     print("Ping")
            #     texture_id = 2
            #     sprite = Entity(row=reversed_row, column=column, texture_id=texture_id, color=colors['transparent'])
            #     sprite.block_sight = True
            #     sprite.blocks = False
            #     sprite.visible_color = colors["light_wall"]
            #     sprite.not_visible_color = colors["dark_wall"]
            if game_map.tiles[row][column].door:
                texture_id = DOOR_NS_CLOSED
                sprite = Entity(row=reversed_row, column=column, texture_id=texture_id, color=colors['transparent'])
                sprite.name = "Door NS Closed"
                sprite.block_sight = True
                sprite.blocks = False
                sprite.visible_color = colors["light_wall"]
                sprite.not_visible_color = colors["dark_wall"]
            elif not is_empty:
                texture_id = WALL_TEXTURE_ID

                if not left_empty and not right_empty and not above_empty and sw_empty and se_empty and ne_empty and nw_empty:
                    texture_id = CENTER_WALL_CROSS
                elif not below_empty and left_empty and right_empty and sw_empty and se_empty and above_empty:
                    texture_id = TOP_CAP
                elif nw_empty and ne_empty and not above_empty and right_empty and not left_empty and below_empty:
                    texture_id = WALL_RIGHT_CORNER
                elif left_empty and not right_empty and above_empty and below_empty:
                    texture_id = LEFT_SHORT_WALL
                elif below_empty and not right_empty and not left_empty and above_empty:
                    texture_id = WALL_SHORT
                elif not below_empty and above_empty and sw_empty and se_empty and not right_empty and not left_empty:
                    texture_id = WALL_SHORT
                # elif below_empty and not right_empty and left_empty and not above_empty and not ne_empty:
                #     texture_id = BOTTOM_LEFT_CORNER_FILLED
                elif below_empty and not right_empty and left_empty and not above_empty and ne_empty:
                    texture_id = BOTTOM_LEFT_CORNER_HOLLOW
                elif not right_empty and left_empty and nw_empty and ne_empty and not above_empty and se_empty:
                    texture_id = BOTTOM_LEFT_CORNER_HOLLOW
                elif below_empty and right_empty and not left_empty and above_empty:
                    texture_id = WALL_SHORT_RIGHT
                elif not below_empty and not above_empty and left_empty and right_empty:
                    texture_id = WALL_MID_ID
                elif not below_empty and not above_empty and not left_empty and right_empty and nw_empty and sw_empty:
                    texture_id = WALL_RIGHT_CORNER
                elif left_empty and above_empty and se_empty:
                    texture_id = LEFT_SHORT_WALL
                elif not left_empty and above_empty and right_empty and (below_empty or sw_empty):
                    texture_id = WALL_SHORT_RIGHT
                elif left_empty and right_empty and not above_empty and below_empty and ne_empty and nw_empty:
                    texture_id = BOTTOM_END_CAP
                elif above_empty and not below_empty and not left_empty and not right_empty and not se_empty and not sw_empty:
                    texture_id = TOP_WALL
                elif above_empty and not below_empty and not left_empty and right_empty:
                    texture_id = TOP_WALL_RIGHT_CORNER
                elif above_empty and not below_empty and left_empty and not right_empty:
                    texture_id = TOP_WALL_LEFT_CORNER
                elif not above_empty and not right_empty and left_empty:
                    texture_id = LEFT_EDGE_WALL
                elif not left_empty and not right_empty and nw_empty and not ne_empty and sw_empty:
                    texture_id = LEFT_EDGE_WALL
                elif not above_empty and right_empty and not left_empty:
                    texture_id = RIGHT_EDGE_WALL
                elif not above_empty and ne_empty and not right_empty and se_empty and not left_empty:
                    texture_id = RIGHT_EDGE_WALL

                sprite = Entity(row=reversed_row, column=column, texture_id=texture_id, color=colors['transparent'])
                sprite.name = "Wall"
                sprite.block_sight = True
                sprite.blocks = True
                sprite.visible_color = colors["light_wall"]
                sprite.not_visible_color = colors["dark_wall"]
            elif game_map.tiles[row][column].corridor or game_map.tiles[row][column].room:
                texture_id = FLOOR_TEXTURE_ID
                if not above_empty:
                    if random.randrange(10) == 0:
                        texture_id = SHADOW_VARIATION
                    else:
                        texture_id = FLOOR_SHADOWED_ID
                elif random.randrange(15) == 0:
                    texture_id = FLOOR_VARIATION_1
                elif random.randrange(35) == 0:
                    texture_id = FLOOR_VARIATION_2
                sprite = Entity(row=reversed_row, column=column, texture_id=texture_id, color=colors['transparent'])
                sprite.name = "Ground"
                sprite.block_sight = False
                sprite.visible_color = colors["light_ground"]
                sprite.not_visible_color = colors["dark_ground"]
            elif game_map.tiles[row][column].stair_down:
                sprite = Stairs(row=reversed_row, column=column, texture_id=STAIRS_DOWN_TEXTURE_ID, color=colors['transparent'])
                sprite.name = "Stairs Down"
                sprite.block_sight = False
                sprite.visible_color = colors["light_ground"]
                sprite.not_visible_color = colors["dark_ground"]
            # elif game_map.tiles[row][column] == TILE.HEALING_POTION:
            #     sprite = Potion(column, row)
            # elif game_map.tiles[row][column] == TILE.LIGHTNING_SCROLL:
            #     sprite = LightningScroll(column, row)
            # elif game_map.tiles[row][column] == TILE.FIREBALL_SCROLL:
            #     sprite = FireballScroll(column, row)
            # elif game_map.tiles[row][column]:
            #     raise ValueError(f"Unknown number in map: {game_map[column][row]}")

            if sprite:
                sprite_list.append(sprite)

    return sprite_list


def creatures_to_sprites(game_map: DungeonMap) -> arcade.SpriteList:
    """ Take a grid of numbers and convert to sprites. """
    sprite_list = arcade.SpriteList(use_spatial_hash=True, spatial_hash_cell_size=16)
#
#     # Take the tiles and make sprites out of them
#     for y in range(len(game_map[0])):
#         for x in range(len(game_map)):
#
#             if game_map[x][y]:
#                 m = get_random_monster_by_challenge(game_map[x][y])
#                 sprite = make_monster_sprite(m)
#                 sprite.x = x
#                 sprite.y = y
#                 sprite.alpha = 0
#                 sprite.visible_color = colors['monster']
#
#                 sprite_list.append(sprite)
#
    return sprite_list
