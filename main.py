# main_tkinter.py

import tkinter as tk
from tkinter import filedialog
import os
import random
import cv2
import numpy as np
from PIL import Image, ImageTk

from gear_logic import MultiLayerGearGrid  # Ensure this module includes the custom copy() methods.
from gear_visualization import GearGridVisualizer  # Your visualization module.

def reseter(grid, x, y, di=0):
    grid.grid[y][x].layers_teeth_flags[0][4] = True
    
    grid.grid[y - 1][x].gear_type = 'Driver'
    
    for i in range(4):
        grid.grid[y][x].layers_teeth_flags[1][(i - 1 + 8) % 8] = True
        grid.grid[y - 1][x].layers_teeth_flags[1][(i - 5 + di + 8) % 8] = True
    
    for i in range(3):
        grid.grid[y][x].layers_teeth_flags[2][(i - 1 + 4 + 8) % 8] = True
        grid.grid[y - 1][x].layers_teeth_flags[2][(i - 5 + 5 + di + 8) % 8] = True

class GearApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gear Grid Animation")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Attempt to load the last-used JSON filename from a file.
        self.last_filename = self.load_last_filename()

        # Initialize gear grid & visualizer variables.
        self.grid_obj = None
        self.init_grid = None  # This will hold the initial grid state.
        self.visualizer = None

        # Animation control.
        self.playing = False
        self.animation_job = None
        self.steps_per_rotation = 3
        self.angle_step = 360 / 8 / self.steps_per_rotation  # For an 8-tooth gear.
        self.current_step = 0
        self.base_radius = 20

        # Variables to help with panning.
        self.last_mouse_x = None
        self.last_mouse_y = None

        # Create GUI buttons and image display.
        self.create_widgets()

        # Load last file if available; otherwise create a default grid.
        if self.last_filename and os.path.exists(self.last_filename):
            # Uncomment the next line to load from file when ready.
            # self.load_grid_from_file(self.last_filename)
            self.grid_obj = self.create_default_gear_grid()
        else:
            self.grid_obj = self.create_default_gear_grid()

        # Set the initial grid using the custom copy method.
        self.init_grid = self.grid_obj.copy()

        self.visualizer = GearGridVisualizer(self.grid_obj, base_radius=self.base_radius)

        # Show the initial image.
        self.update_canvas()

    def create_widgets(self):
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # Button to load a grid state from file.
        self.btn_load = tk.Button(button_frame, text="Load File", command=self.load_file)
        self.btn_load.pack(side=tk.LEFT, padx=2)

        # Toggle button: "Play" when paused, "Pause" when playing.
        self.btn_toggle = tk.Button(button_frame, text="Play", command=self.toggle_play)
        self.btn_toggle.pack(side=tk.LEFT, padx=2)

        # Step button: animate one step of grid iterations (only works when paused).
        self.btn_step = tk.Button(button_frame, text="Step", command=self.step_animation)
        self.btn_step.pack(side=tk.LEFT, padx=2)

        # Reset button: restore the grid to its initially loaded/default state.
        self.btn_reset = tk.Button(button_frame, text="Reset", command=self.reset_animation)
        self.btn_reset.pack(side=tk.LEFT, padx=2)

        # Label for displaying the gear grid image.
        self.image_label = tk.Label(self)
        self.image_label.pack(padx=5, pady=5)

        # Bind mouse events for drag (panning) and wheel (zooming).
        self.image_label.bind("<ButtonPress-1>", self.on_mouse_down)
        self.image_label.bind("<B1-Motion>", self.on_mouse_drag)
        self.image_label.bind("<MouseWheel>", self.on_mouse_wheel)   # Windows and macOS
        # For Linux (wheel up/down)
        self.image_label.bind("<Button-4>", self.on_mouse_wheel)
        self.image_label.bind("<Button-5>", self.on_mouse_wheel)

    def load_last_filename(self):
        """Load the last filename from 'last_file.txt' if it exists."""
        try:
            with open("last_file.txt", "r") as f:
                return f.read().strip()
        except Exception:
            return None

    def save_last_filename(self, filename):
        """Save the last-used filename to 'last_file.txt'."""
        with open("last_file.txt", "w") as f:
            f.write(filename)

    def load_file(self):
        """Open a file dialog to load a gear grid JSON file."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if filename:
            self.load_grid_from_file(filename)
            self.save_last_filename(filename)

    def load_grid_from_file(self, filename):
        """Load the gear grid state from a JSON file and reinitialize the visualizer."""
        try:
            self.grid_obj = MultiLayerGearGrid.load_grid_state(filename)
            # Set the initial grid using the custom copy method.
            self.init_grid = self.grid_obj.copy()
            self.visualizer = GearGridVisualizer(self.grid_obj, base_radius=self.base_radius)
            self.current_step = 0
            self.update_canvas()
        except Exception as e:
            print("Error loading file:", e)

    def create_default_gear_grid(self):
        """Create a default gear grid with dimensions 18×38, 4 layers, and mark one gear as 'Driver'."""
#        rows, cols = 18, 38
        rows, cols = 10, 20
        num_layers = 4
        random.seed(4468)
        grid = MultiLayerGearGrid(rows, cols, num_layers)
        # For example, set a specific gear as a 'Driver'.
        grid.grid[1][1].layers_teeth_flags[0][7] = True
        grid.grid[1][1].gear_type = 'Driver'
        
        grid.grid[1][2].layers_teeth_flags[0][0] = True
        grid.grid[1][2].layers_teeth_flags[0][4] = True

        reseter(grid, 3, 1)
        reseter(grid, 6, 1, -1)
        reseter(grid, 8, 1, -1)
        reseter(grid, 10, 1, -1)
        reseter(grid, 12, 1, -1)
                
        for i in range(8):
            grid.grid[1][4].layers_teeth_flags[0][i] = True
            grid.grid[1][5].layers_teeth_flags[0][i] = True
            grid.grid[1][7].layers_teeth_flags[0][i] = True
            grid.grid[1][9].layers_teeth_flags[0][i] = True
            grid.grid[1][11].layers_teeth_flags[0][i] = True
        
        
        return grid

    def toggle_play(self):
        """Toggle between play and pause states."""
        if self.playing:
            self.playing = False
            self.btn_toggle.config(text="Play")
            if self.animation_job is not None:
                self.after_cancel(self.animation_job)
                self.animation_job = None
        else:
            self.playing = True
            self.btn_toggle.config(text="Pause")
            self.animation_loop()

    def reset_animation(self):
        """
        Reset the gear grid to the initially loaded state while preserving the current
        virtual window settings (zoom and pan).
        """
        self.playing = False
        if self.animation_job is not None:
            self.after_cancel(self.animation_job)
            self.animation_job = None

        # Preserve the current virtual window state.
        current_zoom = self.visualizer.zoom
        current_window_x = self.visualizer.window_x
        current_window_y = self.visualizer.window_y

        # Restore grid using the custom copy method.
        self.grid_obj = self.init_grid.copy()

        # Reinitialize the visualizer with the new grid.
        self.visualizer = GearGridVisualizer(self.grid_obj, base_radius=self.base_radius)
        # Restore the window settings.
        self.visualizer.zoom = current_zoom
        self.visualizer.window_x = current_window_x
        self.visualizer.window_y = current_window_y

        self.current_step = 0
        self.btn_toggle.config(text="Play")
        self.update_canvas()


    def step_animation(self):
        """
        Advance one iteration step of the grid.
        This method is effective only when the animation is paused.
        """
        if self.playing:
            return  # Do nothing if animation is playing.
        self.grid_obj.prepare_iteration()
        self.grid_obj.iterate()
        if self.current_step < self.steps_per_rotation - 1:
            self.current_step += 1
        else:
            self.current_step = 0
            self.grid_obj.rotate_gears()
        self.update_canvas()

    def update_canvas(self):
        """Render the current gear grid frame and update the Tkinter image."""
        if self.visualizer:
            self.visualizer.draw_grid(self.angle_step * self.current_step)
            # Convert the OpenCV BGR image to RGB.
            cv_img_rgb = cv2.cvtColor(self.visualizer.canvas, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(cv_img_rgb)
            imgtk = ImageTk.PhotoImage(image=im)
            self.image_label.imgtk = imgtk  # Keep a reference.
            self.image_label.configure(image=imgtk)

    def animation_loop(self):
        """The main animation loop using Tkinter's after() method."""
        if self.playing:
            self.grid_obj.prepare_iteration()
            self.grid_obj.iterate()
            if self.current_step < self.steps_per_rotation - 1:
                self.current_step += 1
            else:
                self.current_step = 0
                self.grid_obj.rotate_gears()
            self.update_canvas()
            self.animation_job = self.after(1, self.animation_loop)

    def on_close(self):
        """Cancel any pending jobs and close the window."""
        if self.animation_job is not None:
            self.after_cancel(self.animation_job)
        self.destroy()

    # --- Mouse event handlers for panning and zooming ---

    def on_mouse_down(self, event):
        """Store the current mouse position when the left button is pressed."""
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

    def on_mouse_drag(self, event):
        """
        Adjust the virtual window's position based on mouse drag.
        The displacement (in screen coordinates) is converted to world coordinates
        (by dividing by the zoom factor), and then subtracted from the window's position.
        """
        if self.last_mouse_x is None or self.last_mouse_y is None:
            return

        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y

        # Convert screen displacement to world displacement.
        dx_world = dx / self.visualizer.zoom
        dy_world = dy / self.visualizer.zoom

        # Moving the mouse right (positive dx) should move the window left.
        self.visualizer.move_window(-dx_world, -dy_world)

        # Update last mouse positions.
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

        self.update_canvas()

    def on_mouse_wheel(self, event):
        """
        Adjust the virtual window's zoom level based on the mouse wheel.
        The zoom is centered on the mouse pointer. For Windows and macOS,
        event.delta is used; for Linux, event.num is used.
        """

        # Determine zoom factor.
        if hasattr(event, 'delta') and event.delta != 0:
            # Windows / macOS: event.delta > 0 for scroll up (zoom in).
            if event.delta > 0:
                factor = 1.1
            else:
                factor = 0.9
        else:
            # Linux: Button-4 (zoom in), Button-5 (zoom out).
            if event.num == 4:
                factor = 1.1
            elif event.num == 5:
                factor = 0.9
            else:
                factor = 1.0

        new_zoom = self.visualizer.zoom * factor

        # Zoom around the mouse pointer position (event.x, event.y) in canvas coordinates.
        self.visualizer.set_zoom_xy(event.x, event.y, new_zoom)
        self.update_canvas()

if __name__ == "__main__":
    app = GearApp()
    app.mainloop()

