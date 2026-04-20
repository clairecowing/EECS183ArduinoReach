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
            self.selection()
    
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
            game = "space_invaders"
            # space_invaders.setup()
            print_text("Space", "Invaders")
            time.sleep(2)
            # just call space invaders
        else: 
            game = "flappy"
            # flappy.setup()
            print_text("Flappy", "Bird")
            time.sleep(2)
            # just call flappy set up

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
