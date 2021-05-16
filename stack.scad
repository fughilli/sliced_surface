for(i=[0:16]) {
    translate([0,0,25.4 * 1.5 * i])
linear_extrude(height=25.4 * 0.75, center=true)
import(file=str("outputs/slice_",i,".dxf"));
}

h=(25.4 * (1.5*17));
for(i=[0:3]) {
    x = 2 * 25.4 + (44  *25.4 / 3) * i;
translate([x,25.4,h/2 - 0.75*25.4])
cylinder(h=h+(0.5*25.4),r=(0.75*25.4/2), center=true);
}

translate([25.4*24,-25.4/4,h - 25.4])
rotate([-90,-90,-90])
linear_extrude(height=25.4*48,center=true)
scale([25.4*2,25.4*2,25.4*2])
polygon([[0,0],[-1,0],[-1,0.1],[0.1,0.1],[0.1,-1],[0,-1]]);
