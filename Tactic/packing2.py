from rectpack import newPacker, PackingMode, SORT_AREA
from rectpack.maxrects import MaxRectsBl

packer = newPacker(mode=PackingMode.Offline, pack_algo=MaxRectsBl, sort_algo=SORT_AREA, rotation=False)

# Add the rectangles to packing queue
# for r in rectangles:
# 	packer.add_rect(*r)

# # Add the bins where the rectangles will be placed
# for b in bins:
# 	packer.add_bin(*b)

# Start packing



import pygame
import random

# ---- Pygame Visualization ----

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 500, 250
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Guillotine Bin Packing")

# Generate random boxes
num_boxes = 20
boxes = [(random.randint(20, 100), random.randint(20, 100)) for _ in range(num_boxes)]

container = (WIDTH, HEIGHT)
packer.add_bin(*container)


# Get positions using the Guillotine algorithm
#positions = guillotine_pack(WIDTH, HEIGHT, boxes)
#positions = arrange_boxes_shelf(HEIGHT, boxes)
#positions = arrange_boxes_next_fit(WIDTH, HEIGHT, boxes)
#positions = best_fit_pack(WIDTH, HEIGHT, boxes)

for box in boxes:
    packer.add_rect(*box)
    packer.pack()
 
    screen.fill((255, 255, 255))
    all_rects = packer.rect_list()
    # Draw boxes
    for (b, x, y, w, h, rid) in all_rects:
        pygame.draw.rect(screen, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (x, y, w, h))

    pygame.display.flip()
    pygame.time.wait(500)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
