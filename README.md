# vinyl-hologram-etching

This project is an attempt at writing a somewhat automated workflow for creating scratch holograms for circular media. (Inspiration: https://www.youtube.com/watch?v=aEbAaL7fPl4 and https://www.youtube.com/watch?v=sv-38lwV6vc)

The workflow is:

1. Import some model into `occlusion.blend` using Blender. The origin must be centred on the origin, and preferably about the same size as the reference model already in there.
2. The camera is already positioned, but if your model is very very large, you will need to move the camera further away. This is because the camera is used to detect which vertices are occluded at any angle. Ideally the camera would be infinitely far away since this model uses orthogonal projection, but I got lazy here.
3. Run the script inside the blender file using the blender scripting tab. This should produce `report.json` which contains the vertex data in world space, and which angles each vertex is visible to the camera at (informing which sections of the radial hologram etch are present)
4. Run `main.py` to produce an SVG of the etched hologram as well as a nice little maltplotlib debug visualisation.

5. using the software of your choice, convert the SVG into a tool path for some plotter or etching machine. I used an Ender 3 and the inkscape laser tool from here: https://jtechphotonics.com/?page_id=2012

6. Good luck!

## Some notes
- The python environment to run this script needs matplotlib and numpy installed
- There are variables you can fiddle with in the python script to enhance the visualisation:
- `SCALE_SCENE` = 10. This scales the coordinates of your blender shape in case you made it too large or small. This is the overall scale of the image on your disc.
- `DISC_RADIUS` = 100. This sets the radius of the disc in the visualisation and svg
- `CAM_OFFSET` = 50. Position the hologram image vertically within your disc
- `REPORT_NAME` = "report.json". In case you wanna mess around
- `FPS` = 60. set framerate target of the visualisation
- `DRAW_DEBUG_CIRCLES` = 1 show the eventual circles that the SVG will contain (minus occlusion)
- `DEBUG_DEROTATE` = 0 de-rotate the moving points which trace the circle as if the disc is spinning.
- `SHOW_BOTTOM` = 0 also show the bottom image since an etched circle reflects at gradient = 0 (top and bottom edge of circle)


## Some bad maths
This of each vertex in the mesh as per below:

We have some point `P(x,y,z)` in cartesian coordinates, which is `P(rho, phi, z)` in polar coordinates.
The point as seen from above traces a circular path with radius `rho`, when spun around the origin on the Z axis. If we wished to visualise this, we can use the original `phi` as a time offset for the circular motion.

If we stack a bunch of these circles, and then offset them vertically on our image according to their `z` coordinate, we get a very cheap orthogonal projection (you can scale z to achieve a fake camera skew effect)

We want a circle where the glint traces a path as defined above. In a hologram etch, the glint is where the circle gradient is 0, i.e. the top.

We find that some point `P(rho, phi, z)` traces a new circle `C(cr, cx, cy)` where `r = radius and cx, cy are the coordinates of the circle centre`. The circle geometry is calculated as:

`cr = z+CAMERA_OFFSET`

`cx = r*cos(phi)`

`cy = r*sin(phi)`

We then just dont plot the parts of the circle that are occluded when the model is rotated by that much.

To trace this path, we create a moving point with `x = cr*sin(time) + cx, y = cr*cos(time) + cy`. 

These paths are what appears in the final SVG.

## Yes, I know.

I have positioned the camera in the blender file at about 30 degrees elevation. This means we probably should be warping the image by scaling the z coordinate of the points by an amount so when you view the image it all self corrects. You would do this by multiplying the z = cr = z+CAMERA_OFFSET by the cosine of the angle of elevation of the camera, and by having the camera elevation equal to the intended viewing angle.

