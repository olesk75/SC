#version 330 core

uniform sampler2D u_tex;  // let's the shader sample value from the texture u_tex
uniform sampler2D bg_tex;
uniform float u_time;

// uniform inputs are the same for every instance
// in inputs depends on the instance (effectively different each pixel)

in vec2 uvs;  // texture coordinates
out vec4 f_color;  // this is the final output - the color of the pixel

void main() {
    vec2 st = gl_FragCoord.xy/1000;

    vec3 color;

    // Check if the pixel is in the bottom-right corner
    if (st.x > 0.5 && st.y < 0.5) {
        // Add a small red square in the top-right corner
        //color = vec3(1.0, 0.0, 0.0);
        color = texture(u_tex, uvs).rgb + texture(bg_tex, uvs).rgb;  // we add a color overlay
    } else {
        // Use the texture color for the rest of the screen
        color = texture(u_tex, uvs).rgb;
    }

    f_color = vec4(color, 1.0);     // here the last figure _is_ transparency
                                    
    
}
 