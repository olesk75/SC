#version 330 core


/* Main vertex shader

Input variables in vertex shaders are called attributes 
Output values are called varyings

The output values all end up in the buffer

ASSUMTIONS: we keep this one pretty much constant and do all our effects in the fragment shader(s)
as we're doing a 2D project across two static triangles.

*/



// describing our inputs, using bec2 datatypes (mutable unlike tuples)
in vec2 in_vert;            // vertex coordinates
in vec2 in_texcoord;        // uv coordinates

out vec2 uvs;               // output uv coords (vert shader has vertex coords sorted already)

void main() {
    uvs = in_texcoord;      // simple pass-through
    gl_Position = vec4(in_vert, 0.0, 1.0);  // vertex coordinates (in_vert.x and in_vert.y), z=0.0

}