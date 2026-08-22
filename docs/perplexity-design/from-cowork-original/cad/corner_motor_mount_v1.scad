// SpiderPi Corner Motor Mount v1
// Mounts NEMA17 to 2020 aluminum extrusion corner
// NEMA17 face: 42x42mm, M3 bolts on 31mm circle

nema17_w = 42.0;
nema17_bolt_circle = 31.0;
nema17_boss_d = 22.0;
nema17_boss_h = 2.0;
bolt_d = 3.2;           // M3 clearance
extrusion_w = 20.0;
plate_t = 4.0;
plate_w = 60.0;
plate_h = 60.0;
slot_w = 6.2;           // T-slot bolt head clearance
slot_offset = 10.0;     // T-nut center from edge

module nema17_face() {
    // Boss cutout
    circle(d = nema17_boss_d);
    // Bolt holes on 31mm circle
    for (a = [45, 135, 225, 315]) {
        rotate([0,0,a])
            translate([nema17_bolt_circle/2, 0])
                circle(d = bolt_d);
    }
}

module extrusion_slot() {
    square([slot_w, plate_t + 2], center = true);
}

module corner_mount() {
    difference() {
        // Main plate
        cube([plate_w, plate_h, plate_t]);
        // NEMA17 mounting pattern
        translate([plate_w/2, plate_h/2, -1])
            linear_extrude(plate_t + 2)
                nema17_face();
        // T-slot mounting holes for 2020 extrusion (X direction)
        translate([slot_offset, plate_h/2, plate_t/2])
            rotate([0,90,0])
                cylinder(d=bolt_d, h=plate_w, $fn=16);
        translate([plate_w - slot_offset, plate_h/2, plate_t/2])
            rotate([0,90,0])
                cylinder(d=bolt_d, h=plate_w, $fn=16);
    }
}

corner_mount();
// Print flat side down. Use M3x12 bolts for NEMA17, M5x8 T-nuts for extrusion.
