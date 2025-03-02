import cv2
import random
from gear_logic import MultiLayerGearGrid
from gear_visualization import GearGridVisualizer
import time 
import os 

def reseter(grid, x, y, di=0):
    grid.grid[y][x].layers_teeth_flags[0][4] = True
    
    grid.grid[y - 1][x].gear_type = 'Driver'
    
    for i in range(4):
        grid.grid[y][x].layers_teeth_flags[1][(i - 1 + 8) % 8] = True
        grid.grid[y - 1][x].layers_teeth_flags[1][(i - 5 + di + 8) % 8] = True
    
    for i in range(3):
        grid.grid[y][x].layers_teeth_flags[2][(i - 1 + 4 + 8) % 8] = True
        grid.grid[y - 1][x].layers_teeth_flags[2][(i - 5 + 5 + di + 8) % 8] = True


def add_data_to_grid(grid, data, dx=0, dy=0):
    """
    Modify a given MultiLayerGearGrid using specified gear data.
    
    :param grid: The MultiLayerGearGrid instance to modify.
    :param data: List of tuples containing (position, layer, active_teeth, optional is_driver).
    :param dx: Horizontal shift for all positions.
    :param dy: Vertical shift for all positions.
    """
    # Process gear data
    for item in data:
        pos, layer, active_teeth = item[:3]
        is_driver = item[3] if len(item) > 3 else False
        
        shifted_pos = (pos[0] + dy, pos[1] + dx)
        
        if is_driver:
            grid.grid[shifted_pos[0]][shifted_pos[1]].gear_type = 'Driver'
        
        for tooth in active_teeth:
            grid.grid[shifted_pos[0]][shifted_pos[1]].layers_teeth_flags[layer][tooth] = True


def create_OR_gate():
    """
    Create a MultiLayerGearGrid with dimensions 10x8 and 4 layers using add_data_to_grid.
    """
    rows, cols = 8, 20
    num_layers = 4
    
    # Initialize the grid
    grid = MultiLayerGearGrid(rows, cols, num_layers)
    
        # Define gear activation data (position, layer, active_teeth, is_driver)
    data = [
        [[2, 2], 0, list(range(8)), True],  # Index 0 - Driver gear with all teeth activated in layer 0
        [[3, 2], 0, [1, 3, 5, 7]],  # Index 1 - Single gear with teeth 1, 3, 5, 7 active in layer 0
        [[3, 2], 1, [0, 2, 4, 6]],  # Index 2 - Same gear with teeth 0, 2, 4, 6 active in layer 2
        [[3, 1], 1, [1]],  # Index 3 - New gear to the left with tooth 7 active in layer 1
        [[3, 1], 2, [5, 4]],  # Index 4 - New gear to the left with teeth 3, 4 active in layer 2
        [[3, 0], 2, [1, 2], True],  # Index 5 - New driver to the left with teeth 1, 2 active in layer 2
        [[4, 2], 0, list(range(8))],  # Index 6 - Three consecutive gears below (3,2) with all teeth active in layer 0
        [[5, 2], 0, list(range(8))],  # Index 7 - Three consecutive gears below (3,2) with all teeth active in layer 0
        [[6, 2], 0, list(range(8))],  # Index 8 - Three consecutive gears below (3,2) with all teeth active in layer 0
        [[6, 2], 1, [2]],  # Index 9 - Gear at (6,2) with tooth 2 active in layer 1
        [[3, 3], 1, [5]],  # Index 10 - Mirroring the left-side gear (3,1)
        [[3, 3], 2, [0, 1]],  # Index 11 - Mirroring left-side activation
        [[3, 4], 2, [1, 2], True]  # Index 12 - Mirroring the left driver at (3,0)
    ]
    
    add_data_to_grid(grid, data, dx=2)
    data[5][2] = [6, 7]
    add_data_to_grid(grid, data, dx=8)
    data[12][2] = [6, 7]
    add_data_to_grid(grid, data, dx=14)
    
    return grid 

def create_wire_grid():
    """Create a default gear grid with dimensions 18×38, 4 layers, and mark one gear as 'Driver'."""
    rows, cols = 10, 20
    num_layers = 4
    grid = MultiLayerGearGrid(rows, cols, num_layers)
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

def save_gear_grid(grid, filename):
    """
    Save the current gear grid state to a JSON file.
    """
    grid.save_grid_state(filename)
    print(f"Gear grid state saved to: {filename}")

def create_my_gear_grid1():
    """
    Create a MultiLayerGearGrid with 7 rows × 7 cols, 3 layers and 8 teeth per gear.
    Randomly set the tooth flags and mark the four corner gears as 'Driver'.
    """
    rows, cols = 7, 7
    num_layers = 3

    # In the logical grid we only need rows, cols, num_layers (num_teeth defaults to 8)
    grid = MultiLayerGearGrid(rows, cols, num_layers)

    # Randomly initialize each gear's layers and set corner gears as Drivers.
    for row_idx, row in enumerate(grid.grid):
        for col_idx, gear in enumerate(row):
            for layer in range(num_layers):
                for i in range(gear.num_teeth):
                    gear.layers_teeth_flags[layer][i] = random.choice(
                        [True, True, True, False, False, False, False]
                    )
            if (row_idx == 0 and col_idx == 0) or \
               (row_idx == 0 and col_idx == cols - 1) or \
               (row_idx == rows - 1 and col_idx == 0) or \
               (row_idx == rows - 1 and col_idx == cols - 1):
                gear.gear_type = 'Driver'

    return grid

def generate_all_files():
    grid = create_wire_grid()
    save_gear_grid(grid, "wire.json")
    
    grid = create_OR_gate()
    save_gear_grid(grid, "OR_gate.json")


def main():
    last_filename = "last_file.txt"
    
    # Read JSON file name from last_file.txt if it exists; otherwise, use "wire.json".
    if os.path.exists(last_filename):
        with open(last_filename, 'r') as f:
            json_filename = f.read().strip()
    else:
        json_filename = "wire.json"
    
    # 3. Load the gear grid state back from the JSON file.
    grid = MultiLayerGearGrid.load_grid_state(json_filename)
    print(f"Gear grid loaded from: {json_filename}")

    # 4. Create the visualizer (base_radius is used for drawing layout).
    visualizer = GearGridVisualizer(grid, base_radius=25, screen_width = 1050, screen_height = 500)
    
    steps_per_rotation = 10
    # Each tooth (for an 8-tooth gear) covers 360/8 degrees; we split that into small steps.
    angle_step = 360 / 8 / steps_per_rotation
    total_iterations = 2400

    # Main animation loop.
    for iteration in range(total_iterations):
        grid.prepare_iteration()
        grid.iterate()

        # Draw partial rotation frames.
        for s in range(steps_per_rotation):
            delta_angle = angle_step * s
            visualizer.draw_grid(delta_angle)
            cv2.imshow('Gear Grid', visualizer.canvas)
            time.sleep(0.01)
            key = cv2.waitKey(1)  # Adjust speed here (1 ms per frame)
            if key == 113:  # Press 'q' to quit.
                cv2.destroyAllWindows()
                return

        # Rotate the gears that are flagged.
        grid.rotate_gears()
        
    cv2.destroyAllWindows()

if __name__ == "__main__":
    generate_all_files()
    main()
