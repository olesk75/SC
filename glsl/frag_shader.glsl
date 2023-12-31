#version 330 core

/* Main fragment shader


*/


// Uniforms are read-only for all threads
uniform sampler2D u_tex;    // different type of input, same for _all_ parallel processes, samples texture values
uniform float u_time;       // placeholder until I can find a use for it

in vec2 uvs;
out vec4 f_color;


// Plot a line on Y using a value between 0.0-1.0
float plot(vec2 st) {    
    return smoothstep(0.02, 0.0, abs(st.y - st.x));
}

void main() {
	vec2 st = gl_FragCoord.xy/100000;

    float y = st.x;

    vec3 color = vec3(y);

    // Plot a line
    float pct = plot(st);
    color = (1.0-pct)*color+pct*vec3(0.0,1.0,0.0);

	//gl_FragColor = vec4(color,1.0);
    f_color = vec4(texture(u_tex, uvs).rgb, 1.0);  // 1.0 is transparency
}

/*
void main(){
    f_color = vec4(texture(u_tex, uvs).rgb, 1.0);  // 1.0 is transparency
}
*/