#version 330 core

uniform sampler2D u_tex;  // let's the shader sample value from the texture u_tex
uniform sampler2D u_bg_tex;
  
uniform int u_effect;   // which effect, if any, are we running?
uniform float u_time; // who long into the current effect are we? 

// uniform inputs are the same for every instance
// in inputs depends on the instance (effectively different each pixel)

in vec2 uvs;  // texture coordinates
out vec4 f_color;  // this is the final output - the color of the pixel


void main() {
    vec2 st = gl_FragCoord.xy/1000;
    vec3 color;

    switch (u_effect) {
        case 0: 
            // NO effect - foreground texture overwrites background texture (default)

            // We check if the foreground surface has a black pixel, in which case we
            // only show the background, otherwise we show the foreground
            if (texture(u_tex, uvs).rgb == vec3(0.0, 0.0, 0.0))  { 
                f_color = vec4(texture(u_bg_tex, uvs).rgb, 1.0); 
            } else {
                f_color = vec4(texture(u_tex, uvs).rgb, 1.0); 
            } 
            break;
        /*
        Test effect - shows red frame
        */
        case 1:
            // Test effect - red screen 
            // Check if the pixel is in the bottom-right corner
            if (st.x > 0.1 && st.y < 0.9) {
            // Add a small red square in the top-right corner
            //color = vec3(1.0, 0.0, 0.0);
            color = texture(u_tex, uvs).rgb + texture(u_bg_tex, uvs).rgb;  
            } else {
            // Use the texture color for the rest of the screen
            //color = texture(u_tex, uvs + u_time).rgb;
            color = vec3(1.0, 0.0, 0.0);
            }
            f_color = vec4(color, 1.0);     // here the last figure _is_ transparency
            break;

        /*
        Zoom effect - WIP!
        */
        case 2:
            vec2 uv = gl_FragCoord.xy; // / iResolution.xy;  // unsure if this is correct or not
            float zoom = (0.1 + 0.5 * sin(u_time));  // 0.5 on both
            vec2 scaleCenter = vec2(0.7);
            uv = (uv - scaleCenter) * zoom + scaleCenter;
            
            vec4 texel = texture(u_tex, uv);
            f_color = texel;
            break;

        /*
        Fade to black effect 
        */
        case 3:
            if (texture(u_tex, uvs).rgb == vec3(0.0, 0.0, 0.0))  { 
                color = vec3(texture(u_bg_tex, uvs).rgb); 
            } else {
                color = vec3(texture(u_tex, uvs).rgb); 
            }

            if (u_time < 50) {
                color.rgb = mix(color.rgb, vec3(0.0, 0.0, 0.0), u_time/50);
            } else {
                color.rgb = vec3(0.0, 0.0, 0.0);
            }
            f_color = vec4(color, 1.00);  
            break;

        /*
        Fade in from black effect 
        */
        case 4:
            if (texture(u_tex, uvs).rgb == vec3(0.0, 0.0, 0.0))  { 
                color = vec3(texture(u_bg_tex, uvs).rgb); 
            } else {
                color = vec3(texture(u_tex, uvs).rgb); 
            }

            if (u_time < 50) {
                color.rgb = mix(color.rgb, vec3(0.0, 0.0, 0.0), 1.0 - u_time/50);
            } else {
                color.rgb = vec3(0.0, 0.0, 0.0);
            }
            f_color = vec4(color, 1.00);  
            break;
        
        /*
        Swipe from left to right between two textures
        */
        case 5:
            vec4 t0 = texture2D(u_bg_tex, uvs);
            vec4 t1 = texture2D(u_tex, uvs);
            f_color = mix(t0, t1, step(u_time * 0.5, uvs.x));  // the multiplier for time needs to be tested
            break;
        /*
        Short wobble, used for teleports
        */
        case 6:
            vec2 sample_pos = vec2(uvs.x + sin(uvs.y * 10 + u_time * 1.00) * 0.01, uvs.y);
            //f_color = vec4(texture(tex, sample_pos).rg, texture(tex, sample_pos).b * 1.5, 1.0);
            if (texture(u_tex, uvs).rgb == vec3(0.0, 0.0, 0.0))  { 
                f_color = vec4(texture(u_bg_tex, sample_pos).rgb, 1.0); 
            } else {
                f_color = vec4(texture(u_tex, sample_pos).rgb, 1.0); 
            }
              
            break;

}
        
    
                                    
    
}


/*
We can also remap where the uv data is read from, so we can shake/move etc. the image.
vec_2 sample_pos = vec2 (uvs.x + sin(uvs.y * 10 + time * 0.01) *0.1, uv.y)  // this changes the x based on the y and time
f_color = vec4(texture(u_tex, sample_pos).rg, 1.0)

*/