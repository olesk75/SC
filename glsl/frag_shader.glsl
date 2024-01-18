#version 330 core

uniform sampler2D u_tex;  // let's the shader sample value from the texture u_tex
uniform sampler2D u_bg_tex;

uniform float u_screenHeight;
uniform float u_screenWidth;

uniform float u_effect_x;
uniform float u_effect_y;


uniform int u_effect;   // which effect, if any, are we running?
uniform float u_time; // who long into the current effect are we?

// uniform inputs are the same for every instance
// in inputs depends on the instance (effectively different each pixel)

in vec2 uvs;  // texture coordinates
out vec4 f_color;  // this is the final output - the color of the pixel

vec3 prandom3( vec2 co )
{
	vec3 a = fract( cos( co.x*8.3e-3 + co.y )*vec3(1.3e5, 4.7e5, 2.9e5) );
	vec3 b = fract( sin( co.x*0.3e-3 + co.y )*vec3(8.1e5, 1.0e5, 0.1e5) );
	vec3 c = mix(a, b, 0.5);
	return c;
}



void main() {
    // This is our current x and y pixel coordinate
    vec2 st = vec2(gl_FragCoord.x/u_screenWidth, gl_FragCoord.y/u_screenHeight);
    vec2 effect_center = vec2(u_effect_x/u_screenWidth, u_effect_y/u_screenHeight);
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

            
            // f_color *= 1. - 0.5 * pow(length(uvs), 3.);  // vignette effect
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
            // TODO:  the first texture must be foreground + background, and the second texture something else
            vec4 t0 = texture(u_bg_tex, uvs);
            vec4 t1 = texture(u_tex, uvs);
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
        /*
        Starfield of random stars - something is odd, possibly with the resolution 
        */
        case 7:
            vec2 resolution = vec2(1024, 1024);
            vec2 p = gl_FragCoord.xy / resolution.xy + u_time / 20.0;
            vec2 seed = p * 1.8;	
            
            seed = floor(seed * resolution);
            vec3 rnd = prandom3(seed);
            f_color = vec4(pow(rnd.y,40.0));
            break;

        /*
        Shockwave effect, needs effect coordinates
        */
        case 8:
        //uniform vec3 shockParams; // 10.0, 0.8, 0.1  // original 
        //vec3 shockParams = vec3(1.0, 0.4, 0.03); // very subtle
        vec3 shockParams = vec3(1.0, 0.4, 0.03); // hardcoded for now
        float time = u_time / 50;

        vec2 texCoord = uvs;
        float distance = distance(uvs, effect_center);
        if ( (distance <= (time + shockParams.z)) && 
            (distance >= (time - shockParams.z)) ) 
        {
            float diff = (distance - time); 
            float powDiff = 0.1 - pow(abs(diff*shockParams.x), 
                                        shockParams.y); 
            float diffTime = diff  * powDiff; 
            vec2 diffUV = normalize(uvs - effect_center); 
            texCoord = uvs + (diffUV * diffTime);
        } 


        // We apply the distortion both foreground and backgroudn textures
        if (texture(u_tex, uvs).rgb == vec3(0.0, 0.0, 0.0))  { 
                f_color = vec4(texture(u_bg_tex, texCoord).rgb, 1.0); 
            } else {
                f_color = vec4(texture(u_tex, texCoord).rgb, 1.0); 
            } 
        break;
    }                         
}


/*
We can also remap where the uv data is read from, so we can shake/move etc. the image.
vec_2 sample_pos = vec2 (uvs.x + sin(uvs.y * 10 + time * 0.01) *0.1, uv.y)  // this changes the x based on the y and time
f_color = vec4(texture(u_tex, sample_pos).rg, 1.0)

*/