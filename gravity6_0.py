from hashlib import new
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
    win = GraphWin('Space v6.0', x_dims, y_dims) # 4/12
    win.setCoords(0,0,x_dims,y_dims)
    win.setBackground("black")

    
    # ALL DEBUG VARIABLES -------------------------------------------------------------------------------------------------------
    
    # radius of central mass
    center_radius = 16

    # radius of spawn range for planet ring
    spawn_range = 350

    # number of planets
    circle_num = 24 # bring down to 20 if lines enabled

    # force multiplier on planet's gravity
    force_multiplier = 2

    # multiplier on (randomized?) initial velocities of planets
    debug_start_velocity = 3

    # modifier on first planet mass/radius (testing potential binary systems)
    first_planet_multiplier = 2.5

    # --------------------------------------------------------------------------------------------------------------------------------

    circles = []
    center_gravity = center_radius**2
    circle = Circle(Point(x_dims/2, y_dims/2), center_radius)
    circle.setFill(rand_color())
    center_point = circle.getCenter()
    circle.draw(win)

    #offsets = [(spawn_dist, 0, 0), (spawn_dist/2,-spawn_dist/math.sqrt(3),1), (-spawn_dist/2, -spawn_dist/math.sqrt(3), 2), 
    #(-spawn_dist, 0, 3), (-spawn_dist/2, spawn_dist/math.sqrt(3), 4), (spawn_dist/2, spawn_dist/math.sqrt(3), 5)]

    offsets = []
    for x in range(circle_num):
        offsets.append((spawn_range * math.cos((360/circle_num) * x), spawn_range * math.sin((360/circle_num) * x), x))

    # initialize circles
    first = True
    for (x_offset, y_offset, index) in offsets:
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
        velocities.append(Velocity(debug_start_velocity * math.cos((360/circle_num) * x + 90), debug_start_velocity * math.sin((360/circle_num) * x + 90)))
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
    while(True):
        min_dist = 1000000
        curr_point = Point(0,0)
        curr_color = color_rgb(0,0,0)
        

        for circle, choose_color, num, mass in circles:
            curr_pos = circle.getCenter()


            #new_pos = Point(newX, newY)
            x_dist = (center_point.x - (curr_pos.x + velocities[num].x))  
            y_dist = (center_point.y - (curr_pos.y + velocities[num].y))            
            curr_dis = math.dist([center_point.x, center_point.y],[curr_pos.x + velocities[num].x, curr_pos.y + velocities[num].y])

            velocities[num].x += (x_dist / (curr_dis ** 2)) * gravity_constant * (mass * center_gravity) / ((mass/force_multiplier)**2)
            velocities[num].y += (y_dist / (curr_dis ** 2)) * gravity_constant * (mass * center_gravity) / ((mass/force_multiplier)**2)

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

                    velocities[num].x += (x_minor / (dist_minor ** 2)) * (gravity_constant) * (mass * other_mass) / ((mass/force_multiplier)**2)
                    velocities[num].y += (y_minor / (dist_minor ** 2)) * (gravity_constant) * (mass * other_mass) / ((mass/force_multiplier)**2)



            minor_line = Line(circle.getCenter(), minor_point)
            minor_line.setFill(minor_color)
            minor_line.setWidth(2)
            #minor_line.draw(win)
            #if (minor_targets[minor_targets[num]] != num):    
            #    minor_line.draw(win)
                

                
            if minor_lines[num]:
                minor_lines[num].undraw()
            minor_lines[num] = minor_line




        new_line = Line(center_point, curr_point)
        new_line.setFill(curr_color)
        new_line.setWidth(2)
        #new_line.draw(win)
        if old_line:
            old_line.undraw()
        old_line = new_line
        
        # center of gravity debug
        #center_size = 5
        #total_mass = center_gravity
        #total_y = (y_dims/2) * center_gravity
        #total_x = (x_dims/2) * center_gravity
        #for circle, _, _, mass in circles:
        #    total_mass += mass
        #    total_y += circle.getCenter().y * mass 
        #    total_x += circle.getCenter().x * mass 
        #centered_y = total_y / total_mass 
        #centered_x = total_x / total_mass
        #new_center = Rectangle(Point(centered_x - 5, centered_y - 5), Point(centered_x + 5, centered_y + 5))
        #new_center.setFill("white")
        #new_center.draw(win)
        #if centerOfMass:
        #    centerOfMass.undraw()
        #centerOfMass = new_center

main()