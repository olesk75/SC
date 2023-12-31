import moderngl
from array import array
import time, os
import pygame as pg
from pathlib import Path
from icecream import ic
from dataclasses import dataclass

import settings



@dataclass()
class FightStatus:
    """
    Dataclass for state of game
    """

    p1_ship: str
    ai_ship: str

    win: bool = False

    p1_wins: int = 0
    ai_wins: int = 0


class GameGL:
    """
    Class which mostly calls the same methods for whatever state is currently active,
    including GAMEPLAY.

    It also handles the ModernGL integration

    The run() method is looping until the game exits
    """

    def __init__(self, states, start_state, FPS) -> None:
        self.done = False
        
        # Resolution and screen setup
        current_screen = pg.display.Info()
        monitor_res = (current_screen.current_w, current_screen.current_h)
        width, height = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT

        scale = (current_screen.current_h - 100) / settings.SCREEN_HEIGHT

        ic("Screen resolution", width, height, monitor_res)

        x = 10 
        y = 10
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)
        FLAGS = pg.OPENGL | pg.DOUBLEBUF  # flags = pg.FULLSCREEN | pg.HWSURFACE | pg.SCALED
        self.screen = pg.display.set_mode((width * scale, height * scale), FLAGS)

        """
        --------------------------------------------------------------------------------
        ModernGL 
        --------------------------------------------------------------------------------
        """

        # We need a context, and the create_context() method will detect and 
        # connect to the pygame window
        self.ctx = moderngl.create_context()
        ic(self.ctx.info["GL_RENDERER"])
        quad_buffer = self.ctx.buffer(data=array('f', [
        # vertex coordiantes (x,y), uv coords (x,y)
           -1.0, 1.0, 0.0, 0.0,  # top left
           1.0, 1.0, 1.0, 0.0,   # top right
           -1.0,-1.0, 0.0, 1.0,  # bottom left
           1.0, -1.0, 1.0, 1.0,  # bottom right
        ])) 

        glsl_folder = Path("glsl/")

        with open(glsl_folder / "vertex_shader.glsl", 'r') as file:
            vert_shader = file.read()

        # Runs for every pixel in the vertices defined in the vertex shader
        with open(glsl_folder / "frag_shader.glsl", 'r') as file:
            frag_shader = file.read()

        ic('Shader compilation start')
        self.program = self.ctx.program(vert_shader, frag_shader)  # compiles GLSL code
        self.render_object = self.ctx.vertex_array(self.program, [(quad_buffer, '2f 2f', 'in_vert', 'in_texcoord')])
        ic('Shader compilation end')
        self.start_time = time.time()

        self.clock = pg.time.Clock()
        self.FPS = FPS
        self.states = states
        self.state_name = start_state
        self.state = self.states[self.state_name]
        self.game_surface = pg.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.font = pg.font.Font("freesansbold.ttf", 32)
        self.game_status = []  # to be passed between states

        self.fight_status = FightStatus(p1_ship="martian", ai_ship="plutonian")

    # We need to convert our python surface into an OpenGL texture
    def surf_to_texture(self, surf) -> moderngl.Texture:
        tex = self.ctx.texture(surf.get_size(), 4)  # RGBA (4 component) f1 texture, as dype="f4" by default
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)  # how to convert pixels (try INEEAR)
        tex.swizzle = 'BGRA'  # swapping channels around between pygame and OpenGL
        tex.write(surf.get_view('1'))
        return tex


    def event_loop(self) -> None:
        for event in pg.event.get():
            self.state.get_event(event)

    def flip_state(self) -> None:
        current_state = self.state_name
        self.state.done = False
        next_state = self.state.next_state
        ic("State transition:", current_state, next_state)
        self.state_name = next_state
        self.state = self.states[self.state_name]
        self.state.startup(self.fight_status)

    def update(self) -> None:
        if self.state.quit:
            self.done = True
            ic("Player terminated game")
        elif self.state.done:
            self.flip_state()
        self.state.update()  # call the update function in active state

    def draw(self) -> None:
        self.state.draw(
            self.game_surface
        )  # call the update function in active state (on game_surface, not the screen)

        if settings.SHOW_FPS:
            fps_text = self.font.render(f"FPS: {self.clock.get_fps():.2f}", True, (255, 255, 0))
            self.game_surface.blit(fps_text, (10, 100))


        frame_tex = self.surf_to_texture(self.game_surface)
        frame_tex.use(0)  # Set use location 0
        self.program['u_tex'] = 0  #  Write to tex uniform the value 0
        #self.program['u_time'] = time.time() - self.start_time  # writing elapsed time to framentation shader
        self.render_object.render(mode=moderngl.TRIANGLE_STRIP)  # Triangle strip used to convert our quad_buffer
 
        #self.screen.blit(self.game_surface, (0, 0))

        pg.display.flip()

        frame_tex.release()  # free up VRAM - required!

        self.clock.tick(self.FPS)
        

    """ 
    This is the main game loop
    """

    def run(self) -> None:
        while not self.done:
            self.clock.tick(self.FPS)
            self.event_loop()
            self.update()
            self.draw()
