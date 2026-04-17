from math import cos, sin, pi

def lerp(a, b, t):
    return a + (b - a) * t

def line_path(p0, p1, steps=60):
    out = []
    for i in range(steps + 1):
        t = i / steps
        out.append({
            "x": lerp(p0["x"], p1["x"], t),
            "y": lerp(p0["y"], p1["y"], t),
            "z": lerp(p0["z"], p1["z"], t),
        })
    return out

def square_path(center, size=0.8, z=0.9, steps_per_edge=40):
    cx, cy = center["x"], center["y"]
    s = size / 2
    pts = [
        {"x": cx - s, "y": cy - s, "z": z},
        {"x": cx + s, "y": cy - s, "z": z},
        {"x": cx + s, "y": cy + s, "z": z},
        {"x": cx - s, "y": cy + s, "z": z},
        {"x": cx - s, "y": cy - s, "z": z},
    ]
    out = []
    for i in range(len(pts) - 1):
        seg = line_path(pts[i], pts[i + 1], steps_per_edge)
        out.extend(seg[:-1] if i < len(pts) - 2 else seg)
    return out

def circle_path(center, radius=0.45, z=0.9, steps=180):
    cx, cy = center["x"], center["y"]
    return [
        {"x": cx + radius * cos(2 * pi * i / steps), "y": cy + radius * sin(2 * pi * i / steps), "z": z}
        for i in range(steps + 1)
    ]
