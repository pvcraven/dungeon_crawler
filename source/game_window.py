"""
Main Game Engine
"""
import arcade
import pyglet.gl as gl

from game_map import GameMap
from constants import *
from entity import Entity
from recalculate_fov import recalculate_fov
from fighter import Fighter
from util import get_blocking_sprites
from status_bar import draw_status_bar
from inventory import Inventory


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title, antialiasing=False)

        arcade.set_background_color(arcade.color.BLACK)
        self.game_map = None
        self.player = None

        self.characters = None
        self.entities = None
        self.dungeon_sprites = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.up_left_pressed = False
        self.up_right_pressed = False
        self.down_left_pressed = False
        self.down_right_pressed = False

        self.messages = []

        self.time_since_last_move_check = 0

        self.action_queue = []
        self.mouse_over_text = None
        self.mouse_position = None

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        # Set game state
        # Create sprite lists
        self.characters = arcade.SpriteList()
        self.dungeon_sprites = arcade.SpriteList(
            use_spatial_hash=True, spatial_hash_cell_size=16
        )
        self.entities = arcade.SpriteList(
            use_spatial_hash=True, spatial_hash_cell_size=16
        )

        # Create player
        fighter_component = Fighter(hp=30, defense=2, power=5)
        self.player = Entity(
            x=0,
            y=0,
            char="@",
            color=arcade.csscolor.WHITE,
            fighter=fighter_component,
            name="Player",
            inventory=Inventory(capacity=5),
        )
        self.characters.append(self.player)

        # --- Create map
        # Size of the map
        map_width = MAP_WIDTH
        map_height = MAP_HEIGHT

        # Some variables for the rooms in the map
        room_max_size = 10
        room_min_size = 6
        max_rooms = 30

        self.game_map = GameMap(map_width, map_height)
        self.game_map.make_map(
            max_rooms=max_rooms,
            room_min_size=room_min_size,
            room_max_size=room_max_size,
            map_width=map_width,
            map_height=map_height,
            player=self.player,
            entities=self.entities,
            max_monsters_per_room=3,
            max_items_per_room=2,
        )

        # Take the tiles and make sprites out of them
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                wall = self.game_map.tiles[x][y].block_sight
                sprite = Entity(x, y, WALL_CHAR, arcade.csscolor.BLACK)
                if wall:
                    sprite.name = "Wall"
                    sprite.block_sight = True
                    sprite.blocks = True
                    sprite.visible_color = colors["light_wall"]
                    sprite.not_visible_color = colors["dark_wall"]
                else:
                    sprite.name = "Ground"
                    sprite.block_sight = False
                    sprite.visible_color = colors["light_ground"]
                    sprite.not_visible_color = colors["dark_ground"]

                self.dungeon_sprites.append(sprite)

        # Set field of view
        recalculate_fov(
            self.player.x,
            self.player.y,
            FOV_RADIUS,
            [self.dungeon_sprites, self.entities],
        )

    def on_draw(self):
        """
        Render the screen.
        """
        try:
            arcade.start_render()

            # Draw the sprites
            self.dungeon_sprites.draw(filter=gl.GL_NEAREST)
            self.entities.draw(filter=gl.GL_NEAREST)
            self.characters.draw(filter=gl.GL_NEAREST)

            # Draw the status panel
            arcade.draw_xywh_rectangle_filled(
                0,
                0,
                SCREEN_WIDTH,
                STATUS_PANEL_HEIGHT,
                colors["status_panel_background"],
            )
            text = f"HP: {self.player.fighter.hp}/{self.player.fighter.max_hp}"
            arcade.draw_text(text, 0, 0, colors["status_panel_text"])
            size = 65
            margin = 2
            draw_status_bar(
                size / 2 + margin,
                24,
                size,
                10,
                self.player.fighter.hp,
                self.player.fighter.max_hp,
            )
            capacity = self.player.inventory.capacity
            for i in range(capacity):
                y = 40
                x = i * SCREEN_WIDTH / (capacity + 1)
                if self.player.inventory.items[i]:
                    item_name = self.player.inventory.items[i].name
                else:
                    item_name = ""
                text = f"{i+1}: {item_name}"
                arcade.draw_text(text, x, y, colors["status_panel_text"])
            # Check message queue. Limit to 2 lines
            while len(self.messages) > 2:
                self.messages.pop(0)

            # Draw messages
            y = 20
            for message in self.messages:
                arcade.draw_text(message, 200, y, colors["status_panel_text"])
                y -= 20

            # Draw mouse-over text
            if self.mouse_over_text:
                x, y = self.mouse_position
                arcade.draw_xywh_rectangle_filled(x, y, 100, 16, arcade.color.BLACK)
                arcade.draw_text(self.mouse_over_text, x, y, arcade.csscolor.WHITE)
        except Exception as e:
            print(e)

    def move_player(self, cx, cy):
        nx = self.player.x + cx
        ny = self.player.y + cy
        blocking_dungeon_sprites = get_blocking_sprites(nx, ny, self.dungeon_sprites)
        blocking_entity_sprites = get_blocking_sprites(nx, ny, self.entities)
        if not blocking_dungeon_sprites and not blocking_entity_sprites:
            self.player.x += cx
            self.player.y += cy
            recalculate_fov(
                self.player.x,
                self.player.y,
                FOV_RADIUS,
                [self.dungeon_sprites, self.entities],
            )
            return [{"enemy_turn": True}]
        elif blocking_entity_sprites:
            target = blocking_entity_sprites[0]
            attack_results = self.player.fighter.attack(target)
            attack_results.extend([{"enemy_turn": True}])
            return attack_results

        return None

    def on_key_press(self, key: int, modifiers: int):
        """ Manage keyboard input """
        self.time_since_last_move_check = None
        if key in KEYMAP_UP:
            self.up_pressed = True
        elif key in KEYMAP_DOWN:
            self.down_pressed = True
        elif key in KEYMAP_LEFT:
            self.left_pressed = True
        elif key in KEYMAP_RIGHT:
            self.right_pressed = True
        elif key in KEYMAP_UP_LEFT:
            self.up_left_pressed = True
        elif key in KEYMAP_UP_RIGHT:
            self.up_right_pressed = True
        elif key in KEYMAP_DOWN_LEFT:
            self.down_left_pressed = True
        elif key in KEYMAP_DOWN_RIGHT:
            self.down_right_pressed = True
        elif key in KEYMAP_PICKUP:
            self.action_queue.extend([{"pickup": True}])
        elif key in KEYMAP_USE_ITEM_1:
            self.action_queue.extend([{"use_item": 0}])
        elif key in KEYMAP_USE_ITEM_2:
            self.action_queue.extend([{"use_item": 1}])
        elif key in KEYMAP_USE_ITEM_3:
            self.action_queue.extend([{"use_item": 2}])
        elif key in KEYMAP_USE_ITEM_4:
            self.action_queue.extend([{"use_item": 3}])
        elif key in KEYMAP_USE_ITEM_5:
            self.action_queue.extend([{"use_item": 4}])
        elif key in KEYMAP_USE_ITEM_6:
            self.action_queue.extend([{"use_item": 5}])
        elif key in KEYMAP_USE_ITEM_7:
            self.action_queue.extend([{"use_item": 6}])
        elif key in KEYMAP_USE_ITEM_8:
            self.action_queue.extend([{"use_item": 7}])
        elif key in KEYMAP_USE_ITEM_9:
            self.action_queue.extend([{"use_item": 8}])
        elif key in KEYMAP_USE_ITEM_0:
            self.action_queue.extend([{"use_item": 9}])

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key in KEYMAP_UP:
            self.up_pressed = False
        elif key in KEYMAP_DOWN:
            self.down_pressed = False
        elif key in KEYMAP_LEFT:
            self.left_pressed = False
        elif key in KEYMAP_RIGHT:
            self.right_pressed = False
        elif key in KEYMAP_UP_LEFT:
            self.up_left_pressed = False
        elif key in KEYMAP_UP_RIGHT:
            self.up_right_pressed = False
        elif key in KEYMAP_DOWN_LEFT:
            self.down_left_pressed = False
        elif key in KEYMAP_DOWN_RIGHT:
            self.down_right_pressed = False

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouse_position = x, y
        sprite_list = arcade.get_sprites_at_point((x, y), self.entities)
        self.mouse_over_text = None
        for sprite in sprite_list:
            if isinstance(sprite, Entity):
                if sprite.fighter and sprite.is_visible:
                    self.mouse_over_text = (
                        f"{sprite.name} {sprite.fighter.hp}/{sprite.fighter.max_hp}"
                    )
            else:
                raise TypeError("Sprite is not an instance of Entity class.")

    def move_enemies(self):
        full_results = []
        for entity in self.entities:
            if entity.ai:
                results = entity.ai.take_turn(
                    target=self.player,
                    sprite_lists=[self.dungeon_sprites, self.entities],
                )
                full_results.extend(results)
        return full_results

    def check_for_player_movement(self):
        if self.player.is_dead:
            return

        self.time_since_last_move_check = 0
        cx = 0
        cy = 0

        if self.up_pressed or self.up_left_pressed or self.up_right_pressed:
            cy += 1
        if self.down_pressed or self.down_left_pressed or self.down_right_pressed:
            cy -= 1

        if self.left_pressed or self.down_left_pressed or self.up_left_pressed:
            cx -= 1
        if self.right_pressed or self.down_right_pressed or self.up_right_pressed:
            cx += 1

        if cx or cy:
            results = self.move_player(cx, cy)
            if results:
                self.action_queue.extend(results)

    def on_update(self, dt):

        if self.time_since_last_move_check is not None:
            self.time_since_last_move_check += dt

        if (
            self.time_since_last_move_check is None
            or self.time_since_last_move_check > 0.3
        ):
            self.check_for_player_movement()

        new_action_queue = []
        for action in self.action_queue:
            if "enemy_turn" in action:
                new_actions = self.move_enemies()
                if new_actions:
                    new_action_queue.extend(new_actions)
            if "message" in action:
                print(action["message"])
                self.messages.append(action["message"])
            if "dead" in action:
                target = action["dead"]
                target.color = colors["dying"]
                # target.visible_color = colors["dying"]
                target.is_dead = True
                if target is self.player:
                    new_action_queue.extend([{"message": "Player has died!"}])
                else:
                    new_action_queue.extend(
                        [{"message": f"{target.name} has been killed!"}]
                    )
                    new_action_queue.extend(
                        [{"delay": {"time": DEATH_DELAY, "action": {"remove": target}}}]
                    )
            if "remove" in action:
                target = action["remove"]
                target.char = "X"
                target.color = colors["dead_body"]
                target.visible_color = colors["dead_body"]
                target.blocks = False
            if "delay" in action:
                target = action["delay"]
                target["time"] -= dt
                if target["time"] > 0:
                    new_action_queue.extend([{"delay": target}])
                else:
                    new_action_queue.extend([target["action"]])
            if "pickup" in action:
                entities = arcade.get_sprites_at_exact_point(
                    self.player.position, self.entities
                )
                for entity in entities:
                    if isinstance(entity, Entity):
                        if entity.item:
                            results = self.player.inventory.add_item(entity)
                            if results:
                                new_action_queue.extend(results)
                    else:
                        raise ValueError("Sprite is not an instance of Entity.")

            if "use_item" in action:
                item_number = action["use_item"]
                item = self.player.inventory.get_item_number(item_number)
                if item:
                    if item.name == "Healing Potion":
                        self.player.fighter.hp += 5
                        if self.player.fighter.hp > self.player.fighter.max_hp:
                            self.player.fighter.hp = self.player.fighter.max_hp
                        self.player.inventory.remove_item_number(item_number)

        self.action_queue = new_action_queue


def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()