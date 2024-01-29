#version 330 core

uniform sampler2D u_tex;  // let's the shader sample value from the texture u_tex
uniform sampler2D u_bg_tex;
uniform sampler2D u_overlay_tex;

uniform float u_screenHeight;
uniform float u_screenWidth;

uniform float u_effect_x;
uniform float u_effect_y;

uniform int u_effect;   // which effect, if any, are we running?
uniform float u_time; // who long into the current effect are we?

uniform float u_zoom_lvl; // who long into the current effect are we?
uniform float u_zoom_x;
uniform float u_zoom_y;

// uniform inputs are the same for every instance
// in inputs depends on the instance (effectively different each pixel)

in vec2 uv;  // texture coordinates from vertex shader
out vec4 f_color;  // this is the final output - the color of the pixel


vec4 bg_effect(sampler2D bg_tex, vec2 uv_zoomed) {
    vec4 new_bg = texture(bg_tex, uv_zoomed);

    return new_bg;
}


void main() {
    vec2 effect_center = vec2(u_effect_x/u_screenWidth, u_effect_y/u_screenHeight);
    vec3 color;

    // scaleCenter is literally that, the center between the two ships, but we need top left
    vec2 scaleCenter = vec2(u_zoom_x/u_screenWidth, u_zoom_y/u_screenHeight);

    vec2 uv_z = (uv - scaleCenter) * (u_zoom_lvl / 3) + scaleCenter;  // offset uv gets zoomed 

    vec4 foreground = texture(u_tex,         uv_z);
    vec4 overlay    = texture(u_overlay_tex, uv  );  // we don't zoom the overlay
    vec4 foreground_mix = mix(foreground, overlay, overlay.a);  // overlay is added to foreground, with alpha

    //Any permanent background effects we want gets added here
    vec4 background = bg_effect(u_bg_tex, uv_z);
   
    f_color = mix(background, foreground_mix, foreground_mix.a);  // foreground is added to background, with alpha

    // 
    switch (u_effect) {

        /*
        Fade to black effect 
        */
        case 3:
            color = mix(texture(u_bg_tex, uv).rgb, texture(u_tex, uv).rgb, texture(u_tex, uv).a);  // blended textures

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
            color = mix(texture(u_bg_tex, uv).rgb, texture(u_tex, uv).rgb, texture(u_tex, uv).a);  // blended textures

            if (u_time < 50) {
                color.rgb = mix(color.rgb, vec3(0.0, 0.0, 0.0), 1.0 - u_time/50);
            } else {
                color.rgb = vec3(0.0, 0.0, 0.0);
            }
            f_color = vec4(color, 1.00);  
            break;
        
        /*
        Full-screen wobble
        */
        case 6:
            vec2 sample_pos = vec2(uv.x + sin(uv.y * 10 + u_time * 1.00) * 0.01, uv.y);
            f_color = mix(texture(u_bg_tex, sample_pos), texture(u_tex, sample_pos), texture(u_tex, sample_pos).a);  // blended textures
            break;

        /*
        Shockwave effect, needs effect coordinates - used for teleport
        */
        case 8:
        //uniform vec3 shockParams; // 10.0, 0.8, 0.1  // original 
        //vec3 shockParams = vec3(1.0, 0.4, 0.03); // very subtle
        vec3 shockParams = vec3(3.0, 0.4, 0.03); // hardcoded for now
        float time = u_time / 50;

        vec2 texCoord = uv;
        float distance = distance(uv, effect_center);
        if ( (distance <= (time + shockParams.z)) && 
            (distance >= (time - shockParams.z)) ) 
        {
            float diff = (distance - time); 
            float powDiff = 0.1 - pow(abs(diff*shockParams.x), 
                                        shockParams.y); 
            float diffTime = diff  * powDiff; 
            vec2 diffUV = normalize(uv - effect_center); 
            texCoord = uv + (diffUV * diffTime);
        } 

        // We apply the distortion both foreground and background textures
        f_color = mix(texture(u_bg_tex, texCoord), texture(u_tex, texCoord), texture(u_tex, texCoord).a);



        
        break;
       
    }                         
}
