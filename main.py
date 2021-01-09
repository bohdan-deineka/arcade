__author__ = "Bohdan Deineka, Bartlomiej Matuszewski, Bartlomiej Kuzba"
__copyright__ = "Copyright 2020, The Arcade Project"
__credits__ = ["Bohdan Deineka", "Bartlomiej Matuszewski", "Bartlomiej Kuzba"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Bohdan Deineka"
__email__ = "bohdan.deineka@edu.uni.lodz.pl"
__status__ = "Production"

import arcade
import constants
import os

def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class PlayerCharacter(arcade.Sprite):
    """ Player Sprite"""
    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = constants.RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = constants.CHARACTER_SCALING

        # Track our state
        self.jumping = False

        # --- Load Textures ---
        main_path = "images/character"

        # Load textures for idle standing
        self.idle_textures = []
        for i in range(1, 5):
            texture = load_texture_pair(f"{main_path}/grave_robber_idle ({i}).png")
            self.idle_textures.append(texture)

        # Load textures for walking
        self.walk_textures = []
        for i in range(1, 7):
            texture = load_texture_pair(f"{main_path}/grave_robber_walk ({i}).png")
            self.walk_textures.append(texture)

        # Load textures for jumping
        self.jump_textures = []
        for i in range(1, 7):
            texture = load_texture_pair(f"{main_path}/grave_robber_jump ({i}).png")
            self.jump_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_textures[0][0]

        # Hit box will be set based on the first image used.
        self.set_hit_box(self.texture.hit_box_points)

    def update_animation(self, delta_time: float = 1/60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == constants.RIGHT_FACING:
            self.character_face_direction = constants.LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == constants.LEFT_FACING:
            self.character_face_direction = constants.RIGHT_FACING

        # Jumping animation
        if self.change_y > 0:
            self.cur_texture += 1
            if self.cur_texture > 5:
                self.cur_texture = 0
            self.texture = self.jump_textures[self.cur_texture][self.character_face_direction]
            return

        # Idle animation
        if self.change_x == 0:
            self.cur_texture += 1
            if self.cur_texture > 3:
                self.cur_texture = 0
            self.texture = self.idle_textures[self.cur_texture][self.character_face_direction]
            return

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 5:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]


class Game(arcade.Window):

    def __init__(self):
        super().__init__(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, constants.SCREEN_TITLE, fullscreen=True)

        # Set the path to start with this program
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        self.coin_list = None
        self.wall_list = None
        self.player_list = None
        self.background_list = None

        self.player_sprite = None

        self.physics_engine = None

        self.view_bottom = 0
        self.view_left = 0

        # Keep track of the score
        self.score = 0

        # Where is the right edge of the map?
        self.end_of_map = 0

        # Level
        self.level = 1

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")

        self.music_list = []
        self.current_song_index = 0
        self.current_player = None
        self.music = None

        arcade.set_background_color(arcade.csscolor.BLACK)

    def play_song(self):
        if self.music:
            self.music.stop()

        self.music = arcade.Sound(self.music_list[self.current_song_index], streaming = True)
        self.current_player = self.music.play(constants.MUSIC_VOLUME)

    def setup(self, level):

        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.coin_list = arcade.SpriteList(use_spatial_hash=True)
        self.background_list = arcade.SpriteList(use_spatial_hash=True)

        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = constants.PLAYER_START_X
        self.player_sprite.center_y = constants.PLAYER_START_Y
        self.player_list.append(self.player_sprite)

        # --- Load in a map from the tiled editor ---

        # Name of map file to load
        map_name = "maps/map_castle.tmx"
        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Platforms'
        moving_platforms_layer_name = 'Moving Platforms'
        # Name of the layer that has items for pick-up
        coins_layer_name = 'Coins'
        # Name of the layer that has items for background
        background_layer_name = 'Background'

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = my_map.map_size.width * constants.GRID_PIXEL_SIZE

        # -- Background
        self.background_list = arcade.tilemap.process_layer(my_map,
                                                            background_layer_name,
                                                            constants.TILE_SCALING)

        # -- Platforms
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platforms_layer_name,
                                                      scaling=constants.TILE_SCALING,
                                                      use_spatial_hash=True)

        # -- Moving Platforms
        moving_platforms_list = arcade.tilemap.process_layer(my_map, moving_platforms_layer_name, constants.TILE_SCALING)
        for sprite in moving_platforms_list:
            self.wall_list.append(sprite)

        # -- Coins
        self.coin_list = arcade.tilemap.process_layer(my_map, coins_layer_name, constants.TILE_SCALING)

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             constants.GRAVITY)

        self.music_list = ["music/guitar_music.wav"]
        self.current_song_index = 0
        self.play_song()

    def on_draw(self):
        arcade.start_render()

        self.background_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()
        self.player_list.draw()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)

    def process_keychange(self):
        """
        Called when we change a key up/down or we move on/off a ladder.
        """
        # Process up/down
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = constants.PLAYER_MOVEMENT_SPEED
            elif self.physics_engine.can_jump(y_distance=10) and not self.jump_needs_reset:
                self.player_sprite.change_y = constants.PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -constants.PLAYER_MOVEMENT_SPEED

        # Process left/right
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = constants.PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -constants.PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0
 
    def on_key_press(self, key, modifiers):
        if key == arcade.key.F:
            # User hits f. Flip between full and not full screen.
            self.set_fullscreen(not self.fullscreen)

            # Get the window coordinates. Match viewport to window coordinates
            # so there is a one-to-one mapping.
            width, height = self.get_size()
            self.set_viewport(0, width, 0, height)

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False        
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()    

    def on_update(self, delta_time):
        self.physics_engine.update()

        # Update animations
        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False
        else:
            self.player_sprite.can_jump = True

        # Update animations
        self.coin_list.update_animation(delta_time)
        self.background_list.update_animation(delta_time)
        self.player_list.update_animation(delta_time)

        # Update walls, used with moving platforms
        self.wall_list.update()

        # See if the wall hit a boundary and needs to reverse direction.
        for wall in self.wall_list:

            if wall.boundary_right and wall.right > wall.boundary_right and wall.change_x > 0:
                wall.change_x *= -1
            if wall.boundary_left and wall.left < wall.boundary_left and wall.change_x < 0:
                wall.change_x *= -1
            if wall.boundary_top and wall.top > wall.boundary_top and wall.change_y > 0:
                wall.change_y *= -1
            if wall.boundary_bottom and wall.bottom < wall.boundary_bottom and wall.change_y < 0:
                wall.change_y *= -1

        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list)

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Add one to the score
            self.score += 1

        # Track if we need to change the viewport
        changed_viewport = False

        # Did the player fall off the map?
        if self.player_sprite.center_y < -100:
            self.player_sprite.center_x = constants.PLAYER_START_X
            self.player_sprite.center_y = constants.PLAYER_START_Y
            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True
            arcade.play_sound(self.game_over)

        # See if the user got to the end of the level
        if self.player_sprite.center_x >= self.end_of_map:
            # Advance to the next level
            self.level += 1
            # Load the next level
            self.setup(self.level)
            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True

        # --- Manage Scrolling ---

        # Track if we need to change the viewport

        changed = False

        # Scroll left
        left_boundary = self.view_left + constants.LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True

        # Scroll right
        right_boundary = self.view_left + constants.SCREEN_WIDTH - constants.RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.view_bottom + constants.SCREEN_HEIGHT - constants.TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.view_bottom + constants.BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True

        if changed:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                constants.SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                constants.SCREEN_HEIGHT + self.view_bottom)

        position = self.music.get_stream_position()
        if position == 0.0:
            self.play_song()


def main():
    window = Game()
    window.setup(window.level)
    arcade.run()


if __name__ == "__main__":
    main()
