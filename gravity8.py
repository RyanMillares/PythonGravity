from gettext import lngettext
from hashlib import new
#from this import d
from tracemalloc import stop
#from os import minor
from graphics import *
from random import randrange
from dataclasses import dataclass
import math
#from win32api import GetSystemMetrics

def rand_color():
    """ Generate a random color and return it. """

    return color_rgb(randrange(256), randrange(256), randrange(256))

#def return_dist(p1, p2): #assume parameters are points


def main():

    gravity_constant = (6.67408 * math.pow(10,-1))
    x_dims = 1550
    y_dims = 800
    prev_y = -1
    prev_x = -1
    win = GraphWin('Space v8', x_dims, y_dims) #4/17
    win.setCoords(0,0,x_dims,y_dims)
    win.setBackground("black")

    
    # ALL DEBUG VARIABLES -------------------------------------------------------------------------------------------------------
    
    # radius of central mass
    center_radius = 5

    # radius of spawn range for planet ring
    spawn_range = 350

    # number of planets
    circle_num = 22  # bring down to 20 if lines enabled

    # force multiplier on planet's gravity
    force_multiplier = 3

    # multiplier on (randomized?) initial velocities of planets
    debug_start_velocity = 3

    # modifier on first planet mass/radius (testing potential binary systems)
    first_planet_multiplier = 1

    # max distance constrant from center
    stopping_distance = 700

    # line intensity (0, 1, 2), 0 = none, 1 = partial, 2 = full (limit to 20 planets)
    line_intensity = 0

    # length of experimental trails
    trail_length = 0

    # influence radius
    influce_radius = 20

    if (line_intensity > 1):
        circle_num = min(circle_num, 20)

    # --------------------------------------------------------------------------------------------------------------------------------
    
    color = color_rgb(0,0,0)
    
    # space range
    space_range = Circle(Point(x_dims/2, y_dims/2), stopping_distance)
    space_range.setFill(color_rgb(20,20,20))
    space_range.draw(win)

    circles = []
    has_drawn = []
    dot_trails = []
    old_trails = []

    center_gravity = center_radius**2
    circle = Circle(Point(x_dims/2, y_dims/2), center_radius)
    circle.setFill("green")
    center_point = circle.getCenter()
    circle.draw(win)

    #offsets = [(spawn_dist, 0, 0), (spawn_dist/2,-spawn_dist/math.sqrt(3),1), (-spawn_dist/2, -spawn_dist/math.sqrt(3), 2), 
    #(-spawn_dist, 0, 3), (-spawn_dist/2, spawn_dist/math.sqrt(3), 4), (spawn_dist/2, spawn_dist/math.sqrt(3), 5)]

    offsets = []
    for x in range(circle_num):
        offsets.append((spawn_range * math.cos(((math.pi * 2)/circle_num) * x), spawn_range * math.sin(((math.pi * 2)/circle_num) * x), x))

    # initialize circles
    first = True
    for (x_offset, y_offset, index) in offsets:
        dot_trails.append([])
        old_trails.append([])
        has_drawn.append(False)
        planet_mass = randrange(5,10)

        # test huge masses by increasing one single planet
        if first:
            planet_mass *= first_planet_multiplier
            first = False
        circle = Circle(Point(x_dims/2 + x_offset, y_dims/2 + y_offset), planet_mass)
        choose_color = rand_color()
        circle.setFill(choose_color)
        circle.draw(win)
        circles.append((circle, choose_color, index, planet_mass**2))

    #new_line = Line(Point(0,0), Point(1,1))
    #new_line.setFill("black")

    @dataclass
    class Velocity:
        x: float = 0
        y: float = 0

    # initialize velocities
    velocities = []
    minor_lines = []
    minor_targets = []
    for x in range(circle_num):
        #velocities.append(Velocity(randrange(-200, 200) / 100, randrange(-200,200) / 100))
        #velocities.append(Velocity())
        velocities.append(Velocity(debug_start_velocity * math.cos(((math.pi * 2)/circle_num) * x + (math.pi/2)), debug_start_velocity * math.sin(((math.pi * 2)/circle_num) * x + (math.pi/2))))
        minor_lines.append(None)
        minor_targets.append(-1)
    #velocities.append(Velocity(0, -0.2))
    #velocities.append(Velocity(-0.07, -0.1))
    #velocities.append(Velocity(-0.15, 0.08))
    #velocities.append(Velocity(0, 0.12))
    #velocities.append(Velocity(0.07, 0.15))
    #velocities.append(Velocity(0.18,-0.08))



    old_line = None
    centerOfMass = None
    mass_sum = 0
    while(True):
        min_dist = 1000000
        curr_point = Point(0,0)
        curr_color = color_rgb(0,0,0)
        

        for circle, choose_color, num, mass in circles:
            curr_trail_circle = Circle(circle.getCenter(), circle.getRadius())
            curr_trail_color = choose_color

            curr_pos = circle.getCenter()

            #new_pos = Point(newX, newY)
            x_dist = (center_point.x - (curr_pos.x + velocities[num].x))  
            y_dist = (center_point.y - (curr_pos.y + velocities[num].y))            
            curr_dis = math.dist([center_point.x, center_point.y],[curr_pos.x + velocities[num].x, curr_pos.y + velocities[num].y])

            velocities[num].x += (x_dist / (curr_dis ** 2)) * gravity_constant * (mass * center_gravity) / ((mass/force_multiplier)**2) * (1 if (curr_dis > 2*(center_radius + circle.getRadius())) else -1)
            velocities[num].y += (y_dist / (curr_dis ** 2)) * gravity_constant * (mass * center_gravity) / ((mass/force_multiplier)**2) * (1 if (curr_dis > 2*(center_radius + circle.getRadius())) else -1)

            new_pos = Point(velocities[num].x, velocities[num].y)
            circle.move(new_pos.x,new_pos.y)
            if (curr_dis < min_dist):
                curr_point = Point(curr_pos.x + new_pos.x, curr_pos.y + new_pos.y)
                curr_color = choose_color
                min_dist = curr_dis

            circle_min_dist = 100000
            minor_point = Point(0,0)
            minor_color = color_rgb(0,0,0)
            minor_target = -1
            for other_circle, other_color, other_num, other_mass in circles:
                # only check other dots
                if num != other_num:
                    dot_dist = math.dist([circle.getCenter().x, circle.getCenter().y], [other_circle.getCenter().x, other_circle.getCenter().y])
                    if dot_dist < circle_min_dist:
                        minor_point = other_circle.getCenter()
                        minor_color = other_color 
                        circle_min_dist = dot_dist
                        minor_targets[num] = other_num
                    x_minor = (other_circle.getCenter().x - circle.getCenter().x)
                    y_minor = (other_circle.getCenter().y - circle.getCenter().y)
                    dist_minor = math.dist([circle.getCenter().x, circle.getCenter().y], [other_circle.getCenter().x, other_circle.getCenter().y])

                    velocities[num].x += (x_minor / (dist_minor ** 2)) * (gravity_constant) * (mass * other_mass) / ((mass/force_multiplier)**2) * (1 if (dist_minor > (other_circle.getRadius() + circle.getRadius())) else -1)
                    velocities[num].y += (y_minor / (dist_minor ** 2)) * (gravity_constant) * (mass * other_mass) / ((mass/force_multiplier)**2) * (1 if (dist_minor > (other_circle.getRadius() + circle.getRadius())) else -1)

                    # v1 collision handling
                    if (dist_minor < influce_radius and mass_sum is not 0):
                        velocity_offset_x = velocities[other_num].x - velocities[num].x
                        velocity_offset_y = velocities[other_num].y - velocities[num].y

                        velocities[num].x += 2*velocity_offset_x * (other_mass / mass_sum) #/ (mass / force_multiplier)
                        velocities[num].y += 2*velocity_offset_y * (other_mass / mass_sum) #/ (mass / force_multiplier)


                    

            if (curr_dis > stopping_distance and (math.sqrt(math.pow(velocities[num].x, 2) * math.pow(velocities[num].y, 2)) > 1)):
                velocities[num] = Velocity()

            new_pos = Point(velocities[num].x, velocities[num].y)
            # remove this line when done checking spawn positions
            #velocities[num] = Velocity()
            circle.move(new_pos.x,new_pos.y)

            has_drawn[num] = False

            minor_line = Line(circle.getCenter(), minor_point)
            minor_line.setFill(minor_color)
            minor_line.setWidth(2)
            if (line_intensity == 1):
                if (minor_targets[minor_targets[num]] != num):    
                    minor_line.draw(win)
                    has_drawn[num] = True
            elif (line_intensity == 2):

                if (minor_targets[minor_targets[num]] != num):    
                    minor_line.draw(win)
                    has_drawn[num] = True
                elif(not has_drawn[minor_targets[num]]):
                    minor_line.draw(win)
                    has_drawn[num] = True     

                
            if minor_lines[num]:
                minor_lines[num].undraw()
            minor_lines[num] = minor_line
            # trail code

            
            #for drawn_trail_circle in old_trails:
            #    drawn_trail_circle.undraw()
            #old_trails = []
            if True:
                trail_index = 1
                drawn_trails = old_trails[num]
                for old_circle in dot_trails[num]:
                    circle_trail = Circle(old_circle.getCenter(), old_circle.getRadius() / (math.pow(1.1, trail_index)))
                    circle_trail.setFill(choose_color)
                    old_trails[num].append(circle_trail)
                    circle_trail.draw(win)
                    trail_index += 1

                for drawn_trail in drawn_trails:
                    drawn_trail.undraw()

                dot_trails[num].insert(0,curr_trail_circle)
                if (len(dot_trails[num]) > trail_length):
                    dot_trails[num].pop()


          



        new_line = Line(center_point, curr_point)
        new_line.setFill(curr_color)
        new_line.setWidth(2)
        #if (line_intensity > 0):
            #new_line.draw(win)
        if old_line:
            old_line.undraw()
        old_line = new_line
        

        # center of gravity debug
        center_size = 5
        total_mass = center_gravity
        total_y = (y_dims/2) * center_gravity
        total_x = (x_dims/2) * center_gravity
        for circle, _, _, mass in circles:
            total_mass += mass
            total_y += circle.getCenter().y * mass 
            total_x += circle.getCenter().x * mass 
        centered_y = total_y / total_mass 
        centered_x = total_x / total_mass
        new_center = Rectangle(Point(centered_x - 5, centered_y - 5), Point(centered_x + 5, centered_y + 5))
        new_center.setFill("white")
        #new_center.draw(win)
        if centerOfMass:
            centerOfMass.undraw()
        centerOfMass = new_center
        curr_pos = circle.getCenter()
        mass_sum = total_mass
        #new_pos = Point(newX, newY)
        #for circle, _, num, _ in circles:
        #    x_dist = (centered_x - (circle.getCenter().x + velocities[num].x))  
        #    y_dist = (centered_y - (circle.getCenter().y + velocities[num].y))            
        #    curr_dis = math.dist([centered_x, centered_y],[circle.getCenter().x, circle.getCenter().y])

            #velocities[num].x += (x_dist / (curr_dis ** 2)) * gravity_constant * (mass * math.pow((total_mass/circle_num), 1)*3) / ((mass/force_multiplier)**2)
            #velocities[num].y += (y_dist / (curr_dis ** 2)) * gravity_constant * (mass * math.pow((total_mass/circle_num), 1)*3) / ((mass/force_multiplier)**2)
            #circle.move(velocities[num].x, velocities[num].y)
        

main()