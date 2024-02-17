#version 460 core

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform sampler2D texture;
uniform float zScale;
uniform float dx;
uniform float origx;
uniform float origy;

void main() {

    float halfdx = dx/2.0;

    vec2 texCoord = (gl_in[0].gl_Position.xy - vec2(origx, origy)) / dx + 0.5;

    float zValue = texture(texture, texCoord).r * zScale;

    gl_Position = vec4(gl_in[0].gl_Position.x - halfdx, gl_in[0].gl_Position.y - halfdx, zValue, 1.0);
    EmitVertex();

    gl_Position = vec4(gl_in[0].gl_Position.x + halfdx, gl_in[0].gl_Position.y - halfdx, zValue, 1.0);
    EmitVertex();

    gl_Position = vec4(gl_in[0].gl_Position.x + halfdx, gl_in[0].gl_Position.y + halfdx, zValue, 1.0);
    EmitVertex();

    gl_Position = vec4(gl_in[0].gl_Position.x - halfdx, gl_in[0].gl_Position.y + halfdx, zValue, 1.0);
    EmitVertex();

    EndPrimitive();
}
