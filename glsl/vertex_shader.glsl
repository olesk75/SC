#version 330 core

in vec2 in_vert;            // vertex coordinates, tuple of floats, from the quad_buffer
in vec2 in_texcoord;        // uv coordinates, from the quad_buffer

out vec2 uv;               // output uv coords (vert shader has vertex coords sorted already)
                            // so we only need to output the uv vector

void main() {
    uv = in_texcoord;      // simple pass-through
    gl_Position = vec4(in_vert.x, in_vert.y, 0.0, 1.0);  // vertex coordinates (in_vert.x and in_vert.y), z=0.0
    // 1.0 in the end is required (but not alpha, it's the "homogenous coordinate")
}