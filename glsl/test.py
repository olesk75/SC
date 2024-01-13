import pygame
import moderngl
import numpy as np

# Pygame initialization
pygame.init()

# Pygame screen settings
screen_size = (800, 600)
screen = pygame.display.set_mode(screen_size, pygame.DOUBLEBUF | pygame.OPENGL)
pygame.display.set_caption("Pygame and ModernGL - Passing Variables to Fragment Shader")

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

uniform float u_time;  // Example of a uniform variable

in vec2 uvs;
out vec4 f_color;

void main() {
    // Use the uniform variable in the fragment shader
    float red_component = sin(u_time);
    f_color = vec4(red_component, uvs.y, 1.0, 1.0);
}
"""

# Shader programs
prog = ctx.program(vertex_shader=vertex_shader_source, fragment_shader=fragment_shader_source)

# Vertex buffer
vertices = np.array([-1.0, -1.0, 0.0, 0.0, 1.0, -1.0, 1.0, 0.0], dtype='f4')
vbo = ctx.buffer(vertices)
vao = ctx.simple_vertex_array(prog, vbo, 'in_vert', 'in_texcoord')

# Main loop
running = True
clock = pygame.time.Clock()
time = 0.0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the uniform variable (e.g., time)
    time += 0.01
    prog['u_time'].value = time

    # Draw using ModernGL
    ctx.clear(1.0, 1.0, 1.0, 1.0)
    prog.use()
    vao.render(moderngl.TRIANGLE_STRIP)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
