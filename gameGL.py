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
        scale = 1  # TODO: fix scaling. Right now it breaks uv coords for the frag shader

        ic("Screen resolution", width, height, monitor_res)
        
        # Tons of stuff to prevent Macs from freaking out
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (10,10)  # We place scaled window top left

        FLAGS = pg.OPENGL | pg.DOUBLEBUF  # flags = pg.FULLSCREEN | pg.HWSURFACE | pg.SCALED
        self.screen = pg.display.set_mode((width * scale, height * scale), FLAGS)
        self.game_surface = pg.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

        """
        --------------------------------------------------------------------------------
        ModernGL 
        --------------------------------------------------------------------------------
        """

        # We need a context, and the create_context() method will detect and 
        # connect to the pygame window
        self.ctx = moderngl.create_context()
        ic(self.ctx.info["GL_RENDERER"])

        quad_buffer = self.ctx.buffer(data=array('f', [  # 'f' mean float
           -1.0, 1.0, 0.0, 0.0,  # top left vertex coords (-1.0, 1.0) and top left uv coords (0.0.)
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
        self.render_object = self.ctx.vertex_array(self.program, [(quad_buffer, '2f 2f', 'in_vert', 'in_texcoord')])  # format is 2 floats ('in_verts') and 2 floats ('in_texcoord') for the buffer
        # it's important that the names used for the buffer parts matches the in varaibles in the vertex shader
        ic('Shader compilation end')

        # Enable blending
        self.ctx.enable(moderngl.BLEND)
        # Set the blending function
        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)



        # TEST ZONE
        bg_surf = pg.image.load(
            "assets/backgrounds/Starfields/Starfield 3 - 1024x1024.png").convert()
        self.bg_tex = self.surf_to_texture(bg_surf)
        self.bg_tex.use(1)
        """
        --------------------------------------------------------------------------------
        """

        self.start_time = time.time()
        self.clock = pg.time.Clock()
        self.FPS = FPS
        self.states = states
        self.state_name = start_state
        self.state = self.states[self.state_name]
        self.font = pg.font.Font("freesansbold.ttf", 32)
        self.game_status = []  # to be passed between states

        self.fight_status = FightStatus(p1_ship="martian", ai_ship="plutonian")

    
    def surf_to_texture(self, surf) -> moderngl.Texture:
        '''
        Converts pygame texture to OpenGL texture and returns it
        '''
        tex = self.ctx.texture(surf.get_size(), 4)  # RGBA (4 component) f1 texture, as dype="f4" by default
        tex.filter = (moderngl.LINEAR, moderngl.LINEAR)  # how to convert pixels (NEAREST gives more of a pixel-art feel)
        tex.swizzle = 'BGRA'  # The swizzle mask change/reorder the vec4 value returned by the texture() function in a GLSL shaders
        # This is done to convert between pygame and OpenGL color formats
        
        # We first set up an OpenGL texture with ctx.texture(), we then set the filter function, reordered the channels 
        # and now we write an array version of our pygame surface to this OpenGl texture and return it
        tex.write(surf.get_view('1'))  # pygame: '1' returns a (surface-width * surface-height) array of continuous pixels
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
        self.state.draw(self.game_surface)  # call the update function in active state (on game_surface, not the screen)

        if settings.SHOW_FPS:
            fps_text = self.font.render(f"FPS: {self.clock.get_fps():.2f}", True, (255, 255, 0))
            self.game_surface.blit(fps_text, (10, 100))

        # -----------------------------------------------------------------------------------------------------------
        frame_tex = self.surf_to_texture(self.game_surface)
        frame_tex.use(0)  # Set use index 0
    

        self.program['bg_tex'] = 1

        #The location is the texture unit we want to bind the texture. 
        #This should correspond with the value of the sampler2D uniform 
        # in the shader because samplers read from the texture unit we assign to them
        self.program['u_tex'] = 0  #  Write to tex uniform the value 0, which is how the Sampler2D knows its input
        # texture comes from index 0
        self.render_object.render(mode=moderngl.TRIANGLE_STRIP)  # Triangle strip used to convert our quad_buffer
        # -----------------------------------------------------------------------------------------------------------

        pg.display.flip()  # We use flip() as we have set the pg.DOUBLEBUF flag in display.set_mode() earlier

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
