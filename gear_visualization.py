import math
import cv2
import numpy as np
import os
import random

random.seed(4468)

# Colors for each layer.
layer_colors = [
    (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    for _ in range(100)
]

class GearGridVisualizer:
    def __init__(self, gear_grid, base_radius, screen_width=800, screen_height=600, save=True):
        self.gear_grid = gear_grid
        self.base_radius = base_radius

        rows = self.gear_grid.rows
        cols = self.gear_grid.cols
        self.world_width = int(cols * 2 * self.base_radius + self.base_radius * 0.4)
        self.world_height = int(rows * 2 * self.base_radius + self.base_radius * 0.4)

        self.window_x = 0
        self.window_y = 0
        self.zoom = 1.0

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.canvas = self._create_canvas()

        self.save = save
        self.canvas_idx = 0

        if self.save and not os.path.exists("images"):
            os.makedirs("images")

    def _create_canvas(self):
        return np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)

    def transform_point(self, x, y):
        screen_x = int((x - self.window_x) * self.zoom)
        screen_y = int((y - self.window_y) * self.zoom)
        return (screen_x, screen_y)

    def projected_circle(self, center, radius, color, thickness, **kwargs):
        center_screen = self.transform_point(center[0], center[1])
        radius_screen = int(radius * self.zoom)
        if (center_screen[0] + radius_screen < 0 or
            center_screen[0] - radius_screen > self.screen_width or
            center_screen[1] + radius_screen < 0 or
            center_screen[1] - radius_screen > self.screen_height):
            return
        cv2.circle(self.canvas, center=center_screen, radius=radius_screen,
                   color=color, thickness=thickness, **kwargs)

    def projected_fillPoly(self, pts, color, **kwargs):
        pts_screen = np.array([self.transform_point(x, y) for (x, y) in pts], dtype=np.int32)
        xs = pts_screen[:, 0]
        ys = pts_screen[:, 1]
        if (np.all(xs < 0) or np.all(xs > self.screen_width) or
            np.all(ys < 0) or np.all(ys > self.screen_height)):
            return
        cv2.fillPoly(self.canvas, [pts_screen], color, **kwargs)

    def projected_polylines(self, pts, isClosed, color, thickness, **kwargs):
        pts_screen = np.array([self.transform_point(x, y) for (x, y) in pts], dtype=np.int32)
        xs = pts_screen[:, 0]
        ys = pts_screen[:, 1]
        if (np.all(xs < 0) or np.all(xs > self.screen_width) or
            np.all(ys < 0) or np.all(ys > self.screen_height)):
            return
        cv2.polylines(self.canvas, [pts_screen], isClosed=isClosed,
                      color=color, thickness=thickness, **kwargs)

    def _draw_one_gear(self, gear, i, j, delta_angle):
        center_x = j * 2 * self.base_radius + self.base_radius * 1.2
        center_y = i * 2 * self.base_radius + self.base_radius * 1.2

        gear_radius = 0.75 * self.base_radius
        tooth_length = gear_radius * 0.4

        step = 360 / gear.num_teeth
        half_tooth_deg = 180 / gear.num_teeth
        angle_offset = delta_angle * gear.direction

        if gear.gear_type == "Driver":
            self.projected_circle((center_x, center_y),
                                  0.8 * gear_radius + tooth_length,
                                  color=(0, 255, 255), thickness=-1)

        gear_points_world = []

        for layer_idx in range(gear.num_layers):
            layer_factor = gear_radius / 30.0
            current_radius = gear_radius + 4 * (-layer_factor * layer_idx)
            current_tip_radius = gear_radius

            color = layer_colors[layer_idx % len(layer_colors)]
            
            if not (True in gear.layers_teeth_flags[layer_idx]):
                continue 
                
            for tooth_idx in range(gear.num_teeth):
                start_angle = angle_offset + tooth_idx * step - half_tooth_deg
                end_angle   = angle_offset + (tooth_idx + 1) * step - half_tooth_deg
                start_rad = math.radians(start_angle)
                end_rad   = math.radians(end_angle)

                p1_world = (
                    center_x + current_radius * math.cos(start_rad),
                    center_y + current_radius * math.sin(start_rad)
                )
                p2_world = (
                    center_x + current_radius * math.cos(end_rad),
                    center_y + current_radius * math.sin(end_rad)
                )

                sector_pts = [p1_world, p2_world, (center_x, center_y)]
                self.projected_fillPoly(sector_pts, color)
                gear_points_world.append(p1_world)

                if gear.layers_teeth_flags[layer_idx][tooth_idx]:
                    mid_angle = 0.5 * (start_rad + end_rad)
                    tip_world = (
                        center_x + (current_tip_radius + tooth_length) * math.cos(mid_angle),
                        center_y + (current_tip_radius + tooth_length) * math.sin(mid_angle)
                    )
                    tooth_pts = [p1_world, p2_world, tip_world]
                    self.projected_fillPoly(tooth_pts, color)
                    gear_points_world.append(tip_world)

            if layer_idx == 0 and gear_points_world:
                self.projected_polylines(gear_points_world, isClosed=True,
                                         color=(255, 0, 0), thickness=1)

    def draw_grid(self, delta_angle):
        self.canvas[:] = (0, 0, 0)
        for i, row in enumerate(self.gear_grid.grid):
            for j, gear in enumerate(row):
                if gear.will_rotate:
                    self._draw_one_gear(gear, i, j, delta_angle)
                else:
                    self._draw_one_gear(gear, i, j, 0)

        if self.save:
            self.save_canvas()

    def save_canvas(self):
        img_rgb = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2RGB)
        filename = f"images/{self.canvas_idx:04d}.png"
        cv2.imwrite(filename, img_rgb)
        self.canvas_idx += 1

    def move_window(self, dx, dy):
        self.window_x += dx
        self.window_y += dy

    def zoom_window(self, factor):
        self.zoom *= factor

    def set_window(self, x, y, zoom):
        self.window_x = x
        self.window_y = y
        self.zoom = zoom
        
    def set_zoom_xy(self, x, y, zoom):
        world_x = x / self.zoom + self.window_x
        world_y = y / self.zoom + self.window_y

        self.zoom = zoom

        self.window_x = world_x - x / self.zoom
        self.window_y = world_y - y / self.zoom

