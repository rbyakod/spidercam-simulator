// SpiderPi Spool v1 - Uses 5mm shaft coupler
// Use when you have a 5mm-to-5mm rigid coupler
// This spool mounts to the output side of the coupler

coupler_d = 18.0;      // Outer diameter of coupler
coupler_bore = 5.0;    // Bore to fit coupler shaft or set screw side
flange_d = 30.0;
flange_t = 2.5;
barrel_d = 20.0;
barrel_h = 14.0;
hub_h = 10.0;

module spool_coupler() {
    difference() {
        union() {
            cylinder(d = flange_d, h = flange_t, $fn=64);
            translate([0,0,flange_t]) cylinder(d=barrel_d, h=barrel_h, $fn=64);
            translate([0,0,flange_t+barrel_h]) cylinder(d=flange_d, h=flange_t, $fn=64);
            cylinder(d=coupler_d, h=hub_h, $fn=32);
        }
        cylinder(d=coupler_bore, h=hub_h+1, $fn=32);
        // M3 set screw
        translate([coupler_d/2, 0, hub_h/2])
            rotate([0,90,0]) cylinder(d=3.0, h=coupler_d, $fn=16);
    }
}

spool_coupler();
