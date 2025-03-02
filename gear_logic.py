import json
import random

class MultiLayerGear:
    """
    A purely logical representation of a multi-layer gear:
    
      - num_teeth:          Number of teeth in a circular arrangement.
      - num_layers:         Number of layers (each with its own tooth pattern).
      - layers_teeth_flags: A list (for each layer) of booleans indicating which teeth are present.
      - gear_type:          "Driver" or "Driven" (determines if this gear forces rotation).
      - direction:          +1 or -1 (clockwise or counterclockwise).
      - will_rotate:        A flag indicating if the gear is set to rotate.
    """
    def __init__(self, num_teeth, num_layers, gear_type="Driven", direction=1):
        self.num_teeth = num_teeth
        self.num_layers = num_layers
        self.layers_teeth_flags = [[False] * num_teeth for _ in range(num_layers)]
        self.gear_type = gear_type
        self.direction = direction
        self.will_rotate = False

    def rotate_layer(self, layer, steps=1):
        if 0 <= layer < self.num_layers:
            # Rotate the list according to the gear's direction and steps.
            self.layers_teeth_flags[layer] = (
                self.layers_teeth_flags[layer][-self.direction * steps:] +
                self.layers_teeth_flags[layer][:-self.direction * steps]
            )

    def rotate(self, steps=1):
        for layer in range(self.num_layers):
            self.rotate_layer(layer, steps)

    def print_properties(self, label=""):
        print(f"{label}Gear Type: {self.gear_type}, Direction: {self.direction}")
        for layer_idx, layer_flags in enumerate(self.layers_teeth_flags):
            print(f"  Layer {layer_idx + 1} Flags: {layer_flags}")

    def copy(self):
        """
        Create a new MultiLayerGear with the same properties.
        """
        new_gear = MultiLayerGear(self.num_teeth, self.num_layers, self.gear_type, self.direction)
        # Make a shallow copy of each layer's list of booleans.
        new_gear.layers_teeth_flags = [list(layer) for layer in self.layers_teeth_flags]
        new_gear.will_rotate = self.will_rotate
        return new_gear


class MultiLayerGearGrid:
    """
    A 2D grid of MultiLayerGear objects with logic to:
      - Reset the rotation flags.
      - Propagate rotation flags to adjacent gears if their matching teeth are present.
      - Rotate the gears.
      - Save/load the grid state to/from a JSON file.
    """
    def __init__(self, rows, cols, num_layers, num_teeth=8):
        self.rows = rows
        self.cols = cols
        self.num_layers = num_layers
        self.num_teeth = num_teeth

        # Build a grid of "Driven" gears with alternating directions (+1 or -1).
        self.grid = []
        for i in range(rows):
            row_gears = []
            for j in range(cols):
                direction = ((i + j) % 2) * 2 - 1  # yields either +1 or -1.
                gear = MultiLayerGear(
                    num_teeth=num_teeth,
                    num_layers=num_layers,
                    gear_type="Driven",
                    direction=direction
                )
                row_gears.append(gear)
            self.grid.append(row_gears)

    def prepare_iteration(self):
        # Clear all rotation flags.
        for row in self.grid:
            for gear in row:
                gear.will_rotate = False

        # Set gears of type 'Driver' to rotate.
        for row in self.grid:
            for gear in row:
                if gear.gear_type == 'Driver':
                    gear.will_rotate = True

    def iterate(self):
        updated = True

        # Map logical positions (in terms of teeth indices).
        positions = {
            'top': 3 * self.num_teeth // 4,
            'bottom': self.num_teeth // 4,
            'left': self.num_teeth // 2,
            'right': 0
        }

        # Map positions to their opposites.
        opposite_positions = {
            'top': 'bottom',
            'bottom': 'top',
            'left': 'right',
            'right': 'left'
        }

        # Map grid neighbors.
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

                                ni, nj = neighbor_map[position](i, j)
                                if 0 <= ni < self.rows and 0 <= nj < self.cols:
                                    opposite_teeth_index = positions[opposite_positions[position]]
                                    if self.grid[ni][nj].layers_teeth_flags[layer][opposite_teeth_index]:
                                        if not self.grid[ni][nj].will_rotate:
                                            self.grid[ni][nj].will_rotate = True
                                            updated = True

    def rotate_gears(self, steps=1):
        for row in self.grid:
            for gear in row:
                if gear.will_rotate:
                    gear.rotate(steps=steps)

    def print_grid_properties(self):
        for i, row in enumerate(self.grid):
            for j, gear in enumerate(row):
                gear.print_properties(label=f"[{i},{j}] ")

    # Saving / Loading State

    def save_grid_state(self, filename):
        data = {
            "rows": self.rows,
            "cols": self.cols,
            "num_layers": self.num_layers,
            "num_teeth": self.num_teeth,
            "grid": []
        }
        for i in range(self.rows):
            row_data = []
            for j in range(self.cols):
                gear = self.grid[i][j]
                gear_info = {
                    "num_teeth": gear.num_teeth,
                    "num_layers": gear.num_layers,
                    "layers_teeth_flags": gear.layers_teeth_flags,
                    "gear_type": gear.gear_type,
                    "direction": gear.direction,
                    "will_rotate": gear.will_rotate
                }
                row_data.append(gear_info)
            data["grid"].append(row_data)

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_grid_state(cls, filename):
        with open(filename, "r") as f:
            data = json.load(f)

        grid_obj = cls(
            rows=data["rows"],
            cols=data["cols"],
            num_layers=data["num_layers"],
            num_teeth=data["num_teeth"]
        )

        for i in range(data["rows"]):
            for j in range(data["cols"]):
                gear_data = data["grid"][i][j]
                gear = grid_obj.grid[i][j]
                gear.num_teeth = gear_data["num_teeth"]
                gear.num_layers = gear_data["num_layers"]
                gear.layers_teeth_flags = gear_data["layers_teeth_flags"]
                gear.gear_type = gear_data["gear_type"]
                gear.direction = gear_data["direction"]
                gear.will_rotate = gear_data["will_rotate"]

        return grid_obj

    def copy(self):
        """
        Create a new MultiLayerGearGrid that is a copy of the current grid.
        """
        new_grid = MultiLayerGearGrid(self.rows, self.cols, self.num_layers, self.num_teeth)
        for i in range(self.rows):
            for j in range(self.cols):
                new_grid.grid[i][j] = self.grid[i][j].copy()
        return new_grid

