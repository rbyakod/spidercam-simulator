// SpiderCAM Corner Motor Mount v1
// Mounts NEMA 17 at 45-degree corner of 20x20 aluminium extrusion frame

motor_w       = 42.3;
motor_h       = 42.3;
bolt_spacing  = 31.0;
motor_shaft_d = 5.5;
mount_t       = 4.0;
extrusion     = 20.0;
slot_w        = 6.1;
wall          = 3.0;

$fn = 32;

module nema17_holes() {
    cylinder(h = mount_t + 2, d = motor_shaft_d, center = true);
    for (x=[-1,1], y=[-1,1])
        translate([x*bolt_spacing/2, y*bolt_spacing/2, 0])
            cylinder(h = mount_t + 2, d = 3.2, center = true);
}

module extrusion_bracket() {
    difference() {
        cube([extrusion + wall*2, extrusion + wall*2, extrusion], center=true);
        translate([wall, wall, 0])
            cube([extrusion + 0.2, extrusion + 0.2, extrusion + 2], center=true);
        for (face=[0,1]) {
            rotate([0, 0, face*90])
                translate([0, (extrusion/2 + wall), 0])
                    cube([slot_w, wall + 2, extrusion*0.6], center=true);
        }
    }
}

module motor_mount_plate() {
    difference() {
        cube([motor_w + wall*2, motor_h + wall*2, mount_t], center=true);
        nema17_holes();
    }
}

union() {
    motor_mount_plate();
    translate([0, -(motor_h/2 + extrusion/2 + wall), -(extrusion/2 + mount_t/2)])
        extrusion_bracket();
}
