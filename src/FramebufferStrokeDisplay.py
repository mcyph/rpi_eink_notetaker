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
        self.__current_id = 0
        self.__update_regions = []
        self.__cursor_pos = [0, 0]

        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print("I'm running under X display = {0}".format(disp_no))
        os.unsetenv("DISPLAY")

        #os.putenv('SDL_FBDEV', '/dev/fb0')

        drivers = ['RPI',
                   'dispmanx',
                   'opengl',
                   'fbcon',
                   'directfb',
                   'svgalib',
                   ]

        found = False
        for driver in drivers:
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
        self.screen = pygame.display.set_mode(size,
                                              pygame.FULLSCREEN
                                              #| pygame.DOUBLEBUF
                                              #| pygame.OPENGL
                                              | pygame.HWSURFACE
                                              )

        os.putenv("DISPLAY", disp_no)
        pygame.mouse.set_visible(False)
        pygame.font.init()

        self.cursor_surface = pygame.Surface((4, 4))
        self.blank_surface = pygame.Surface((4, 4))
        self.stroke_surface = pygame.Surface(size)
        self.rules_surface = pygame.Surface(size)
        pygame.draw.ellipse(self.cursor_surface, (255, 0, 0), [0, 0, 4, 4])

        for x in range(11):
            y = int(size[1]/10.0*x)
            pygame.draw.line(self.rules_surface, (0, 0, 100), (0, y), (size[0], y))

        self.clear()
        self.update()

    def __del__(self):
        """
        Destructor to make sure pygame shuts down, etc.
        """
        pass

    def clear(self):
        self.screen.fill((0, 0, 0))
        self.stroke_surface.fill((0, 0, 0))
        pygame.display.update()
        self.__current_id = 0

    def draw(self, strokes, cursor_pos):
        if len(strokes) < self.__current_id:
            self.__current_id = 0
            self.clear()

        changed = False
        for stroke in strokes[self.__current_id:]:
            stroke = [
                (self.size[0]-round(y*(self.size[0]/1080.0)),
                 round(x*(self.size[1]/1920.0)))
                for x, y in stroke
            ]
            if not stroke:
                continue
            elif len(stroke) == 1:
                stroke = stroke*2

            pygame.draw.lines(self.stroke_surface, (255, 255, 255), False, stroke)
            xmin = min([x for x, y in stroke])
            ymin = min([y for x, y in stroke])
            self.__update_regions.append(pygame.Rect(xmin, ymin,
                                                     max([x for x, y in stroke])-xmin,
                                                     max([y for x, y in stroke])-ymin))
            changed = True

        if changed:
            self.screen.blit(self.rules_surface, (0, 0))
            self.screen.blit(self.stroke_surface, (0, 0))
        self.__current_id = len(strokes)

        cursor_pos = [
            self.size[0]-round(cursor_pos[1]*(self.size[0]/1080.0))-2,
            round(cursor_pos[0]*(self.size[1]/1920.0))-2
        ]
        if abs(cursor_pos[0]-self.__cursor_pos[0]) > 4 or abs(cursor_pos[1]-self.__cursor_pos[1]) > 4:
            self.screen.blit(self.cursor_surface, cursor_pos)
            self.screen.blit(self.blank_surface, self.__cursor_pos)

            self.__update_regions.append(pygame.Rect(self.__cursor_pos[0], self.__cursor_pos[1], 4, 4))
            self.__update_regions.append(pygame.Rect(cursor_pos[0], cursor_pos[1], 4, 4))
            self.__cursor_pos = cursor_pos

    def update(self):
        if self.__update_regions:
            pygame.display.update(self.__update_regions)
            #pygame.display.flip()
        self.__update_regions = []
