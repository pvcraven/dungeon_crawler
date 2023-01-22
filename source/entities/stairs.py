import arcade
from entities.entity import Entity


class Stairs(Entity):
    def __init__(self,
                 column: int = 0,
                 row: int = 0,
                 texture_id: int = 0,
                 color=arcade.csscolor.WHITE,
                 visible_color=arcade.csscolor.WHITE,
                 not_visible_color=arcade.csscolor.WHITE,
                 name=None,
                 blocks=False,
                 fighter=None,
                 ai=None,
                 inventory=None,
                 item=None,
                 floor: int = 0):
        super().__init__(column, row, texture_id, color, visible_color, not_visible_color, name, blocks, fighter, ai, inventory, item)
        self.floor = floor

    def get_dict(self):
        dict = super().get_dict()
        dict['floor'] = self.floor
        return dict

    def restore_from_dict(self, result):
        super().restore_from_dict(result)
        self.floor = result['floor']

