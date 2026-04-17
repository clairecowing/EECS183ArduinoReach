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

NUM_POSSIBLE_POLES = 5 #! -- change this later

# -------------------------------------------------- #

class Bird:
    def __init__(self):
        self.x = 8 # middle & bottom pixel of the bird
        self.y = 8

    def fly_up(self):
        self.y += 2

    def draw_bird(self):
        matrix[self.x, self.y] = YELLOW
        matrix[self.x - 1, self.y] = YELLOW
        matrix[self.x, self.y - 1] = YELLOW
        matrix[self.x + 1, self.y - 1] = ORANGE
    
    def gravity(self):
        self.y -= 1
    
    def reset(self):
        self.x = 8
        self.y = 8


class Pole:
    def __init__(self,):
        self.pole_height = random.randrange(4, 11)       
        self.x = arg_x #! idk what to do for x, should it be offscreen?
        self.y = self.pole_height

        # TODO idk what should be here
        pass
    
    def move(self):
        pass

    def draw(self, pole_height):
        # may also need to take in some argument indicating the level of the pole
        pass

# ---------------- Game ----------------
class Game:
    def __init__(self) -> None:
        self.speed = 1  # increases after x amount of time playing the game?
        self.possible_poles: list[Pole] = [Pole() for _ in range(NUM_POSSIBLE_POLES)]
        self.active_poles = list()  # usually 5 or 6 on a screen at a time
        self.bird = Bird()
        self.score: int = 0  # when each pole goes past the x axis of the bird, score increases
        self.time: float = time.monotonic()
        self.bird_time = time.monotonic()
        self.pole_time = time.monotonic()
        self.game_speed = 1  # how fast the poles are being generated

    def setup_game(self):
        # TODO
        # reset bird location
        self.bird.reset()
        # reset active poles list
        self.active_poles = []
        self.score = 0
        # is there anything else to be reset?
        self.game_speed = 1


    def update(self, potentiometer_value: int, button_pressed: bool) -> None:
        self.time = time.monotonic()    
        display.refresh()

        curr_pole: Pole = self.active_poles[0]

        # Check if bird collided with pole. If yes, lose game
        if self.check_pole_collision(curr_pole):
            self.lose()
            self.reset_level()

        # Check if button pressed - if true, fly up, else, gravity
        if button_pressed:
            if self.time > self.bird_time + 0.05:
                self.bird.fly_up()
                self.bird_time = self.time

        # Check if pole has passed bird. If yes, increment score
        if curr_pole.x <= self.bird.x:
            self.score += 1
        # if enough time has passed, move pole to left (erase, move, draw)
        # and append new pole to active list
        if self.time > self.pole_time + 3:
            for curr_pole in self.active_poles:
                pass
                # check if movement will make it go out of bounds
                # if yes, remove it from list / draw it only partially
                # else, move it & reset self.pole_time
        if self.time > self.pole_generated_time + self.game_speed:
            next_pole_index = int(random.random() * NUM_POSSIBLE_POLES) + 1
            # if enough time has passed, generate a new pole & add to list
            self.active_poles.append(self.possible_poles[next_pole_index])

        display.refresh() 

    def lose(self):
        print_text("You lose")
        time.sleep(1)
        print_text("Score:", self.score)
        time.sleep(1)

    def reset_level(self) -> None:
        # fill screen 
        fill_screen(BLACK)
        print_text("Score", self.score)
        time.sleep(1)
        self.setup_game()
        # reset bird location
        self.bird.reset()
        # reset active poles list
        self.active_poles = []
        self.score = 0
        # is there anything else to be reset?
        self.game_speed = 1
        self.bird.draw_bird()
        self.time = time.monotonic()

    # checks if the bird collides with a pole
    def check_pole_collision(self, curr_pole: Pole) -> bool:
        # TODO if it does, 
        if (self.bird.x == curr_pole.x) or (self.bird.x == curr_pole.x + 1): #! double check this works after draw pole is implemented
            if self.bird.y <= curr_pole.y:
                return True
        else:
            return False


    def check_pole_score(self, current_pole) -> bool:
        if current_pole.x < self.bird.x:
            return True
        else:
            return False
    
    # checks if the bird collides with the ground.
    def check_ground_collision(self) -> None:
        if self.bird.x >= 14:
            self.reset_level()


# ---------------- Global game instance ----------------
game = Game()

# ---------------- Arduino-style setup and loop ----------------
def setup() -> None:
    game.setup_game()
    loop()

def loop() -> None:
    while True:
        game.update(pot.value, button.value)