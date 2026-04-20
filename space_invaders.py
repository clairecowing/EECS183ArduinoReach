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
pixelColor[ORANGE] = 0xffa500
pixelColor[YELLOW] = 0xffff00
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

NUM_ENEMIES = 16

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
class Game:
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

        # print(button.value)
        print(button_pressed)
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
        if self.time > self.invader_time + 4:            
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
game = Game()


# ---------------- Arduino-style setup and loop ----------------
def setup() -> None:
    game.setup_game()
    loop()

def loop() -> None:
    while True:
        game.update(pot.value, button.value)
