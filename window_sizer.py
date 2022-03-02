import tkinter as tk
#from PIL import Image


class StartWindow:
    def __init__(self):
        # Only launches the game if launch button is pressed
        self.launched_game = False

        self.WIDTH = 500
        self.HEIGHT = 250

        self.game_width = 1200
        self.min_game_width, self.max_game_width = 800, 1600

        self.game_height = 600
        self.min_game_height, self.max_game_height = self.min_game_width//2, self.max_game_width//2

        self.blue = '#285ad2'
        self.red = '#e52d26'
        self.yellow = '#ded524'        

        self.root = tk.Tk()
        defaultbg = self.root.cget('bg')
        self.root.resizable(False, False)
        self.root.title("Catapult Connect 4 Set Up")

        self.canvas = tk.Canvas(self.root, width=self.WIDTH, height=self.HEIGHT, bg=self.blue)
        self.canvas.pack()

        # bg_img = tk.PhotoImage(file='resources/Title_Card.png')
        # bg_label = tk.Label(self.root, image=bg_img)
        # bg_label.place(relwidth=1, relheight=1)

        self.frame_colour = defaultbg
        self.frame_border = 0
        self.frame_width = 0.5

        # creates the title and instructional area
        self.header_frame = tk.Frame(self.root, bg=self.blue, bd=self.frame_border)
        self.header_frame.place(relx=0.5, rely=0.1, relwidth=0.8, relheight=0.25, anchor='n')
        self.fill_header_frame(self.header_frame)

        self.width_text = tk.StringVar()
        self.width_text.set(str(self.game_width))
        self.height_text = tk.StringVar()
        self.height_text.set(str(self.game_height))

        self.increase_size = self.change_size(1)
        self.bulk_increase_size = self.change_size(25)
        self.decrease_size = self.change_size(-1)
        self.bulk_decrease_size = self.change_size(-25)        

        # creates the area for sizing display
        self.width_frame = tk.Frame(self.root, bg=self.blue, bd=self.frame_border)
        self.width_frame.place(relx=0.5, rely=0.4, relwidth=self.frame_width, relheight=0.2, anchor='n')
        self.width_label = self.fill_sizing_frame(self.width_frame, 'Window width:', self.width_text)

        self.height_frame = tk.Frame(self.root, bg=self.blue, bd=self.frame_border)
        self.height_frame.place(relx=0.5, rely=0.6, relwidth=self.frame_width, relheight=0.2, anchor='n')
        self.height_label = self.fill_sizing_frame(self.height_frame, 'Window height:', self.height_text)

        self.launch_button = tk.Button(self.root, text='Launch', command=self.launch, bd=1)
        self.launch_button.place(relx=0.5, rely=0.85, relwidth=0.25, relheight=0.1, anchor='n')

    def change_size(self, height_increment):
        h_inc = height_increment
        def inner_function():
            if self.min_game_height <= self.game_height + h_inc <= self.max_game_height:
                self.game_width += (h_inc * 2)
                self.game_height += h_inc

            elif self.game_height + h_inc < self.min_game_height:
                self.game_width = self.min_game_width
                self.game_height = self.min_game_height 

            elif self.game_height + h_inc > self.max_game_height:
                self.game_width = self.max_game_width
                self.game_height = self.max_game_height     

            self.refresh_entries()      
        return inner_function       

    def fill_header_frame(self, frame):
        rel_title_height = 0.75
        rel_instruc_height = 1 - rel_title_height

        title_label = tk.Label(frame, text='Catapult Connect 4 Launcher', font=('', 20), bg=self.blue)
        title_label.place(relwidth=1, relheight=rel_title_height)

        instructions_label = tk.Label(frame, text='Select the window size for the game', bg=self.blue)
        instructions_label.place(rely=rel_title_height, relwidth=1, relheight=rel_instruc_height)

    def fill_sizing_frame(self, frame, header_text, entry_text): 
        rel_header_height = 0.5
        rel_entry_height = 1 - rel_header_height

        rel_entry_width = 0.4
        rel_button_width = (1-rel_entry_width)/4
        current_x = 0

        label = tk.Label(frame, text=header_text, bg=self.blue)
        label.place(relheight=rel_header_height)

        sizing_label = tk.Label(frame, textvariable=entry_text, borderwidth=1, bg='white')
        sizing_label.place(rely=rel_header_height, relwidth=rel_entry_width, relheight=rel_entry_height)

        current_x += rel_entry_width
        bulk_down_button = tk.Button(frame, text='<<', command=self.bulk_decrease_size, borderwidth=1, bg=self.red)
        bulk_down_button.place(relx=current_x, rely=rel_header_height, relwidth=rel_button_width, relheight=rel_entry_height)

        current_x += rel_button_width
        down_button = tk.Button(frame, text='<', command=self.decrease_size, borderwidth=1, bg=self.red)
        down_button.place(relx=current_x, rely=rel_header_height, relwidth=rel_button_width, relheight=rel_entry_height)

        current_x += rel_button_width
        up_button = tk.Button(frame, text='>', command=self.increase_size, borderwidth=1, bg=self.yellow)
        up_button.place(relx=current_x, rely=rel_header_height, relwidth=rel_button_width, relheight=rel_entry_height)

        current_x += rel_button_width
        bulk_up_button = tk.Button(frame, text='>>', command=self.bulk_increase_size, borderwidth=1, bg=self.yellow) 
        bulk_up_button.place(relx=current_x, rely=rel_header_height, relwidth=rel_button_width, relheight=rel_entry_height)

        return sizing_label

    def refresh_entries(self):
            self.width_text.set(str(self.game_width))
            self.height_text.set(str(self.game_height))   

    def run(self):
        self.root.mainloop()

    def launch(self):
        self.launched_game = True
        self.root.destroy()
