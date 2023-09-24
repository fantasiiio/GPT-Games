import pygame
import random

# ---- Guillotine Algorithm ----

class FreeRect:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def split(self, box_width, box_height):
        bottom_rect = FreeRect(self.width - box_width, box_height)
        bottom_rect.x = self.screen_x + box_width
        bottom_rect.y = self.screen_y

        right_rect = FreeRect(self.width, self.height - box_height)
        right_rect.x = self.screen_x
        right_rect.y = self.screen_y + box_height

        return [bottom_rect, right_rect]

def guillotine_pack(container_width, container_height, boxes):
    free_rects = [FreeRect(container_width, container_height)]
    positions = []

    for box in boxes:
        best_fit_area = float('inf')
        best_fit_rect_index = -1
        for i, rect in enumerate(free_rects):
            if box[0] <= rect.width and box[1] <= rect.height:
                area = rect.width * rect.height
                if area < best_fit_area:
                    best_fit_area = area
                    best_fit_rect_index = i

        if best_fit_rect_index == -1:
            raise ValueError("Couldn't fit all boxes")

        best_rect = free_rects.pop(best_fit_rect_index)
        positions.append((best_rect.x, best_rect.y))
        new_free_rects = best_rect.split(box[0], box[1])
        free_rects.extend(new_free_rects)

    return positions
# ---- Shelf Algorithm ----

class Shelf:
    def __init__(self, width):
        self.width = width
        self.used_width = 0
        self.height = 0
        self.boxes = []

    def can_fit(self, box):
        return self.used_width + box[0] <= self.width

    def add(self, box):
        self.boxes.append(box)
        self.used_width += box[0]
        self.height = max(self.height, box[1])

    def get_positions(self, start_y):
        x = 0
        positions = []
        for box in self.boxes:
            positions.append((x, start_y))
            x += box[0]
        return positions


def arrange_boxes_shelf(container_width, boxes):
    boxes = sorted(boxes, key=lambda x: x[1], reverse=True)
    shelves = [Shelf(container_width)]
    for box in boxes:
        added = False
        for shelf in shelves:
            if shelf.can_fit(box):
                shelf.add(box)
                added = True
                break
        if not added:
            new_shelf = Shelf(container_width)
            new_shelf.add(box)
            shelves.append(new_shelf)

    y = 0
    positions = []
    for shelf in shelves:
        positions.extend(shelf.get_positions(y))
        y += shelf.height

    return positions

# ---- next fit Algorithm ----

def arrange_boxes_next_fit(container_width, container_height, boxes):
    # Sorting boxes by height
    boxes = sorted(boxes, key=lambda x: x[1], reverse=True)

    # Starting position
    x, y = 0, 0

    # Current max height in this row
    current_row_max_height = 0

    positions = []

    for box in boxes:
        width, height = box

        # Check if the box fits at the current position
        if x + width <= container_width:
            positions.append((x, y))
            x += width
            current_row_max_height = max(current_row_max_height, height)
        else:
            # Move to the next row
            x = 0
            y += current_row_max_height

            if y + height > container_height:
                raise ValueError("Box doesn't fit in the container!")

            positions.append((x, y))
            x += width
            current_row_max_height = height

    return positions

def best_fit_pack(container_width, container_height, boxes):
    free_rects = [FreeRect(container_width, container_height)]
    positions = []

    for box in boxes:
        best_fit_rect_index = -1
        best_leftover_space = float('inf')

        for i, rect in enumerate(free_rects):
            if box[0] <= rect.width and box[1] <= rect.height:
                leftover_horz = rect.width - box[0]
                leftover_vert = rect.height - box[1]
                leftover = max(leftover_horz, leftover_vert)

                if leftover < best_leftover_space:
                    best_leftover_space = leftover
                    best_fit_rect_index = i

        if best_fit_rect_index == -1:
            raise ValueError("Couldn't fit all boxes")

        best_rect = free_rects.pop(best_fit_rect_index)
        positions.append((best_rect.x, best_rect.y))
        new_free_rects = best_rect.split(box[0], box[1])
        free_rects.extend(new_free_rects)

    return positions

# ---- Pygame Visualization ----

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Guillotine Bin Packing")

# Generate random boxes
num_boxes = 20
boxes = [(random.randint(20, 100), random.randint(20, 100)) for _ in range(num_boxes)]

# Get positions using the Guillotine algorithm
#positions = guillotine_pack(WIDTH, HEIGHT, boxes)
#positions = arrange_boxes_shelf(HEIGHT, boxes)
#positions = arrange_boxes_next_fit(WIDTH, HEIGHT, boxes)
positions = best_fit_pack(WIDTH, HEIGHT, boxes)
# Main loop
running = True

screen.fill((255, 255, 255))

# Draw boxes
for (x, y), (w, h) in zip(positions, boxes):
    pygame.draw.rect(screen, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (x, y, w, h))

pygame.display.flip()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
