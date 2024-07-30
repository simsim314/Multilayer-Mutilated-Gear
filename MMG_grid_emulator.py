import numpy as np
import cv2
import math
import random
import json 
import time
import os 

class MultiLayerGear:
    def __init__(self, center, radius, num_teeth, gear_type, direction, num_layers):
        self.center = center
        self.radius = radius
        self.num_teeth = num_teeth
        self.num_layers = num_layers
        self.layers_teeth_flags = [[False] * num_teeth for _ in range(num_layers)]
        self.tooth_length = radius * 0.4
        self.gear_type = gear_type
        self.direction = direction
        self.will_rotate = False
        self.layer_colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255)] 

    def rotate_layer(self, layer, steps=1):
        if 0 <= layer < self.num_layers:
            self.layers_teeth_flags[layer] = self.layers_teeth_flags[layer][-self.direction * steps:] + self.layers_teeth_flags[layer][:-self.direction * steps]
            
    def rotate(self, steps=1):
        for layer in range(self.num_layers):
            self.rotate_layer(layer, 1)
            
    def draw(self, image, delta_angle):
        step = 360 / self.num_teeth
        delta = 180 / self.num_teeth
        angle = delta_angle * self.direction
        layer_colors = self.layer_colors
        
        
        if self.gear_type == "Driver":
           # Draw a red circle at the center
            cv2.circle(image, self.center, int(0.8 * self.radius) + int(self.tooth_length), (0, 255, 255), -1) 

        for layer in range(self.num_layers):
            factor = self.radius / 30.
            current_radius = self.radius + (-8 * factor * layer)
            current_tip_radius = self.radius# + (-3 * factor * layer)
            color = layer_colors[layer]
            
            for i in range(self.num_teeth):
                start_angle = math.radians(angle + i * step - delta)
                end_angle = math.radians(angle + (i + 1) * step - delta)
                
                point1 = (int(self.center[0] + current_radius * math.cos(start_angle)),
                          int(self.center[1] + current_radius * math.sin(start_angle)))
                point2 = (int(self.center[0] + current_radius * math.cos(end_angle)),
                          int(self.center[1] + current_radius * math.sin(end_angle)))
                
                # Fill the octagon (gear body)
                octagon_points = [
                    point1,
                    point2,
                    self.center
                ]
                cv2.fillPoly(image, [np.array(octagon_points, dtype=np.int32)], color)
                
                # Draw and fill the triangle (tooth) only if the flag is true for this layer
                if self.layers_teeth_flags[layer][i]:
                    avg_angle = (start_angle + end_angle) / 2
            
                    tip_point = (int(self.center[0] + (current_tip_radius + self.tooth_length) * math.cos(avg_angle)),
                             int(self.center[1] + (current_tip_radius + self.tooth_length) * math.sin(avg_angle)))
                
                    tooth_points = [tip_point, point1, point2]
                    cv2.fillPoly(image, [np.array(tooth_points, dtype=np.int32)], color)

    def print_properties(self):
        print(f"MultiLayerGear at {self.center} - Type: {self.gear_type}")
        for layer in range(self.num_layers):
            positions = {
                'top': 3 * self.num_teeth // 4,
                'bottom': self.num_teeth // 4,
                'left': self.num_teeth // 2,
                'right': 0
            }
            print(f"Layer {layer + 1}:")
            for position, index in positions.items():
                print(f"{position.capitalize()}: {'True' if self.layers_teeth_flags[layer][index] else 'False'}")

class MultiLayerGearGrid:
    def __init__(self, rows, cols, radius, num_layers):
        self.rows = rows
        self.cols = cols
        self.radius = radius
        self.num_layers = num_layers
        self.grid = [[MultiLayerGear((int(j * 2 * radius + radius * 1.2), int(i * 2 * radius + radius * 1.2)), radius * 0.75, 8, 'Driven', (i + j) % 2 * 2 - 1, num_layers)
                      for j in range(cols)] for i in range(rows)]
        
    def prepare_iteration(self):
        for row in self.grid:
            for gear in row:
                gear.will_rotate = False
        
        for row in self.grid:
            for gear in row:
                if gear.gear_type == 'Driver':
                    gear.will_rotate = True

    def iterate(self):
        updated = True

        # Logical map for gear connections
        positions = {
            'top': 3 * self.grid[0][0].num_teeth // 4,
            'bottom': self.grid[0][0].num_teeth // 4,
            'left': self.grid[0][0].num_teeth // 2,
            'right': 0
        }

        # Dictionary to map directions to their opposite directions
        opposite_positions = {
            'top': 'bottom',
            'bottom': 'top',
            'left': 'right',
            'right': 'left'
        }

        # Dictionary to map grid indices for each position
        neighbor_map = {
            'top': lambda i, j: (i - 1, j),
            'bottom': lambda i, j: (i + 1, j),
            'left': lambda i, j: (i, j - 1),
            'right': lambda i, j: (i, j + 1)
        }

        while updated:
            updated = False
            for i in range(self.rows):
                for j in range(self.cols):
                    if self.grid[i][j].will_rotate:
                        for layer in range(self.num_layers):
                            for position, neighbor_teeth_index in positions.items():
                                if not self.grid[i][j].layers_teeth_flags[layer][neighbor_teeth_index]:
                                    continue 
                                    
                                neighbor_pos = neighbor_map[position](i, j)
                                if 0 <= neighbor_pos[0] < self.rows and 0 <= neighbor_pos[1] < self.cols:
                                    ni, nj = neighbor_pos
                                    opposite_teeth_index = positions[opposite_positions[position]]
                                    if self.grid[ni][nj].layers_teeth_flags[layer][opposite_teeth_index]:
                                        if not self.grid[ni][nj].will_rotate:
                                            self.grid[ni][nj].will_rotate = True
                                            updated = True

    def draw(self, image, delta_angle):
        for row in self.grid:
            for gear in row:
                if gear.will_rotate:
                    gear.draw(image, delta_angle)
                else:
                    gear.draw(image, 0)

    def rotate_gears(self):
        for row in self.grid:
            for gear in row:
                if gear.will_rotate:
                   gear.rotate()
                   
    def print_grid_properties(self):
        for row in self.grid:
            for gear in row:
                gear.print_properties()

if __name__ == "__main__":
    idx = 0
    
    rows = 7
    cols = 7
    radius = 50  # Smaller radius
    num_layers = 3
    random.seed(4468)
    multi_layer_gear_grid = MultiLayerGearGrid(rows, cols, radius, num_layers)

    # Randomly set teeth flags for each layer in each gear
    for row_idx, row in enumerate(multi_layer_gear_grid.grid):
        for col_idx, gear in enumerate(row):
            for layer in range(num_layers):
                for i in range(gear.num_teeth):
                    gear.layers_teeth_flags[layer][i] = random.choice([True, True, True, False, False, False, False])

            # Set driver gears in the corners
            if (row_idx == 0 and col_idx == 0) or \
               (row_idx == 0 and col_idx == cols - 1) or \
               (row_idx == rows - 1 and col_idx == 0) or \
               (row_idx == rows - 1 and col_idx == cols - 1):
                gear.gear_type = 'Driver'

    # Ensure the output directory exists
    # output_dir = "Multi_Layer_Gear_Grid"
    # if not os.path.exists(output_dir):
        # os.makedirs(output_dir)

    steps = 10  # Faster rotation with more steps
    angle_step = 360 / 8 / steps  # Rotate by 360/8 degrees in given steps
    image = np.zeros((int(rows * 2 * radius + radius * 0.4), int(cols * 2 * radius + radius * 0.4), 3), dtype=np.uint8)
    iter_steps = 2400

    for iter_step in range(iter_steps):
        multi_layer_gear_grid.prepare_iteration()
        multi_layer_gear_grid.iterate()

        for step in range(steps):
            delta_angle = angle_step * step
            image[:] = (0, 0, 0)
            multi_layer_gear_grid.draw(image, delta_angle)
            cv2.imshow('Gear Grid', image)
            cv2.waitKey(1)  # Control animation speed
            # Save the image
            # filename = os.path.join(output_dir, f"{idx + 1:06d}.png")
            # save is commented out
            # cv2.imwrite(filename, image)
            idx += 1

        # Rotate the gears
        multi_layer_gear_grid.rotate_gears()
        k = cv2.waitKey(1)
        
        if k == 113:
            cv2.destroyAllWindows()
            exit()

    cv2.destroyAllWindows()
