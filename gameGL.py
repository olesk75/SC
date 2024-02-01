import moderngl
from array import array
import time
import os
import pygame as pg
from pathlib import Path
from icecream import ic


class GameGL:
    """
    Class which mostly calls the same methods for whatever state is currently active,
    including GAMEPLAY.

    It also handles the ModernGL integration

    The run() method is looping until the game exits
    """

    def __init__(self, states, start_state, config) -> None:
        self.config = config
        self.done = False
        self.previous_effect = 0
        self.effect_counter = 0
        self.start_time = 0
        self.clock = pg.time.Clock()
        self.states = states
        self.state_name = start_state
        self.state = self.states[self.state_name]
        self.font = pg.font.Font("freesansbold.ttf", 32)

        self.fight_status = None  # only gets defined in the menu


        # Resolution and screen setup
        current_screen = pg.display.Info()
        monitor_res = (current_screen.current_w, current_screen.current_h)

        ic("Screen resolution", monitor_res)
        window_size_xy = int(min(monitor_res) * 0.9)  # window will be square and 90% of shortest screen dimension (for window borders etc.)
        self.config.window_size_xy = window_size_xy  # this allows main to access this for the config instance

        # DEBUG OVERRIDE FOR PERF TESTING
        #self.config.window_size_xy = 800

        # Tons of stuff to prevent Macs from freaking out
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)
        os.environ["SDL_VIDEO_WINDOW_POS"] = "%d,%d" % (10, 10)  # We place scaled window top left

        # flags = pg.FULLSCREEN | pg.HWSURFACE | pg.SCALED
        self.screen = pg.display.set_mode((self.config.window_size_xy, self.config.window_size_xy), pg.OPENGL | pg.DOUBLEBUF)
        self.game_surface = pg.Surface((self.config.window_size_xy, self.config.window_size_xy), pg.SRCALPHA)
        self.game_overlay = pg.Surface((self.config.window_size_xy, self.config.window_size_xy), pg.SRCALPHA)


        """
        --------------------------------------------------------------------------------
        ModernGL 
        --------------------------------------------------------------------------------
        """

        # We need a context, and the create_context() method will detect and
        # connect to the pygame window
        self.ctx = moderngl.create_context()
        ic(self.ctx.info["GL_RENDERER"])

        quad_buffer = self.ctx.buffer(
            data=array(
                "f",
                [  # 'f' mean float
                    -1.0, 1.0, 0.0, 0.0, # top left vertex coords (-1.0, 1.0) and top left uv coords (0.0.)
                    1.0, 1.0, 1.0, 0.0,  # top right
                    -1.0,-1.0, 0.0,1.0,  # bottom left
                    1.0, -1.0, 1.0, 1.0, # bottom right
                ],
            )
        )

        glsl_folder = Path("glsl/")

        with open(glsl_folder / "vertex_shader.glsl", "r") as file:
            vert_shader = file.read()

        # Runs for every pixel in the vertices defined in the vertex shader
        with open(glsl_folder / "frag_shader.glsl", "r") as file:
            frag_shader = file.read()

        self.program = self.ctx.program(vert_shader, frag_shader)  # compiles GLSL code

        # format is 2 floats ('in_verts') and 2 floats ('in_texcoord') for the buffer
        self.render_object = self.ctx.vertex_array(self.program, [(quad_buffer, "2f 2f", "in_vert", "in_texcoord")])

        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)

        # Initial values
        self.program["u_effect"] = 1
        self.program["u_time"] = time.time()
        self.program["u_screenWidth"] = self.config.window_size_xy
        self.program["u_screenHeight"] = self.config.window_size_xy

        # Image background loaded as completely separate texture (same size as game texture)
        # bg_surf = pg.image.load("assets/backgrounds/Starfields/Starfield 3 - 1024x1024.png").convert_alpha()
        bg_surf = pg.image.load("assets/backgrounds/Blue Nebula/Blue Nebula 8 - 1024x1024.png").convert_alpha()
        bg_surf = pg.transform.scale(bg_surf, (self.config.window_size_xy, self.config.window_size_xy))
        self.bg_tex = self.surf_to_texture(bg_surf)
        self.bg_tex.use(0)
        """
        --------------------------------------------------------------------------------
        """



    def surf_to_texture(self, surf) -> moderngl.Texture:
        """
        Converts pygame texture to OpenGL texture and returns it
        """
        tex = self.ctx.texture(
            surf.get_size(), 4)  # RGBA (4 component) f1 texture, as dype="f4" by default
        tex.filter = (
            moderngl.LINEAR,
            moderngl.LINEAR,
        )  # how to convert pixels (NEAREST gives more of a pixel-art feel)

        # The swizzle mask change/reorder the vec4 value returned by the texture() function in a GLSL shaders
        tex.swizzle = "BGRA"
        # This is done to convert between pygame and OpenGL color formats

        # pygame: '1' returns a (surface-width * surface-height) array of continuous pixels
        tex.write(surf.get_view("1"))
        return tex

    def event_loop(self) -> None:
        for event in pg.event.get():
            if self.state_name == "MENU":
                self.fight_status = self.state.get_event(event)
            else: 
                self.state.get_event(event)

    def flip_state(self) -> None:
        current_state = self.state_name
        self.state.done = False
        next_state = self.state.next_state
        ic("State transition:", current_state, next_state)
        self.state_name = next_state
        self.state = self.states[self.state_name]
        self.state.startup(self.fight_status, self.config)

    def update(self) -> None:
        if self.state.quit:
            self.done = True
            ic("Player terminated game")
        elif self.state.done:
            self.flip_state()
        self.state.update(self.fight_status, self.config)  # call the update function in active state - this is always inherited from the base class

        if self.previous_effect != self.state.active_effect:
            self.previous_effect = self.state.active_effect
            self.effect_counter = 0

    def draw(self) -> None:
        # we erase the game surfaces so we start with a clean transparent canvas each iteration
        self.game_surface.fill((0, 0, 0, 0))
        self.game_overlay.fill((0, 0, 0, 0))

        # call the update function in active state (on game_surface, not the screen)
        self.state.draw(self.game_surface, self.game_overlay)

        if self.config.SHOW_FPS:
            fps_text = self.font.render(
                f"FPS: {self.clock.get_fps():.2f}", True, (255, 255, 0))
            self.game_overlay.blit(fps_text, (10, 100))

        # -----------------------------------------------------------------------------------------------------------
        frame_tex = self.surf_to_texture(self.game_surface)
        frame_tex.use(1)  # Set use index 1
        frame_tex = self.surf_to_texture(self.game_overlay)
        frame_tex.use(2)  # Set use index 2

        # The location is the texture unit we want to bind the texture.
        # This should correspond with the value of the sampler2D uniform
        # in the shader because samplers read from the texture unit we assign to them

        # Write to tex uniform the value 0, which is how the Sampler2D knows its input
        self.program["u_bg_tex"] = 0
        self.program["u_tex"] = 1
        self.program["u_overlay_tex"] = 2

        self.program["u_effect"] = self.state.active_effect
        self.program["u_effect_x"], self.program["u_effect_y"] = self.state.effect_coords

        self.program["u_time"] = self.effect_counter
        
        self.program["u_zoom_lvl"] = float(self.state.zoom)
        self.program["u_zoom_x"] = self.state.zoom_x
        self.program["u_zoom_y"] = self.state.zoom_y

        self.ctx.enable(moderngl.BLEND)  # Enable blending for transparency
        self.render_object.render(mode=moderngl.TRIANGLE_STRIP)  # Triangle strip used to convert our quad_buffer
        # -----------------------------------------------------------------------------------------------------------

        # We use flip() as we have set the pg.DOUBLEBUF flag in display.set_mode() earlier
        pg.display.flip()

        frame_tex.release()  # free up VRAM - required!

        self.effect_counter += 1  # increases 60 per second
        self.clock.tick(self.config.FPS)

    """ 
    This is the main game loop
    """

    def run(self) -> None:
        while not self.done:
            self.clock.tick(self.config.FPS)
            self.event_loop()
            self.update()
            self.draw()
