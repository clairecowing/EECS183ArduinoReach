import random
import time
import board
import displayio
import terminalio
import framebufferio
import rgbmatrix
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn
import adafruit_display_text.label
# import space_invaders
# import flappy

NUM_ENEMIES = 16 
POLE_GAP = 7

displayio.release_displays()

# set up the button input
button = DigitalInOut(board.D7)
button.direction = Direction.INPUT
button.pull = Pull.UP

# set up the potentiometer
pot = AnalogIn(board.A5)

#set up the LED display
panel = rgbmatrix.RGBMatrix(
    width=32, bit_depth=4,
    rgb_pins=[board.D8, board.D9, board.D10, board.D11, board.D12, board.D13],
    addr_pins=[board.D4, board.D5, board.D6],
    clock_pin=board.D1, latch_pin=board.D3, output_enable_pin=board.D2)
display = framebufferio.FramebufferDisplay(panel, auto_refresh=False)
SCALE = 1
matrix = displayio.Bitmap(display.width//SCALE, display.height//SCALE, 10)
pixelColor = displayio.Palette(10)
tg1 = displayio.TileGrid(matrix, pixel_shader=pixelColor)
g1 = displayio.Group(scale=SCALE)
g1.append(tg1)
display.root_group = g1

# pallette color index numbers
BLACK, RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, WHITE, LIME, AQUA = range(10)

# set pallette colors
pixelColor[BLACK] = 0x000000
pixelColor[RED] = 0xff0000
pixelColor[ORANGE] = 0xf34e00
pixelColor[YELLOW] = 0xffe400
pixelColor[GREEN] = 0x008000
pixelColor[BLUE] = 0x0000ff
pixelColor[PURPLE] = 0xa020f0
pixelColor[WHITE] = 0xffffff
pixelColor[LIME] = 0x00ff00
pixelColor[AQUA] = 0x00ffff

# ---------------- Utility display functions ----------------

def print_text(inputText: str, value: str | int | None = None) -> None:
    '''
    # call this function with one or two arguments
    # the first argument will print on the top half of the display
    # the second argument (if provided) will print on the bottom half
    '''
    # first line
    topline = adafruit_display_text.label.Label(
        terminalio.FONT,
        color=0xffffff,
        text=inputText
    )
    topline.x = 0
    topline.y = 4

    textGroup = displayio.Group()
    textGroup.append(topline)

    # optional second line
    if value is not None:
        bottomline = adafruit_display_text.label.Label(
            terminalio.FONT,
            color=0xffffff,
            text=str(value)
        )
        bottomline.x = 0
        bottomline.y = 12
        textGroup.append(bottomline)

    display.root_group = textGroup

    display.refresh()

    display.root_group = g1


def fill_screen(color) -> None:
    # sets each pixel on the display to color
    for i in range(matrix.height * matrix.width):
        matrix[i] = color
    display.refresh()
# ------ SPACE INVADERS ---------------
# ---------------- Invader ----------------
class Invader:
    def __init__(self, x_arg: int = 0, y_arg: int = 0, strength_arg: int = 0) -> None:
        self.x = x_arg
        self.y = y_arg
        self.strength = strength_arg
        self.can_move = False

    def initialize(self, x_arg: int, y_arg: int, strength_arg: int) -> None:
        # initialize instance variables
        self.x = x_arg
        self.y = y_arg
        self.strength = strength_arg

    # getters
    def get_x(self) -> int:
        return self.x

    def get_y(self) -> int:
        return self.y

    def get_strength(self) -> int:
        return self.strength

    # Moves the Invader down the screen by one row
    # Modifies: y
    def move(self) -> None:
        if self.can_move:
            self.y += 1

    def get_body_color(self):
        if self.strength == 1:
            return RED
        elif self.strength == 2:
            return ORANGE
        elif self.strength == 3:
            return YELLOW
        elif self.strength == 4:
            return GREEN
        elif self.strength == 5:
            return BLUE
        elif self.strength == 6:
            return PURPLE
        else:
            return WHITE

    # draws the Invader if its strength is greater than 0
    # use self.draw_with_rgb
    def draw(self) -> None:
        if self.strength > 0:
            body_color = self.get_body_color()
            self.draw_with_rgb(body_color, BLUE)

    # draws black where the Invader used to be
    # use self.draw_with_rgb
    def erase(self) -> None:
        # if self.strength > 0:
            # body_color = self.get_body_color()        maddie: I commented these out because we may need to call erase when strength = 0? not sure
            self.draw_with_rgb(BLACK, BLACK)

    # Invader is hit by a Cannonball.
    # Modifies: strength
    # calls: draw, erase
    def hit(self) -> None:
        self.strength -= 1
        self.erase()
        self.draw()

    # draws the Invader
    def draw_with_rgb(self, body_color: int, eye_color: int) -> None:
        left = self.x
        top = self.y
        matrix[left + 1, top] = body_color
        matrix[left + 2, top] = body_color
        matrix[left, top + 1] = body_color
        matrix[left + 1, top + 1] = eye_color
        matrix[left + 2, top + 1] = eye_color
        matrix[left + 3, top + 1] = body_color
        matrix[left, top + 2] = body_color
        matrix[left + 1, top + 2] = body_color
        matrix[left + 2, top + 2] = body_color
        matrix[left + 3, top + 2] = body_color
        matrix[left, top + 3] = body_color
        matrix[left + 3, top + 3] = body_color

# ---------------- Cannonball ----------------
class Cannonball:
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.fired = False

    # resets private data members to initial values
    def reset(self) -> None:
        self.x = 0
        self.y = 0
        self.fired = False

    # getters
    def get_x(self) -> int:
        return self.x

    def get_y(self) -> int:
        return self.y

    def has_been_fired(self) -> bool:
        return self.fired

    # sets private data members
    def fire(self, x_arg: int, y_arg: int) -> None:
        self.x = x_arg
        self.y = y_arg
        self.fired = True
        self.draw()

    # moves the Cannonball and detects if it goes off the screen
    # Modifies: y, fired
    def move(self) -> None:
        self.erase()
        if self.y >= 2:
            self.y -= 1
            self.draw()
        else:
            self.reset()

    # resets private data members to initial values
    '''why do we have this as a separate function to reset()--------------------------------'''
    def hit(self) -> None:
        self.x = 0
        self.y = 0
        self.fired = False

    # draws the Cannonball, if it is fired
    def draw(self) -> None:
        left = self.x
        top = self.y
        matrix[left, top] = ORANGE
        matrix[left, top + 1] = ORANGE

    # draws black where the Cannonball used to be
    def erase(self) -> None:
        left = self.x
        top = self.y
        matrix[left, top] = BLACK
        matrix[left, top + 1] = BLACK

# ---------------- Player ----------------
class Player:
    def __init__(self) -> None:
        self.x = 0
        self.y = 14
        self.lives = 3

    # getters
    def get_x(self) -> int:
        return self.x

    def get_y(self) -> int:
        return self.y

    def get_lives(self) -> int:
        return self.lives

    # setter
    def set_x(self, x_arg: int) -> None:
        self.x = x_arg

    # Modifies: lives
    def die(self) -> None:
        self.lives -= 1

    # draws the Player
    # use self.draw_with_rgb
    def draw(self) -> None:
        self.draw_with_rgb(AQUA)

    # draws black where the Player used to be
    # use self.draw_with_rgb
    def erase(self) -> None:
        self.draw_with_rgb(BLACK)

    # resets private data members x and y to initial values
    def reset(self, x_arg: int, y_arg: int, lives_arg: int) -> None:
        self.x = x_arg
        self.y = y_arg
        ''' are we resetting the lives? ---------------------------------------- '''
        self.lives = lives_arg

    # draws the player
    def draw_with_rgb(self, color: int) -> None:
        middle = self.x
        top = self.y

        if middle >= 31:
            middle = 31
            matrix[middle - 1, top + 1] = color
            matrix[middle, top] = color
            matrix[middle, top + 1] = color

        elif middle <= 0:
            middle = 0
            matrix[middle, top] = color
            matrix[middle, top + 1] = color
            matrix[middle + 1, top + 1] = color
        
        else:
            matrix[middle - 1, top + 1] = color
            matrix[middle, top] = color
            matrix[middle, top + 1] = color
            matrix[middle + 1, top + 1] = color



# ---------------- Game ----------------
class Space_Game:
    def __init__(self) -> None:
        self.level: int = 1
        self.time: float = time.monotonic()
        # suggested: you will want to add more attributes here
        # suggested - float for time for cannonball and invaders to move
        self.last_move: int = 0
        self.player: Player = Player()
        self.ball: Cannonball = Cannonball()
        self.enemies: list[Invader] = [Invader() for _ in range(NUM_ENEMIES)]
        self.cannonball_time = time.monotonic()
        self.invader_time = time.monotonic()
        self.game_over = False

        '''initialize player and cannonball instances'''
        # self.cannonball = Cannonball
        # self.player = Player          maddie: I commented these out because these have already been initialized as self.player and self.ball (above). feel free to switch tho

    # sets up a new game of Space Invaders
    def setup_game(self) -> None:
        
        fill_screen(BLACK)
        self.player.reset(0, 14, 3)
        # maybe reset other items
        self.level = 1
        self.reset_level()

    # main loop (called repeatedly)
    def update(self, potentiometer_value: int, button_pressed: bool) -> None:
        self.time = time.monotonic()
        display.refresh() 

        # suggested steps (check the Game Dynamics section of the specification for more)
        # 1. get the current time - this is a float in seconds
        # since the unit was powered on

        # 2. check for collision with player
        if self.check_invader_collision():
            self.player.die()
            if self.player.lives <= 0:
                fill_screen(BLACK)
                print_text("Game", "Over")
                self.game_over = True
                time.sleep(2)

                self.setup_game()
            else:
                self.reset_level()

        # 3. update the player if potentiometer moved significantly
        # floor division normalizes

        # alternatively: we could define a player.move function, not sure if thats necessary tho or if this will work - maddie

        if potentiometer_value // 2048 != self.player.get_x():
            self.player.erase()
            self.player.set_x((potentiometer_value // 2048)) #1187 # 2048 (65535/ 32)
            self.player.draw()

        #print(button.value)

        # 4. detect if should fire
        if button_pressed and self.ball.fired == False:
            self.ball.fire(self.player.x, self.player.y - 2)

        # 5. move cannonball if fired
        if self.ball.fired == True:
            if self.time > self.cannonball_time + 0.05:
                self.ball.move()
                for invader in self.enemies:
                    if invader.strength > 0:
                        invader.erase()
                        invader.draw()
                self.cannonball_time = self.time
            self.check_ball_collision()


        if self.check_first_row_cleared():
            for invader in self.enemies[0:8]:
                invader.can_move = True

        # 6. move invaders
        if self.time > self.invader_time + .1:            
            #check to make sure invader is within the screen
            #and that its not touching player.       maddie: we already check for collision with player above.
            if not self.check_floor_collision():
                # erase each invader
                for invader in self.enemies:
                    if invader.strength > 0:
                        invader.erase()
                    # move each invader down by 1
                        invader.move()
                    # draw each invader
                        invader.draw()
            else:
                self.player.die()
                self.reset_level()
                    
            self.invader_time = self.time              # should keep invaders drawn in place - maddie -- claire: wouldn't the else case be game over?

        # 7. check for cleared level
        if self.level_cleared():
            self.level += 1
            # also do level and then the level number
            self.reset_level()
        return

    # this function might be useful in loop: check if Player defeated all Invaders
    def level_cleared(self) -> bool:
        for invader in self.enemies:
            if invader.strength != 0:
                return False
            else:
                continue
        return True

    # set up/reset a level
    def reset_level(self) -> None:
        
        # suggested steps:
        # 1. print level and lives
        # fill_screen(BLACK) should erase whole board. not sure how often it should be called - maddie
        if not self.game_over:
            fill_screen(BLACK)
            print_text("Level", self.level)
            time.sleep(1)
            fill_screen(BLACK)
            print_text("Lives", self.player.get_lives())
            time.sleep(1)
            fill_screen(BLACK)
        
        # not sure if we need to wait a few secs between each. see how it displays? - maddie

        # 2. reset the cannonball
        self.ball.reset() # maddie: changed 'cannonball' to 'ball'
        # 3. check for game over
        if self.player.lives == 0:
            fill_screen(BLACK)
            print_text("Game Over")
            self.game_over = True

    
            # We can choose to either leave this text displayed and end the program, or to restart the game. up to you guys. - maddie

        # 4. initialize invaders based on level
        if self.level == 1:
            for i, invader in enumerate(self.enemies[0:8]):
                invader.can_move = False
                invader.y = 0
                invader.strength = 1
                invader.x = i * 4
                invader.draw()
            for i, invader in enumerate(self.enemies[8:16]):
                invader.can_move = True
                invader.y = 0
                invader.strength = 0
                invader.x = i * 4
                invader.draw()
        elif self.level == 2:
            for i, invader in enumerate(self.enemies[0:8]):
                invader.can_move = False
                invader.y = 0
                if i % 2 == 0:
                    invader.strength = 2
                else:
                    invader.strength = 1
                invader.x = i * 4
                invader.draw()
            for i, invader in enumerate(self.enemies[8:16]):
                invader.can_move = True
                invader.y = 4
                if i % 2 == 0:
                    invader.strength = 1
                else:
                    invader.strength = 2
                invader.x = i * 4
                invader.draw()
        elif self.level == 3:
            # first row of invaders
            for i, invader in enumerate(self.enemies[0:8]):
                invader.can_move = False
                invader.y = 0
                if i % 5 == 0:
                    invader.strength = 1
                elif i % 5 == 1:
                    invader.strength = 2
                elif i % 5 == 2:
                    invader.strength = 3
                elif i % 5 == 3:
                    invader.strength = 4
                else:
                    invader.strength = 5
                invader.x = i * 4
                invader.draw()
            # second row of invaders
            for i, invader in enumerate(self.enemies[8:16]):
                invader.can_move = True
                invader.y = 4
                if i % 5 == 0:
                    invader.strength = 4
                elif i % 5 == 1:
                    invader.strength = 5
                elif i % 5 == 2:
                    invader.strength = 1
                elif i % 5 == 3:
                    invader.strength = 2
                else:
                    invader.strength = 3
                invader.x = i * 4
                invader.draw()

        elif self.level == 4:
            # first row of invaders
            for i, invader in enumerate(self.enemies[0:8]):
                invader.can_move = False
                invader.y = 0
                if i % 2 == 0:
                    invader.strength = 4
                else:
                    invader.strength = 5
                invader.x = i * 4
                invader.draw()
            # second row of invaders
            for i, invader in enumerate(self.enemies[8:16]):
                invader.can_move = True
                invader.y = 4
                if i % 2 == 0:
                    invader.strength = 3
                else:
                    invader.strength = 2
                invader.x = i * 4
                invader.draw()
                ''' level 5 + ------------------------------------------------------------'''
        elif self.level > 4:
            for i, invader in enumerate(self.enemies[0:8]):
                invader.can_move = False
                invader.y = 0
                invader.x = i * 4
                invader.strength = int(random.random() * 8) + 1 # idk why this has red underline. also not sure casting to int is required but better safe than sorry
                invader.draw()
            for i, invader in enumerate(self.enemies[8:16]):
                invader.can_move = True
                invader.y = 4
                invader.x = i * 4
                invader.strength = int(random.random() * 8) + 1 # idk why this has red underline - maddie
                invader.draw()

        # 5. draw enemies (should be done above - maddie)

        # 6. draw player
        self.player.draw()
        
        # 7. reset time so invaders do not move immediately
        self.time = time.monotonic()
        return

    # check if cannonball hits an invader
    def check_ball_collision(self) -> None:
        ctop = self.ball.y
        cleft = self.ball.x
        for invader in self.enemies:
            if invader.strength > 0:
                invader_hit = [
                    (invader.x, invader.y + 3),
                    (invader.x + 1, invader.y + 2),
                    (invader.x + 2, invader.y + 2),
                    (invader.x + 3, invader.y + 3)
                ]
                if (cleft, ctop) in invader_hit:
                    self.ball.fired = False
                    self.ball.erase()
                    invader.hit()
        return

    # check if invaders hit the player or bottom
    def check_invader_collision(self) -> bool:
        ptop = self.player.y
        pleft = self.player.x
        
        for invader in self.enemies:
            if invader.strength > 0:
                invader_hit = [
                    (invader.x, invader.y + 3),
                    (invader.x + 1, invader.y + 2),
                    (invader.x + 2, invader.y + 2),
                    (invader.x + 3, invader.y + 3)
                ]
                positions_to_check = ((pleft - 1, ptop + 1), (pleft, ptop), (pleft + 1, ptop + 1))

                if any(pos in invader_hit for pos in positions_to_check):
                    return True
            # if invader.y + 3 == 15: maddie: i made this into its own function below, as colliding w player and w floor have different consequences
                # return True
        return False

    def check_floor_collision(self) -> bool:
        for invader in self.enemies:
            if invader.y + 3 == 15:
                return True
        return False

    def check_first_row_cleared(self) -> bool:
        for invader in self.enemies[8:16]:
            if invader.strength > 0:
                return False
        return True

# ---------------- Global game instance ----------------
space_game = Space_Game()


# ---------------- Arduino-style setup and loop ----------------
def space_setup() -> None:
    space_game.game_over = False
    space_game.setup_game()
    space_loop()
    print("back to menu")
    setup()

def space_loop() -> None:
    while True:
        space_game.update(pot.value, button.value)
        if space_game.game_over:
            print("game is over")
            break 


# ---------- FLAPPY BIRD -------------------------

# -------------------------------------------------- #

class Bird:
    def __init__(self):
        self.x = 8 # middle & bottom pixel of the bird
        self.y = 8

    def fly_up(self):
        if self.y > 2:
            self.y -= 2
        else:
            self.y = 2

    def draw_bird_rgb(self, color):
        matrix[self.x, self.y] = color
        matrix[self.x - 1, self.y] = color
        matrix[self.x, self.y - 1] = color

    def draw(self):
        self.draw_bird_rgb(YELLOW)
        matrix[self.x + 1, self.y - 1] = ORANGE

    def gravity(self):
        self.y += 1
        
    def reset(self):
        self.x = 8
        self.y = 8
    
    def erase(self):
        self.draw_bird_rgb(BLACK)
        matrix[self.x + 1, self.y - 1] = BLACK


class Pole:
    def __init__(self):
        self.pole_height = random.randrange(POLE_GAP, 15)     
        self.x = 32
        self.y = self.pole_height
        self.has_passed = False
   
    def move(self):
        self.x -= 1

    def draw(self):
        self.draw_with_rgb(LIME)

    def erase(self):
        self.draw_with_rgb(BLACK)

    def draw_with_rgb(self, color: int):
        left = self.x

        if left >= 31:
            for i in range(0, self.pole_height - POLE_GAP):
                matrix[31, i] = color
            for i in range(self.pole_height, 16):
                matrix[31, i] = color

        elif left < 0:
            for i in range(0, self.pole_height - POLE_GAP):
                matrix[0, i] = color
            for i in range(self.pole_height, 16):
                matrix[0, i] = color
        else:
            for i in range(0, self.pole_height - POLE_GAP):
                matrix[left, i] = color
                matrix[left + 1, i] = color

            for i in range(self.pole_height, 16):
                matrix[left, i] = color
                matrix[left + 1, i] = color
     

# ---------------- Game ----------------
class Flappy_Game:
    def __init__(self) -> None:
        self.speed = 1  # increases after x amount of time playing the game?
        self.active_poles = [Pole()]  # usually 5 or 6 on a screen at a time
        self.bird = Bird()
        self.score: int = 0  # when each pole goes past the x axis of the bird, score increases
        self.time: float = time.monotonic()
        self.bird_time = time.monotonic()
        self.pole_time = time.monotonic()
        self.gravity_time = time.monotonic()
        self.game_speed = 1  # how fast the poles are being generated
        self.button_press = False
        self.game_over = False

    def setup_game(self):
        # reset bird location
        self.bird.reset()
        # reset active poles list
        self.active_poles = [Pole()]
        self.score = 0
        # is there anything else to be reset?
        self.game_speed = 1
        self.bird.draw()
        self.button_press = False
        self.last_button = False

    def update(self, potentiometer_value: int, button_pressed: bool) -> None:
        # print(1/(potentiometer_value//2048 + 1)) # speed of the game
        self.time = time.monotonic()    
        display.refresh()
        curr_pole: Pole = self.active_poles[0]

        if self.check_offscreen():
            self.lose()
            self.bird.reset()
            self.reset_level()

        # Check if bird collided with pole. If yes, lose game
        if self.check_pole_collision(curr_pole):
            self.lose()
            self.reset_level()

        # gravity

        if self.time > self.gravity_time + 0.4:
            if self.bird.y <= 15:
                self.bird.erase()
                self.bird.gravity()
                self.bird.draw()
                self.gravity_time = self.time

        # Check if button pressed - if true, fly up, else, gravity
        if self.check_button_clicked(button_pressed): 
            # print(self.check_button_clicked(button_pressed))
            if self.time > self.bird_time + 0.1:
                self.bird.erase()
                self.bird.fly_up()
                self.bird.draw()
                self.bird_time = self.time
        
        
        if self.time > self.bird_time + 0.05:
            self.button_press = False


        # Check if pole has passed bird. If yes, increment score
        for curr_pole in self.active_poles:
            if self.check_pole_score(curr_pole):
                if not curr_pole.has_passed:
                    self.score += 1
                    curr_pole.has_passed = True
       
        # if enough time has passed, move pole to left (erase, move, draw)
        # and append new pole to active list
        if self.time > self.pole_time + 1/(potentiometer_value//2048 + 1):
            for curr_pole in self.active_poles:
                curr_pole.erase()
                curr_pole.move()

                # check if movement will make it go out of bounds
                # if yes, remove it from list
                if curr_pole.x < -1:
                    self.active_poles.remove(curr_pole)
                else:
                    curr_pole.draw()
                # else, move it
            # reset self.pole_time
            self.pole_time = time.monotonic()

        # drawing poles? 
        last_pole = self.active_poles[-1]
        if last_pole.x == 23:
            # if enough time has passed, generate a new pole & add to list
            self.active_poles.append(Pole())

        display.refresh()

    def check_offscreen(self):
        if self.bird.y >= 15:
            return True

    def lose(self):
        print_text("You", "lose")
        time.sleep(1)
        print_text("Score:", self.score)
        time.sleep(1)
        self.game_over = True

    def reset_level(self) -> None:
        # fill screen 
        fill_screen(BLACK)
        print_text("Score", self.score)
        time.sleep(1)
        self.setup_game()
        self.time = time.monotonic()

    # checks if the bird collides with a pole
    def check_pole_collision(self, curr_pole: Pole) -> bool:
        if (self.bird.x == curr_pole.x) or (self.bird.x == curr_pole.x + 1):
            if (self.bird.y - 1) <= (curr_pole.pole_height - POLE_GAP):  # top part
                return True
            elif (self.bird.y) >= (curr_pole.pole_height):
                return True
        # checks for beak collision
        elif (self.bird.x + 1 == curr_pole.x) or (self.bird.x + 1 == curr_pole.x + 1):
            if (self.bird.y - 1) <= (curr_pole.pole_height - POLE_GAP):  # top part
                return True
            elif (self.bird.y - 1) >= (curr_pole.pole_height):
                return True
        # checks for tail collision
        elif (self.bird.x - 1 == curr_pole.x) or (self.bird.x - 1 == curr_pole.x + 1):
            if (self.bird.y) <= (curr_pole.pole_height - POLE_GAP):  # top part
                return True
            elif (self.bird.y) >= (curr_pole.pole_height):
                return True
        else:
            return False

    def check_pole_score(self, current_pole) -> bool:
        if current_pole.x + 1 < self.bird.x:
            return True
        else:
            return False
    
    # checks if the bird collides with the ground.
    def check_ground_collision(self) -> None:
        if self.bird.x >= 14:
            self.reset_level()

    # returns true ON BUTTON CLICKED (after it has been released)
    def check_button_clicked(self, button_pressed):
        
        if button_pressed is True and self.last_button is False:
            print("button clicked")
            self.last_button = button_pressed
            return True
        else:
            self.last_button = button_pressed
            return False

# ---------------- Global game instance ----------------
flappy_game = Flappy_Game()

# ---------------- Arduino-style setup and loop ----------------
def flappy_setup() -> None:
    fill_screen(BLACK)
    flappy_game.game_over = False
    flappy_game.setup_game()
    flappy_loop()
    setup()
    
def flappy_loop() -> None:
    while True:
        flappy_game.update(pot.value, button.value)
        if flappy_game.game_over:
            print("game is over")
            fill_screen(BLACK)
            break 


# ---------------- MENU ----------------

class Menu:
    def __init__(self):
        self.selected_game = 0
        self.last_selected = -1
    

    def setup_menu(self):
        fill_screen(BLACK)
        print_text("Micro", "Games") # maybe do a cute name like micro arcade or smth or say welcome idk
        time.sleep(1)
        print("setting up")
        fill_screen(BLACK)
        # display.refresh()
        self.draw_menu_ui()


    def run_menu(self, pot_value, button_value) -> int:
        # for this it makes it so if it's over the halfway point then it's flappy bird else it's space invaders, but it might be better to have it change when you turn left vs. right instead of actual potentiometer value but idk how to do that rn
        
        if pot_value > 31744:
            self.selected_game = 1
        else:
            self.selected_game = 0
            
        if self.selected_game != self.last_selected:
            self.draw_menu_ui()
            self.last_selected = self.selected_game

        
        if button_value:
            return self.selection()
    
            # time.sleep(2)
        
        # g1.remove(menu_label)
        display.refresh()
        
    
    def draw_menu_ui(self) -> None:
        # fill_screen(BLACK)
        print("drawing menu ui")
    #  i just used the functions from each of the games but might need to hardcode it/adjust location but i can't see the board
        # invader_pixels = draw_with_rgb
        self.draw_invader(6, 6)
        # for px, py in invader_pixels:
            # matrix[px + 4, py + 7] = # color

        self.draw_bird(21, 6)
        display.refresh()
        # bird_pixels = draw_bird
        # for px, py, color in bird_pixels:
            # matrix[px + 21, py + 7] = # color
            
        arrow_x = 7 #?
        print(f"selected game: {self.selected_game}")
        if self.selected_game == 0:
            arrow_x = 7
            other_x = 23
        else: 
            arrow_x = 23
            other_x = 7
        # ARROW
        self.draw_arrow(other_x, BLACK)
        self.draw_arrow(arrow_x, WHITE)
     
    def draw_arrow(self, arrow_x, color):
        matrix[arrow_x, 11] = color
        matrix[arrow_x - 1, 12] = color
        matrix[arrow_x, 12] = color
        matrix[arrow_x + 1, 12] = color
        matrix[arrow_x, 13] = color
        matrix[arrow_x, 14] = color


    def selection(self) -> None:
        if self.selected_game == 0:
            
            # space_invaders.setup()
            print_text("Space", "Invaders")
            time.sleep(2)
            space_setup()
            # just call space invaders
        else: 
            game = "flappy"
            # flappy.setup()
            print_text("Flappy", "Bird")
            time.sleep(2)
            # just call flappy set up
            flappy_setup()

        # game.setup()
    
    def draw_bird(self, x_arg, y_arg):
        top = y_arg
        left = x_arg
        matrix[left + 2, top] = YELLOW
        matrix[left + 3, top] = YELLOW
        matrix[left + 1, top + 1] = YELLOW
        matrix[left + 2, top + 1] = YELLOW
        matrix[left + 3, top + 1] = BLUE
        matrix[left + 4, top + 1] = YELLOW
        matrix[left, top + 2] = WHITE
        matrix[left + 1, top + 2] = WHITE
        matrix[left + 2, top + 2] = YELLOW
        matrix[left + 3, top + 2] = YELLOW
        matrix[left + 4, top + 2] = ORANGE
        matrix[left + 5, top + 2] = ORANGE
  
        matrix[left + 1, top + 3] = YELLOW
        matrix[left + 2, top + 3] = YELLOW
        matrix[left + 3, top + 3] = YELLOW
        matrix[left + 4, top + 3] = YELLOW
        print("drawing bird")

    def draw_invader(self, x_arg, y_arg):
        print("drawing_invader")
        left = x_arg
        top = y_arg
        body_color = RED
        eye_color = BLUE
        matrix[left + 1, top] = body_color
        matrix[left + 2, top] = body_color
        matrix[left, top + 1] = body_color
        matrix[left + 1, top + 1] = eye_color
        matrix[left + 2, top + 1] = eye_color
        matrix[left + 3, top + 1] = body_color
        matrix[left, top + 2] = body_color
        matrix[left + 1, top + 2] = body_color
        matrix[left + 2, top + 2] = body_color
        matrix[left + 3, top + 2] = body_color
        matrix[left, top + 3] = body_color
        matrix[left + 3, top + 3] = body_color



# ---------------- Global game instance ----------------
menu = Menu()


# ---------------- Arduino-style setup and loop ----------------
def setup() -> None:
    menu.setup_menu()
    loop()

def loop() -> None:
    while True:
        menu.run_menu(pot.value, button.value)
    