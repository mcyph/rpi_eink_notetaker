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
        os.unsetenv("DISPLAY")

        #os.putenv('SDL_FBDEV', '/dev/fb0')

        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = [#'RPI',
                   #'dispmanx',
                   'opengl',
                   'fbcon',
                   'directfb',
                   'svgalib',
                   ]
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
                print(f"Driver: {driver} opened.")
            except pygame.error:
                print(f"Driver: {driver} failed.")
                continue
            found = True
            break

        if not found:
            raise Exception('No suitable video driver found!')

        print("SDL DRIVER:", pygame.display.get_driver())

        size = self.size = (pygame.display.Info().current_w,
                            pygame.display.Info().current_h)
        print(f"Framebuffer size: {size[0]}x{size[1]}")

        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        self.clear()
        pygame.mouse.set_visible(False)
        pygame.font.init()
        self.update()

        os.putenv("DISPLAY", disp_no)

        self.cursor_surface = pygame.Surface((4, 4))
        self.stroke_surface = pygame.Surface(size)
        pygame.draw.ellipse(self.cursor_surface, (255, 0, 0), [0, 0, 4, 4])
        self.__current_id = 0
        self.__update_regions = []
        self.__cursor_pos = [0, 0]

    def __del__(self):
        """
        Destructor to make sure pygame shuts down, etc.
        """
        pass

    def clear(self):
        self.screen.fill((0, 0, 0))

    def draw(self, strokes, cursor_pos):
        if len(strokes) <= self.__current_id:
            self.__current_id = 0

        for stroke in strokes[self.__current_id:]:
            stroke = [
                (self.size[0]-round(y*(self.size[0]/1080.0)), round(x*(self.size[1]/1920.0)))
                for x, y in stroke
            ]
            pygame.draw.lines(self.stroke_surface, (255, 255, 255), False, stroke)
            self.__update_regions.append((min([x for x, y in stroke]), min([y for x, y in stroke]),
                                          max([x for x, y in stroke]), max([y for x, y in stroke])))
        self.__current_id = len(strokes)

        self.screen.blit(self.cursor_surface,
                         [self.size[0]-round(cursor_pos[1]*(self.size[0]/1080.0))-2,
                          round(cursor_pos[0]*(self.size[1]/1920.0))-2])

        self.__update_regions.append((self.__cursor_pos[0], self.__cursor_pos[1],
                                      self.__cursor_pos[0] + 4, self.__cursor_pos[1] + 4))
        self.__update_regions.append((cursor_pos[0], cursor_pos[1],
                                      cursor_pos[0]+4, cursor_pos[1]+4))
        self.__cursor_pos = cursor_pos

    def update(self):
        pygame.display.update(self.__update_regions)
        self.__update_regions = []
