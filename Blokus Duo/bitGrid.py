import math
import pickle

class BitGrid():
    def __init__(self, x_bits, uncompress_grid = None):
        self.compressed_grid = []
        self.x_bits = x_bits
        if uncompress_grid is not None:
            self.compressed_grid = self.compress_grid_x_bits(uncompress_grid)

    def copy(self):
        new_grid = BitGrid(self.x_bits)
        new_grid.compressed_grid = self.compressed_grid[:]
        return new_grid

    def required_bits(n):
        """Return the number of bits needed to store the given integer."""
        if n < 0:
            raise ValueError("The function only supports non-negative integers.")
        if n == 0:
            return 1  # Special case: 0 requires 1 bit
        return math.ceil(math.log2(n + 1))
    
    # Function to compress a 14x14 grid using variable bit-level compression
    def compress_grid_x_bits(self, grid):
        self.compressed_grid = []
        buffer = 0  # 64-bit buffer to store bits
        buffer_size = 0  # Number of bits currently stored in the buffer
        
        max_value = 2 ** self.x_bits - 1  # Maximum value that can be stored with self.x_bits
        
        for row in grid:
            for num in row:
                if num > max_value:
                    raise ValueError(f"Number {num} cannot be represented with {self.x_bits} bits.")
                
                # Add the self.x_bits binary representation of the number to the buffer
                buffer = (buffer << self.x_bits) | num
                buffer_size += self.x_bits
                
                # If the buffer is filled (or more), append it to the compressed data
                if buffer_size >= 64:
                    self.compressed_grid.append(buffer)
                    buffer_size -= 64
                    buffer &= ((1 << buffer_size) - 1)  # Keep the remaining bits
                    
        # Append any remaining bits to the compressed data
        if buffer_size > 0:
            self.compressed_grid.append(buffer)
            
        return self.compressed_grid

    # Function to decompress a 14x14 grid using variable bit-level compression
    def decompress_grid_x_bits(self):
        decompressed_grid = [[0 for _ in range(14)] for _ in range(14)]
        buffer = 0  # 64-bit buffer to store bits
        buffer_size = 0  # Number of bits currently stored in the buffer
        i, j = 0, 0  # Row and column indices for the decompressed grid
        
        for data in self.compressed_grid:
            buffer = (buffer << 64) | data
            buffer_size += 64
            
            while buffer_size >= self.x_bits and i < 14:
                # Extract the first self.x_bits
                mask = (1 << self.x_bits) - 1  # Create a mask to extract self.x_bits
                num = (buffer >> (buffer_size - self.x_bits)) & mask
                
                # Place the number in the decompressed grid
                decompressed_grid[i][j] = num
                j += 1
                if j == 14:
                    j = 0
                    i += 1
                    
                # Update the buffer
                buffer_size -= self.x_bits
                buffer &= ((1 << buffer_size) - 1)  # Keep the remaining bits
                
        return decompressed_grid


    # Function to write a single number to a compressed grid
    def write(self, row, col, new_number):
        max_value = 2 ** self.x_bits - 1  # Maximum value that can be stored with self.x_bits
        if new_number > max_value:
            raise ValueError(f"Number {new_number} cannot be represented with {self.x_bits} bits.")
        
        # Calculate the position in the compressed data
        pos = col * 14 + row
        chunk_index = pos // (64 // self.x_bits)  # The index of the 64-bit integer that contains the number
        chunk_pos = pos % (64 // self.x_bits)  # The position of the number within the 64-bit integer
        
        # Extract the 64-bit integer and clear the bits corresponding to the number to be replaced
        mask_clear = ~((max_value) << (64 - self.x_bits * (chunk_pos + 1)))  # Mask to clear bits
        self.compressed_grid[chunk_index] &= mask_clear
        
        # Set the new bits
        mask_set = new_number << (64 - self.x_bits * (chunk_pos + 1))  # Mask to set bits
        self.compressed_grid[chunk_index] |= mask_set

    # Function to read a single number from a compressed grid
    def read(self, row, col):
        # Calculate the position in the compressed data
        pos = col * 14 + row
        chunk_index = pos // (64 // self.x_bits)  # The index of the 64-bit integer that contains the number
        chunk_pos = pos % (64 // self.x_bits)  # The position of the number within the 64-bit integer
        
        # Extract the number
        mask = (1 << self.x_bits) - 1  # Mask to extract self.x_bits
        num = (self.compressed_grid[chunk_index] >> (64 - self.x_bits * (chunk_pos + 1))) & mask
        
        return num
    
    def save_to_file(self, filename="grid.txt"):
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load_from_file(filename="grid.txt"):
        with open(filename, 'rb') as file:
            return pickle.load(file)

# grid = BitGrid(2)

# given_grid = [
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [2, 2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
#     [2, 2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
#     [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [2, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
#     [2, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1]
# ]

# print(grid.compress_grid_x_bits(given_grid))