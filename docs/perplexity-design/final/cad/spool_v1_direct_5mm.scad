// SpiderCAM Spool - Direct Drive, 5mm D-shaft
// Print at 0.2mm layer, 40% infill, PETG or ABS

shaft_d      = 5.0;
flat_depth   = 0.5;
hub_d        = 20.0;
hub_h        = 10.0;
flange_d     = 60.0;
flange_t     = 3.0;
barrel_d     = 40.0;
barrel_h     = 20.0;
cable_groove = 1.2;
n_grooves    = 12;

$fn = 64;

module d_shaft_hole() {
    cylinder(h = hub_h + 2, d = shaft_d, center = true);
    translate([-shaft_d/2 + flat_depth, 0, 0])
        cube([shaft_d, shaft_d, hub_h + 2], center = true);
}

module spool() {
    difference() {
        union() {
            cylinder(h = flange_t, d = flange_d);
            translate([0, 0, flange_t])
                cylinder(h = barrel_h, d = barrel_d);
            translate([0, 0, flange_t + barrel_h])
                cylinder(h = flange_t, d = flange_d);
            translate([0, 0, -hub_h])
                cylinder(h = hub_h + flange_t, d = hub_d);
        }
        translate([0, 0, -hub_h - 1]) d_shaft_hole();
        for (i = [0 : n_grooves - 1]) {
            z = flange_t + (barrel_h / n_grooves) * (i + 0.5);
            rotate_extrude()
                translate([barrel_d/2, z, 0])
                    circle(r = cable_groove);
        }
    }
}

spool();
