// SpiderPi Spool v1 - Direct mount to NEMA17 5mm shaft
// Target effective radius: ~11mm after line wrapping
// Designed for 0.8-1.0mm Dyneema braid

// Parameters
shaft_d = 5.0;         // NEMA17 shaft diameter (mm)
shaft_flat = 4.5;      // Shaft flat side (mm)
hub_d = 12.0;          // Hub outer diameter
hub_h = 8.0;           // Hub height
flange_d = 28.0;       // Flange outer diameter
flange_t = 2.5;        // Flange thickness
barrel_d = 18.0;       // Cable barrel diameter (sets effective radius ~9-11mm)
barrel_h = 14.0;       // Cable wrap height
line_anchor_d = 1.2;   // Cable anchor hole diameter
set_screw_d = 3.0;     // M3 set screw hole

module shaft_profile() {
    intersection() {
        circle(d = shaft_d);
        square([shaft_d, shaft_flat], center = true);
    }
}

module spool() {
    difference() {
        union() {
            // Bottom flange
            cylinder(d = flange_d, h = flange_t, $fn=64);
            // Barrel
            translate([0, 0, flange_t])
                cylinder(d = barrel_d, h = barrel_h, $fn=64);
            // Top flange
            translate([0, 0, flange_t + barrel_h])
                cylinder(d = flange_d, h = flange_t, $fn=64);
            // Hub
            cylinder(d = hub_d, h = hub_h, $fn=32);
        }
        // Shaft bore with flat
        linear_extrude(hub_h + 1)
            shaft_profile();
        // Set screw hole
        translate([hub_d/2, 0, hub_h/2])
            rotate([0, 90, 0])
                cylinder(d = set_screw_d, h = hub_d, $fn=16);
        // Line anchor hole
        translate([barrel_d/2 - 1, 0, flange_t + barrel_h/2])
            rotate([0, 90, 0])
                cylinder(d = line_anchor_d, h = 5, $fn=16);
    }
}

spool();
// Print in PETG or ABS for best results. PLA acceptable for light loads.
// After printing, measure actual barrel diameter to set spool_radius_m in config.
