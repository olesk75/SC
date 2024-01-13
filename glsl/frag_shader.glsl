#version 330 core

uniform sampler2D u_tex;  // let's the shader sample value from the texture u_tex
uniform sampler2D u_bg_tex;
  
uniform int u_effect;   // which effect, if any, are we running?
uniform float u_time; // who long into the current effect are we? 


// uniform inputs are the same for every instance
// in inputs depends on the instance (effectively different each pixel)

in vec2 uvs;  // texture coordinates
out vec4 f_color;  // this is the final output - the color of the pixel


// THIS CODE IS FOR A SHOCKWAVE EFFECT AT vec2 center
// uniform vec2 center; // Mouse position
// uniform vec3 shockParams; // 10.0, 0.8, 0.1


void main() {
    vec2 st = gl_FragCoord.xy/1000;
    vec3 color;

    vec4 t0;
    vec4 t1;


    switch (u_effect) {
        case 0: 
            // NO effect
            f_color = vec4(texture(u_tex, uvs).rgb + texture(u_bg_tex, uvs).rgb, 1.0);
            
            break;
        case 1:
            // Test effect - red screen 
            // Check if the pixel is in the bottom-right corner
            if (st.x > 0.1 && st.y < 0.9) {
            // Add a small red square in the top-right corner
            //color = vec3(1.0, 0.0, 0.0);
            color = texture(u_tex, uvs).rgb + texture(u_bg_tex, uvs).rgb;  // we add a color overlay
            } else {
            // Use the texture color for the rest of the screen
            color = texture(u_tex, uvs + u_time).rgb;
            }
            f_color = vec4(color, 1.0);     // here the last figure _is_ transparency
            break;
        case 2:

            vec3 shockParams = vec3(10.0, 0.8, 0.1);
            vec2 center = vec2(0.5, 0.5);

            vec2 texCoord = uvs;
            float distance = distance(uvs, center);
            if ( (distance <= (u_time + shockParams.z)) && 
                (distance >= (u_time - shockParams.z)) ) 
            {
                float diff = (distance - u_time); 
                float powDiff = 1.0 - pow(abs(diff*shockParams.x), 
                                            shockParams.y); 
                float diffTime = diff  * powDiff; 
                vec2 diffUV = normalize(uvs - center); 
                texCoord = uvs + (diffUV * diffTime);
            } 
            f_color = texture(u_bg_tex, texCoord);
}
        
    
                                    
    
}


/*
We can also remap where the uv data is read from, so we can shake/move etc. the image.
vec_2 sample_pos = vec2 (uvs.x + sin(uvs.y * 10 + time * 0.01) *0.1, uv.y)  // this changes the x based on the y and time
f_color = vec4(texture(u_tex, sample_pos).rg, 1.0)

*/