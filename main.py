from game import Catapult_4
from window_sizer import StartWindow

start_window = StartWindow()
start_window.run()

# Ensures you pressed play on the first window instead of just closing it
if start_window.launched_game:

    game = Catapult_4(start_window.game_width, start_window.game_height)

    while game.running:
        game.current_menu.draw_menu()
        game.game_loop()

