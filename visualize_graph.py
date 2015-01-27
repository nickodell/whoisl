#!/usr/bin/python
from record import recordtype
from PIL import Image, ImageDraw
import random
from sys import argv
XRES = 400
YRES = 400
STEPS = int(argv[1])
PERSTEP = 0.005
random.seed(41)
Point = recordtype("Point", "x y name")
connections = eval(open("graph.txt").read())
p_transform = lambda x, y: (x * XRES * 0.95 + XRES * 0.025, y * YRES * 0.95 + YRES * 0.025)
bounds = lambda x, a, b: min(max(x, a), b)

# If there is a p1->p2 relationship, but not the other way around, copy it
# Otherwise set the weight to 0.
for tag1 in connections.keys():
    to_edit = connections[tag1]
    for tag2 in connections.keys():
        if tag1 == tag2:
            # p1 has no relationship with p1
            continue
        if tag2 in to_edit.keys():
            # relationship already exists here
            continue
        if tag1 not in connections[tag2].keys():
            # Neither references the other, set ours to 0
            to_edit[tag2] = 0
        else:
            # We don't have a relationship with them, but they have a relationship with us
            # Copy it.
            to_edit[tag2] = connections[tag2][tag1]
    connections[tag1] = to_edit

#print connections



# Initially set points to random positions between 0 and 1
points = map(lambda name: Point(random.random(), random.random(), name), connections.keys())
n = 0
while n < STEPS:
    for point in points:
        x1, y1, name = point
        # Move away from all points, but move closer to friends.
        for otherpoint in points:
            if point == otherpoint: continue
            x2, y2, _ = otherpoint
            connect_str = connections[point.name][otherpoint.name]
            offsetx = x2 - x1
            offsety = y2 - y1
            # Move towards, linearly
            x1 += offsetx * connect_str * PERSTEP * 3
            y1 += offsety * connect_str * PERSTEP * 3
            # Move away, fall off with distance
            offsetx_sq = offsetx ** 2 or 1e10
            offsety_sq = offsety ** 2 or 1e10
            x1 += -offsetx * PERSTEP / offsetx_sq
            x1 += -offsety * PERSTEP / offsety_sq

        # Keep it in bounds
        x1 = bounds(x1, 0, 1)
        y1 = bounds(y1, 0, 1)
        # Also move slightly towards the center
        #offsetx = 0.5 - x1
        #offsety = 0.5 - y1
        #x1 += offsetx * PERSTEP * 50
        #y1 += offsety * PERSTEP * 50
        point.x, point.y = x1, y1
    n += 1

# Render graph
im = Image.new("RGB", (XRES, YRES), "white")
draw = ImageDraw.Draw(im)
already_drawn = set()
for point in points:
    x1, y1, name = point
    for connect_name, connect_str in connections[name].items():
        if connect_str == 0:
            # Don't draw 0-strength connections
            continue
        if (name, connect_name) in already_drawn or \
           (connect_name, name) in already_drawn:
            # We've drawn this already
            continue
        x2, y2, _ = filter(lambda point: point.name == connect_name, points)[0]
        #x2, y2, _ = other_point.x, other_point.y
        draw.line(p_transform(x1, y1) + p_transform(x2, y2), fill=(0,0,0))
        already_drawn.add((name, connect_name))
im.save("graph.jpg", quality=90)
