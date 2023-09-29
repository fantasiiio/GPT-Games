import pygame
import math
from pygame.math import Vector2

class DashedLine:
    offset = 0

import math
import pygame
from pygame.math import Vector2

class DashedLine:
    offset = 0

    @staticmethod
    def draw(screen, start_pos, end_pos, dash_length, color, width=1):
        start_pos = Vector2(start_pos)
        end_pos = Vector2(end_pos)
        delta = end_pos - start_pos
        length = delta.length()
        dash_count = int(math.floor(length / dash_length))
        
        # Offset the starting point
        start_pos += delta.normalize() * (DashedLine.offset)
        
        dash_vec = delta.normalize() * dash_length

        for i in range(dash_count-1):  # +1 to make sure we reach or pass end_pos
            cur_pos = start_pos + dash_vec * i
            next_pos = cur_pos + dash_vec

            # Don't overshoot end_pos
            if next_pos.distance_to(start_pos) > end_pos.distance_to(start_pos):
                next_pos = end_pos

            if i % 2 == 0:  # Only draw the even dashes
                pygame.draw.line(screen, color, (int(cur_pos.x), int(cur_pos.y)), (int(next_pos.x), int(next_pos.y)), width)
        
        # Increment the offset for the next frame
        DashedLine.offset += 1
        if DashedLine.offset >= dash_length * 2:
            DashedLine.offset = 0

            
if __name__ == "__main__":
    def main():
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('Animated Dashed Line')

        clock = pygame.time.Clock()

        # Create a DashedLine instance
        dashed_line = DashedLine()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            screen.fill((0, 0, 0))

            # Draw and update the dashed line
            dashed_line.draw(screen, Vector2(100, 300), Vector2(700, 300), 20, (255, 255, 255))
            #dashed_line.update_DashedLine.offset()

            pygame.display.update()
            clock.tick(60)


    main()
