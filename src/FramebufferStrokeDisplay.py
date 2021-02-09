import os
import time
import pygame
import random


class FramebufferStrokeDisplay:
    def __init__(self):
        """
        Initializes a new pygame screen using the framebuffer
        """
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print("I'm running under X display = {0}".format(disp_no))

        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                print(f"Driver: {driver} failed.")
                continue
            found = True
            break

        if not found:
            raise Exception('No suitable video driver found!')

        size = self.size = (pygame.display.Info().current_w,
                            pygame.display.Info().current_h)
        print(f"Framebuffer size: {size[0]}x{size[1]}")

        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        self.clear()
        pygame.font.init()
        self.update()

    def __del__(self):
        """
        Destructor to make sure pygame shuts down, etc.
        """
        pass

    def clear(self):
        self.screen.fill((0, 0, 0))

    def draw(self, strokes, cursor_pos):
        strokes_out = []
        for stroke in strokes:
            stroke = [
                (round(x*(self.size[0]/1920.0)),
                 round(y*(self.size[1]/1080.0)))
                for x, y in stroke
            ]
            strokes_out.append(stroke)
        strokes = strokes_out

        pygame.draw.lines(self.screen, (255, 255, 255), False,
                          strokes)
        pygame.draw.ellipse(self.screen, (0, 255, 255),
                            [cursor_pos[0], cursor_pos[1], 1, 1])

    def update(self):
        pygame.display.update()
