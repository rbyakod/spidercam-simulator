// SpiderCAM Spool - With Coupler Hub
// For motors with 5mm shaft connecting to 8mm lead-screw coupler

shaft_d   = 5.0;
coupler_d = 8.0;
hub_d     = 24.0;
hub_h     = 14.0;
flange_d  = 60.0;
flange_t  = 3.0;
barrel_d  = 40.0;
barrel_h  = 20.0;
n_grooves = 12;
cable_r   = 1.2;

$fn = 64;

module coupler_hole() {
    cylinder(h = 8, d = shaft_d);
    translate([-shaft_d/2 + 0.5, 0, 0])
        cube([shaft_d, shaft_d, 8], center = false);
    translate([0, 0, 8])
        cylinder(h = hub_h - 8, d = coupler_d);
}

module coupler_spool() {
    difference() {
        union() {
            cylinder(h = flange_t, d = flange_d);
            translate([0,0,flange_t]) cylinder(h = barrel_h, d = barrel_d);
            translate([0,0,flange_t+barrel_h]) cylinder(h = flange_t, d = flange_d);
            cylinder(h = hub_h + flange_t, d = hub_d);
        }
        translate([0,0,-1]) coupler_hole();
        for (i=[0:n_grooves-1]) {
            z = flange_t + (barrel_h/n_grooves)*(i+0.5);
            rotate_extrude()
                translate([barrel_d/2, z, 0])
                    circle(r=cable_r);
        }
    }
}

coupler_spool();
