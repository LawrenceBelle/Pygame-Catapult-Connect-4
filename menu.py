import pygame
import os

# Parent class for all menus
class Menu:
    def __init__(self, game):
        self.game = game
        self.run_display = False
        self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT = self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT
        self.mid_w, self.mid_h = self.DISPLAY_WIDTH//2, self.DISPLAY_HEIGHT//2
        self.DISPLAY = pygame.Surface((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
        self.bg = self.game.BLUE

        # Dimensions for a typical button
        self.button_height = self.DISPLAY_HEIGHT//6
        self.button_width = self.DISPLAY_WIDTH//3
        self.button_buffer = self.button_height + self.DISPLAY_HEIGHT//40
        self.button_group = pygame.sprite.Group()
        self.buttons = []

        self.font_name = 'hpsimplified'
        self.text_colour = self.game.DARK_GREY
        self.hover_text_colour = None
        self.text_size = self.button_height//2
        self.desc_text_size = self.text_size//2


    def add_button(self, pos, image, hover_image, width, height, function):
        button = self.game.Button(pos, image, hover_image, width, height, function)
        self.button_group.add(button)
        self.buttons.append(button)

    # This stops buttons immediately being pressed when navigating menus
    def clog_buttons(self):
        for button in self.buttons:
            button.clicked = True

    def draw_text(self, pos, size, text):
        font = pygame.font.SysFont(self.font_name, size)
        text_surface = font.render(text, True, self.text_colour)
        text_rect = text_surface.get_rect()
        text_rect.center = pos
        self.DISPLAY.blit(text_surface, text_rect)

    # Checks if the window has been closed
    def check_closed(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running, self.game.playing = False, False
                self.run_display = False                

    # Puts the display onto the game window
    def blit_menu(self):
        self.game.WINDOW.blit(self.DISPLAY, (0, 0))
        pygame.display.update()


# Initial Menu
class MainMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        # Positions the title card
        self.title_card = pygame.transform.scale(pygame.image.load(os.path.join('resources', "Title_Card.png")), (self.DISPLAY_WIDTH//2, self.DISPLAY_HEIGHT//4))
        self.title_card_rect = self.title_card.get_rect()
        self.title_card_rect.center = (self.mid_w, self.DISPLAY_HEIGHT//4)

        # positions for each button
        self.start_pos = (self.mid_w, self.mid_h)
        self.gamemode_pos = (self.mid_w, self.mid_h + self.button_buffer)
        self.quit_pos = (self.mid_w, self.mid_h + 2*self.button_buffer)
        self.add_button(self.start_pos, "Plate_Wide.png", "Hover_Plate_Wide.png", self.DISPLAY_WIDTH//2, self.button_height, 'start')
        self.add_button(self.gamemode_pos, "Plate_Wide.png", "Hover_Plate_Wide.png", self.button_width, self.button_height, 'settings')
        self.add_button(self.quit_pos, "Plate_Wide.png", "Hover_Plate_Wide.png", self.button_width, self.button_height, 'quit')

    def draw_menu(self):
        self.run_display = True
        self.clog_buttons()
        while self.run_display:
            # Handles button functionality and sees if the window is closed
            self.check_closed()
            self.check_buttons()
            # Draws the display
            self.DISPLAY.fill(self.bg)
            self.button_group.update()
            self.button_group.draw(self.DISPLAY)
            self.DISPLAY.blit(self.title_card, self.title_card_rect)
            self.draw_text(self.start_pos, int(self.text_size * 1.5), "Start Game")
            self.draw_text(self.gamemode_pos, self.text_size, "Settings")
            self.draw_text(self.quit_pos, self.text_size, "Quit")
            self.blit_menu()

    # Handles what each button does
    def check_buttons(self):
        for button in self.buttons:
            if button.check_clicked():
                if button.function == 'start':
                    self.game.reset()
                    self.game.playing = True
                elif button.function == 'settings':
                    self.game.current_menu = self.game.settings_menu
                elif button.function == 'quit':
                    self.game.running = False
                self.run_display = False


# Menu to navigate to either the game mode menu or the CPU menu
class SettingsMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        # positions for each button
        self.back_pos = (self.mid_w, self.mid_h - self.button_buffer)
        self.vs_pos = (self.mid_w, self.mid_h)
        self.gamemode_pos = (self.mid_w, self.mid_h + self.button_buffer)
        self.add_button(self.back_pos, "Back_Button.png", "Hover_Back_Button.png", self.button_height, self.button_height, 'back')
        self.add_button(self.vs_pos, "Plate_Wide.png", "Hover_Plate_Wide.png", self.button_width, self.button_height, 'versus')
        self.add_button(self.gamemode_pos, "Plate_Wide.png", "Hover_Plate_Wide.png", self.button_width, self.button_height, 'gamemode')

    def draw_menu(self):
        self.run_display = True
        self.clog_buttons()
        while self.run_display:
            self.check_closed()
            self.DISPLAY.fill(self.bg)
            self.check_buttons()
            self.button_group.update()
            self.button_group.draw(self.DISPLAY)
            self.draw_text(self.vs_pos, self.text_size, "Versus")
            self.draw_text(self.gamemode_pos, self.text_size, "Gamemode")
            self.blit_menu()

    def check_buttons(self):
        for button in self.buttons:
            if button.check_clicked():
                if button.function == 'back':
                    self.game.current_menu = self.game.main_menu
                elif button.function == 'versus':
                    self.game.current_menu = self.game.vs_menu
                elif button.function == 'gamemode':
                    self.game.current_menu = self.game.game_mode_menu
                self.run_display = False


# Menu for whether or not you want to face the computer and the difficulty of it
class VersusMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.show_difficulty = False

        self.difficulties = {
            0 : 'Easy',
            1 : 'Medium',
            2 : 'Extreme',
        }
        self.difficulty_index = 1
        self.difficulty = self.difficulties[self.difficulty_index]

        self.min_difficulty = 0
        self.max_difficulty = 2

        # positions for each button
        self.back_pos = (self.mid_w, self.mid_h - self.button_buffer)
        self.multiplayer_pos = (self.mid_w, self.mid_h)
        self.vs_cpu_pos = (self.mid_w, self.mid_h + self.button_buffer)
        self.difficulty_pos = (self.mid_w, self.mid_h + 2*self.button_buffer)
        # Covers the difficulty of the cpu when playing multiplayer
        self.cover_rect = pygame.Rect(0, self.difficulty_pos[1] - self.button_height//2, self.DISPLAY_WIDTH, self.button_height)
        self.plate = pygame.transform.scale(pygame.image.load(os.path.join('resources', "Plate_Wide.png")), (self.button_width, self.button_height))

        self.add_button(self.back_pos, "Back_Button.png", "Hover_Back_Button.png", self.button_height, self.button_height, 'back')
        self.add_button(self.multiplayer_pos, "Plate_Wide.png", "Hover_Plate_Wide.png", self.button_width, self.button_height, 'multiplayer')
        self.add_button(self.vs_cpu_pos, "Plate_Wide.png", "Hover_Plate_Wide.png", self.button_width, self.button_height, 'vs cpu')

        self.side_button_buffer = self.button_buffer + self.button_width//2

        self.add_button((self.difficulty_pos[0] - self.side_button_buffer, self.difficulty_pos[1]), "Left_Button.png", "Hover_Left_Button.png", self.button_height, self.button_height, 'lower_difficulty')
        self.add_button((self.difficulty_pos[0] + self.side_button_buffer, self.difficulty_pos[1]), "Right_Button.png", "Hover_Right_Button.png", self.button_height, self.button_height, 'raise_difficulty')

        self.highlight = pygame.transform.scale(pygame.image.load(os.path.join('resources', "Confirm_Button.png")), (self.button_height, self.button_height))
        # hl_pos = highlight positions
        self.mode_hl_pos = {
            'multiplayer' : (self.multiplayer_pos[0] + self.button_width//2 + self.DISPLAY_HEIGHT//40, self.multiplayer_pos[1] - self.button_height//2),
            'vs cpu' : (self.vs_cpu_pos[0] + self.button_width//2 + self.DISPLAY_HEIGHT//40, self.vs_cpu_pos[1] - self.button_height//2),
        }
        self.current_hl_pos = self.mode_hl_pos['multiplayer']

    def draw_menu(self):
        self.run_display = True
        self.clog_buttons()
        while self.run_display:
            self.check_closed()
            self.DISPLAY.fill(self.bg)
            self.check_buttons()
            self.button_group.update()
            self.button_group.draw(self.DISPLAY)
            self.draw_text(self.multiplayer_pos, self.text_size, "Multiplayer")
            self.draw_text(self.vs_cpu_pos, self.text_size, "Vs CPU")
            self.DISPLAY.blit(self.highlight, self.current_hl_pos)
            self.DISPLAY.blit(self.plate, (self.difficulty_pos[0] - self.button_width//2, self.difficulty_pos[1] - self.button_height//2))            
            self.draw_text(self.difficulty_pos, self.text_size, self.difficulty)
            if not self.show_difficulty:
                pygame.draw.rect(self.DISPLAY, self.bg, self.cover_rect)
            self.blit_menu()

    def check_buttons(self):
        for button in self.buttons:
            if button.check_clicked():
                if button.function == 'back':
                    self.game.current_menu = self.game.settings_menu
                    self.game.cpu_difficulty = self.difficulty.lower()
                    self.run_display = False
                elif button.function == 'multiplayer':
                    self.current_hl_pos = self.mode_hl_pos[button.function]
                    self.game.vs_cpu = False
                    self.show_difficulty = False
                elif button.function == 'vs cpu':
                    self.current_hl_pos = self.mode_hl_pos[button.function]
                    self.game.vs_cpu = True
                    self.show_difficulty = True

                if self.show_difficulty:
                    if button.function == 'lower_difficulty' and self.difficulty_index > self.min_difficulty:
                        self.difficulty_index -= 1
                        self.difficulty = self.difficulties[self.difficulty_index]
                    if button.function == 'raise_difficulty' and self.difficulty_index < self.max_difficulty:
                        self.difficulty_index += 1
                        self.difficulty = self.difficulties[self.difficulty_index]


# Menu to pick which game mode to play
class GameModeMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        # positions for each button
        self.back_pos = (self.mid_w, self.mid_h - self.button_buffer)
        self.standard_pos = (self.mid_w, self.mid_h)
        self.precision_pos = (self.mid_w, self.mid_h + self.button_buffer)
        self.custom_pos = (self.mid_w, self.mid_h + 2*self.button_buffer)
        self.add_button(self.back_pos, "Back_Button.png", "Hover_Back_Button.png", self.button_height, self.button_height, 'back')
        self.add_button(self.standard_pos, "Plate_Wide.png", "Hover_Plate_Wide.png", self.button_width, self.button_height, 'standard')
        self.add_button(self.precision_pos, "Plate_Wide.png", "Hover_Plate_Wide.png", self.button_width, self.button_height, 'precision')
        self.add_button(self.custom_pos, "Plate_Wide.png", "Hover_Plate_Wide.png", self.button_width, self.button_height, 'custom')

        self.highlight = pygame.transform.scale(pygame.image.load(os.path.join('resources', "Confirm_Button.png")), (self.button_height, self.button_height))
        # hl_pos = highlight positions
        self.mode_hl_pos = {
            'standard' : (self.standard_pos[0] + self.button_width//2 + self.DISPLAY_HEIGHT//40, self.standard_pos[1] - self.button_height//2),
            'precision' : (self.precision_pos[0] + self.button_width//2 + self.DISPLAY_HEIGHT//40, self.precision_pos[1] - self.button_height//2),
            'custom' : (self.custom_pos[0] + self.button_width//2 + self.DISPLAY_HEIGHT//40, self.custom_pos[1] - self.button_height//2),
        }
        self.current_hl_pos = self.mode_hl_pos['standard']

        # Gives a description of the gamemode when hovering over the mode
        self.mode_descriptions = {
            'standard' : ('A 6x7 board,', 'your classic connect 4 game'),
            'precision' : ('A single column with 5 rows,', 'first to 3 discs in wins'),
            'custom' : ('Create your own board size', 'and win condition'),
        }
        self.mode_desc_pos = {
            'standard' : (self.standard_pos[0] - self.button_width, self.standard_pos[1] - self.button_height//4),
            'precision' : (self.precision_pos[0] - self.button_width, self.precision_pos[1] - self.button_height//4),
            'custom' : (self.custom_pos[0] - self.button_width, self.custom_pos[1] - self.button_height//4),            
        }
        self.current_desc = self.mode_descriptions['standard']
        self.current_desc_pos = self.mode_desc_pos['standard']

    def draw_menu(self):
        self.run_display = True
        self.clog_buttons()
        while self.run_display:
            self.check_closed()
            self.DISPLAY.fill(self.bg)
            self.check_buttons()
            self.button_group.update()
            self.button_group.draw(self.DISPLAY)
            self.draw_text(self.standard_pos, self.text_size, "Standard")
            self.draw_text(self.precision_pos, self.text_size, "Precision")
            self.draw_text(self.custom_pos, self.text_size, "Custom")
            self.DISPLAY.blit(self.highlight, self.current_hl_pos)
            self.blit_menu()

    def draw_desc_text(self):
        self.draw_text(self.current_desc_pos, self.desc_text_size, self.current_desc[0])
        self.draw_text((self.current_desc_pos[0], self.current_desc_pos[1] + self.desc_text_size), self.desc_text_size, self.current_desc[1])

    def check_buttons(self):
        for button in self.buttons:
            if button.check_clicked():
                if button.function == 'back':
                    self.game.current_menu = self.game.settings_menu
                    self.run_display = False
                elif button.function == 'custom':
                    self.current_hl_pos = self.mode_hl_pos[button.function]
                    self.game.current_menu = self.game.custom_menu
                    self.run_display = False
                else:
                    self.game.game_mode = self.game.game_modes[button.function]
                    self.current_hl_pos = self.mode_hl_pos[button.function]
            if button.hovering:
                if button.function == 'back':
                    pass
                else:
                    self.current_desc_pos = self.mode_desc_pos[button.function]
                    self.current_desc = self.mode_descriptions[button.function]
                    self.draw_desc_text()


# Menu to pick the settings for a custom game mode
class CustomMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.rows = 6
        self.min_rows = 3
        self.max_rows = 7
        self.columns = 7
        self.min_columns = 3
        self.max_columns = 8
        self.connect = 4
        self.min_connect = 3
        # positions for each button
        self.back_pos = (self.mid_w, self.mid_h - self.button_buffer)
        self.rows_pos = (self.mid_w, self.mid_h)
        self.columns_pos = (self.mid_w, self.mid_h + self.button_buffer)
        self.connect_pos = (self.mid_w, self.mid_h + 2*self.button_buffer)
        self.button_buffer += self.button_width//2
        self.plate = pygame.transform.scale(pygame.image.load(os.path.join('resources', "Plate_Wide.png")), (self.button_width, self.button_height))

        self.add_button(self.back_pos, "Back_Button.png", "Hover_Back_Button.png", self.button_height, self.button_height, 'back')
        self.add_button((self.rows_pos[0] - self.button_buffer, self.rows_pos[1]), "Left_Button.png", "Hover_Left_Button.png", self.button_height, self.button_height, 'rows_left')
        self.add_button((self.rows_pos[0] + self.button_buffer, self.rows_pos[1]), "Right_Button.png", "Hover_Right_Button.png", self.button_height, self.button_height, 'rows_right')
        self.add_button((self.columns_pos[0] - self.button_buffer, self.columns_pos[1]), "Left_Button.png", "Hover_Left_Button.png", self.button_height, self.button_height, 'columns_left')
        self.add_button((self.columns_pos[0] + self.button_buffer, self.columns_pos[1]), "Right_Button.png", "Hover_Right_Button.png", self.button_height, self.button_height, 'columns_right')
        self.add_button((self.connect_pos[0] - self.button_buffer, self.connect_pos[1]), "Left_Button.png", "Hover_Left_Button.png", self.button_height, self.button_height, 'connect_left')
        self.add_button((self.connect_pos[0] + self.button_buffer, self.connect_pos[1]), "Right_Button.png", "Hover_Right_Button.png", self.button_height, self.button_height, 'connect_right')

    def draw_menu(self):
        self.run_display = True
        self.clog_buttons()
        while self.run_display:
            self.check_closed()
            self.check_buttons()
            self.DISPLAY.fill(self.bg)
            self.button_group.update()
            self.button_group.draw(self.DISPLAY)
            self.DISPLAY.blit(self.plate, (self.rows_pos[0] - self.button_width//2, self.rows_pos[1] - self.button_height//2))
            self.DISPLAY.blit(self.plate, (self.columns_pos[0] - self.button_width//2, self.columns_pos[1] - self.button_height//2))
            self.DISPLAY.blit(self.plate, (self.connect_pos[0] - self.button_width//2, self.connect_pos[1] - self.button_height//2))            
            self.draw_text(self.rows_pos, self.text_size, f"Rows: {self.rows}")
            self.draw_text(self.columns_pos, self.text_size, f"Columns: {self.columns}")
            self.draw_text(self.connect_pos, self.text_size, f"Connect: {self.connect}")
            self.blit_menu()

    def check_buttons(self):
        for button in self.buttons:
            if button.check_clicked():
                if button.function == 'back':
                    self.game.current_menu = self.game.game_mode_menu
                    self.game.game_mode = (self.rows, self.columns, self.connect)
                    self.run_display = False
                elif button.function == 'rows_left' and self.rows > self.min_rows:
                    self.rows -= 1
                elif button.function == 'rows_right' and self.rows < self.max_rows:
                    self.rows += 1
                elif button.function == 'columns_left' and self.columns > self.min_columns:
                    self.columns -= 1
                elif button.function == 'columns_right' and self.columns < self.max_columns:
                    self.columns += 1
                elif button.function == 'connect_left' and self.connect > self.min_connect:
                    self.connect -= 1
                elif button.function == 'connect_right' and self.connect < max(self.rows, self.columns):
                    self.connect += 1

                if self.connect > max(self.rows, self.columns):
                    self.connect = max(self.rows, self.columns)


