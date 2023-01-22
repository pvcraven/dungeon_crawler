from entities.entity import Entity
from themes.current_theme import *
from entities.item import Item


class Potion(Entity):
    def __init__(self, column: int = 0, row: int = 0):
        super().__init__(
            column,
            row,
            texture_id=POTION_TEXTURE_ID,
            color=colors["transparent"],
            visible_color=colors["potion"],
            name="Healing Potion",
            item=Item(),
        )

    def use(self, game_engine):
        game_engine.player.fighter.hp += 5
        if game_engine.player.fighter.hp > game_engine.player.fighter.max_hp:
            game_engine.player.fighter.hp = game_engine.player.fighter.max_hp
        game_engine.player.inventory.remove_item(self)

        return [{"enemy_turn": True}, {"play_sound": "heal"}]
