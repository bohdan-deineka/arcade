import arcade

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 2
PLAYER_JUMP_SPEED = 20


class Game(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.coin_list = None
        self.wall_list = None
        self.player_list = None

        self.player_sprite = None

        self.physics_engine = None

        arcade.set_background_color(arcade.csscolor.BLACK)

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.coin_list = arcade.SpriteList(use_spatial_hash=True)

        image_source = "images/character/GraveRobber.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 24
        self.player_sprite.center_y = 48
        self.player_list.append(self.player_sprite)

        for x in range(0, 1250, 24):
            wall = arcade.Sprite("images/tiles/tile22.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 12
            self.wall_list.append(wall)

        coordinate_list = [[128, 31],
                           [256, 31],
                           [384, 31],
                           [512, 31],
                           [640, 31],
                           [768, 31]]

        for coordinate in coordinate_list:
            wall = arcade.Sprite("images/Objects/barrel.png", TILE_SCALING)
            wall.position = coordinate
            self.wall_list.append(wall)

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             GRAVITY)
    def on_draw(self):
        arcade.start_render()

        self.player_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
                   self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
                   self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
                   self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
                   self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        self.physics_engine.update()


def main():
    window = Game()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()