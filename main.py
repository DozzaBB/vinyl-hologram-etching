import matplotlib.pyplot as plt
from math import sin, radians, cos, degrees
from random import random
import json

import matplotlib.animation as animation
import numpy as np

fig, ax = plt.subplots()
plt.gca().set_aspect('equal')

SCALE_SCENE = 10
DISC_RADIUS = 100
CAM_OFFSET = 50 # Pretty sure this can only be done vertically.
REPORT_NAME = "report.json"
FPS = 60
DRAW_DEBUG_CIRCLES = 1
DEBUG_DEROTATE = 0
SHOW_BOTTOM = 0

def cart2pol(p):
    (x,y,z) = p
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi, z)

def rotate(point, theta):
    [x1, y1] = point
    x2 = x1*cos(theta) - y1*sin(theta)
    y2 = y1*cos(theta) + x1*sin(theta)
    return [x2,y2]
 
def scale_point(somepoint):
    [x,y,z] = somepoint["pos"]
    somepoint["pos"] = [x*SCALE_SCENE,y*SCALE_SCENE,z*SCALE_SCENE]

def collect_visible(point):
    og = point["visibleangles"]
    new = []
    started = False
    d = {}
    for i in range(361):

        if ((i+1)%360 in og) and not started:
            started = True
            d = {
                "start": i+1
            }
            new.append(d)
        if ((i+1)%360 not in og) and started:
            started = False
            d["stop"] = i-1
        if ((i+1)%360 not in og) and not started:
            #nothing interesting here
            pass
        if ((i+1)%360 in og) and not started:
            #nothing interesting here
            pass
        if i == 360 and "stop" not in d:
                d["stop"] = 360
    point["visiblechunks"] = new

def polar2holo(polar):
    """return hologram coordinates in r, cx, cy"""
    (r, theta, z) = polar
    return (z+CAM_OFFSET, r*cos(theta), r*sin(theta)) # z*2 because 30 degree camera angle

def circle_from(point, occlusions):
    def circle_maker(time, bottom=False):
        deg = round(degrees(time))
        if (-(deg+180))%360 in occlusions:
            return [0,0]
        (holor, holocx, holocy) = polar2holo(point)
        offset = 3.14159 if bottom else 0
        newx = holor*sin(time+offset) + holocx 
        newy = holor*cos(time+offset) + holocy 

        # rotate by -time
        if DEBUG_DEROTATE: [newx,newy] = rotate([newx, newy],time)

        return [newx,newy]
    return circle_maker

def update(framenum):

    theta_deg = framenum * 360/FPS
    rad = radians(theta_deg)
    dat = []

    for maker in makers:
        dat.append(maker(rad))
        if SHOW_BOTTOM: dat.append(maker(rad, True))


    # print(theta_deg)
    scat.set_offsets(dat)
    return scat

def plot_circle_at(p, rad, centre):
    x,y = [centre[0]+rad*sin(radians(t)) for t in range(360)], [centre[1]+rad*cos(radians(t)) for t in range(360)]
    p.plot(x,y)
    return

scat = ax.scatter([-DISC_RADIUS,DISC_RADIUS],[-DISC_RADIUS,DISC_RADIUS],marker='.') # this just forces the graph scale to contain all our data
makers = []

report = json.load(open(f"../{REPORT_NAME}"))


for p in report:
    scale_point(p)
    collect_visible(p)

for point in report:
    polar = cart2pol(point['pos'])
    pr,px,py = polar2holo(polar)
    makers.append(circle_from(polar, point['occlusions']))
    if DRAW_DEBUG_CIRCLES: plot_circle_at(ax, pr,(px,py))


plot_circle_at(ax, DISC_RADIUS, [0,0])

ani = animation.FuncAnimation(fig=fig, func=update, frames=FPS+1, interval=100/FPS)
# plt.show()

PAD = 10

# Make an SVG
def make_svg(ps):
    circle_text = ""
    circle_text += f'<svg viewBox="0 0 {(DISC_RADIUS+PAD)*2} {(DISC_RADIUS+PAD)*2}" xmlns="http://www.w3.org/2000/svg">'
    # make it actually show everything
    circle_text += f'<g transform="translate(0,{DISC_RADIUS+PAD})">\n'
    # Disc centre
    circle_text += f'<circle fill="none" stroke="green" stroke-width="0.5px" cx="0" cy="0" r="{DISC_RADIUS}" />\n'
    circle_text += f'<circle fill="none" stroke="green" stroke-width="0.5px"  cx="0" cy="0" r="1" />\n'
    # Vertices
    for p in ps:
        (cr, cx, cy) = polar2holo(cart2pol(p['pos']))
        # circle_text += f'<circle fill="None" stroke="red" cx="{cx}" cy="{cy}" r="{cr}" />\n'


        for d in p["visiblechunks"]:
            print(f"Need arc from {d['start']} to {d['stop']}")
            start = radians(d['start'])
            stop = radians(d['stop'])
            big = 1 if ((d['stop'] - d['start']) >= 180) else 0 # make it always sweep in the correct direction
            x1, y1 = cx + cr*sin(start), cy+ cr*cos(start)
            x2, y2 = cx + cr*sin(stop), cy + cr*cos(stop)
            
            circle_text += f'<path fill="none" stroke="green" stroke-width="0.5px" d="M {x1} {y1} A {cr} {cr} 0 {big} 0 {x2} {y2}" />'


    # Close everything up.
    circle_text += '</g>'
    circle_text += '</svg>'
    with open("test.svg", "w") as f:
        f.write(circle_text)


make_svg(report)


plt.show()



