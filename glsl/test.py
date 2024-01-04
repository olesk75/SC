import pygame
import moderngl
import numpy as np

# Pygame initialization
pygame.init()

# Pygame screen settings
screen_size = (800, 600)
screen = pygame.display.set_mode(screen_size, pygame.DOUBLEBUF | pygame.OPENGL)
pygame.display.set_caption("Pygame and ModernGL Integration")

# ModernGL context creation
ctx = moderngl.create_context()

# Vertex shader source
vertex_shader_source = """
#version 330

in vec2 in_vert;
in vec2 in_texcoord;

out vec2 uvs;

void main() {
    uvs = in_texcoord;
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
"""

# Fragment shader source
fragment_shader_source = """
#version 330

uniform sampler2D u_tex;
uniform float u_time;

in vec2 uvs;
out vec4 f_color;

void main() {
    // Check if the pixel is in the top-right corner
    vec3 color;
    if (uvs.x > 0.9 && uvs.y < 0.1) {
        // Add a small red square in the top-right corner
        color = vec3(1.0, 1.0, 0.0);
    } else {
        // Use the texture color for the rest of the screen
        color = texture(u_tex, uvs).rgb;
    }

    f_color = vec4(color, 1.0);
}
"""

# Shader programs
prog = ctx.program(vertex_shader=vertex_shader_source, fragment_shader=fragment_shader_source)

# Vertex buffer
vertices = np.array([-1.0, -1.0, 0.0, 0.0, 1.0, -1.0, 1.0, 0.0], dtype='f4')
vbo = ctx.buffer(vertices)
vao = ctx.simple_vertex_array(prog, vbo, 'in_vert', 'in_texcoord')

# Pygame surface
pygame_surface = pygame.Surface(screen_size)
pygame_surface.fill((255, 0, 0))  # Fill with red color for demonstration

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw the red square using ModernGL
    ctx.clear(1.0, 1.0, 1.0, 1.0)
    #prog.use()
    vao.render(moderngl.TRIANGLE_STRIP)

    # Alpha-blend the Pygame surface on top of the ModernGL rendering
    #screen.blit(pygame_surface.convert_alpha(), (0, 0))

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
