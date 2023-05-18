import time
from datetime import datetime
from tracemalloc import start
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

    win = GraphWin('Gravity Clock', x_dims, y_dims) # 4/13, started 1:00 PM
    win.setCoords(0,0,x_dims,y_dims)
    win.setBackground("black")

    
    # ALL DEBUG VARIABLES -------------------------------------------------------------------------------------------------------
    
    # radius of central mass
    center_radius = 10

    # radius of clock masses
    clock_radius = 15

    # radius of spawn range for planet ring
    spawn_range = 350

    # number of planets
    circle_num = 18 # bring down to 20 if lines enabled

    # force multiplier on planet's gravity
    force_multiplier = 2

    # multiplier on (randomized?) initial velocities of planets
    debug_start_velocity = 8

    # modifier on first planet mass/radius (testing potential binary systems)
    first_planet_multiplier = 1

    # max distance constrant from center
    stopping_distance = 800

    # line intensity (0, 1, 2), 0 = none, 1 = partial, 2 = full (limit to 20 planets)
    line_intensity = 0

    # number of clock hands (1, 2, 3) 1 = sec, 2 = sec/min, 3 = sec/min/hour
    time_measures = 3

    # --------------------------------------------------------------------------------------------------------------------------------

    

    # space range
    space_range = Circle(Point(x_dims/2, y_dims/2), stopping_distance)
    space_range.setFill(color_rgb(25,25,25))
    space_range.draw(win)

    circles = []
    center_gravity = center_radius**2
    circle = Circle(Point(x_dims/2, y_dims/2), center_radius)
    circle.setFill("green")
    center_point = circle.getCenter()
    circle.draw(win)

    
    millis = time.time()
    date = datetime.fromtimestamp(millis)

    start_sec = (date.second + (date.microsecond / 1000000))
    fraction_sec = start_sec / 60
    start_min = date.minute + fraction_sec
    fraction_min = start_min / 60
    start_hour = date.hour + fraction_min
    fraction_hour = start_hour / 12
    time_array = [fraction_sec, fraction_min, fraction_hour]

    clock_masses = []
    clock_lines = []
    for x in range(time_measures):
        offset = stopping_distance * ((6- 2*x) / 16)
        x_offset = offset * (math.cos(-(2 * math.pi * time_array[x]) + math.pi / 2))
        y_offset = offset * (math.sin(-(2 * math.pi * time_array[x]) + math.pi/2))
        
        
        clock_circle = Circle(Point(x_offset + x_dims/2, y_offset + y_dims/2), clock_radius)
        clock_circle.setFill(color_rgb(0,175,0))
        clock_circle.draw(win)
        clock_masses.append((clock_circle, clock_radius ** 2, x))

        clock_line = Line(clock_circle.getCenter(), center_point)
        clock_line.setFill("green")
        clock_line.setWidth(2*(x + 2))
        clock_line.draw(win)
        clock_lines.append(clock_line)

    #offsets = [(spawn_dist, 0, 0), (spawn_dist/2,-spawn_dist/math.sqrt(3),1), (-spawn_dist/2, -spawn_dist/math.sqrt(3), 2), 
    #(-spawn_dist, 0, 3), (-spawn_dist/2, spawn_dist/math.sqrt(3), 4), (spawn_dist/2, spawn_dist/math.sqrt(3), 5)]

    offsets = []
    for x in range(circle_num):
        offsets.append((spawn_range * math.cos(((math.pi * 2)/circle_num) * x), spawn_range * math.sin(((math.pi * 2)/circle_num) * x), x))

    # initialize circles
    first = True
    for (x_offset, y_offset, index) in offsets:
        planet_mass = randrange(3,10)

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
        velocities.append(Velocity(debug_start_velocity * math.cos(((math.pi * 2)/circle_num) * x - (math.pi/2)), debug_start_velocity * math.sin(((math.pi * 2)/circle_num) * x - (math.pi/2))))
        minor_lines.append(None)
        minor_targets.append(-1)




    old_line = None
    centerOfMass = None
    while(True):

        # clock portion
        millis = time.time()
        date = datetime.fromtimestamp(millis)

        start_sec = (date.second + (date.microsecond / 1000000))
        fraction_sec = start_sec / 60
        start_min = date.minute + fraction_sec
        fraction_min = start_min / 60
        start_hour = date.hour + fraction_min
        fraction_hour = start_hour / 12
        time_array = [fraction_sec, fraction_min, fraction_hour]

        for clock_circle, mass, measure in clock_masses:
            offset = stopping_distance * ((6 - 2*measure) / 16)
            x_new_pos = offset * (math.cos(-(2 * math.pi * time_array[measure]) + math.pi / 2)) + x_dims/2
            y_new_pos = offset * (math.sin(-(2 * math.pi * time_array[measure]) + math.pi / 2)) + y_dims/2

            clock_circle.move(x_new_pos - clock_circle.getCenter().x, y_new_pos - clock_circle.getCenter().y)
            new_clock_line = Line(Point(x_new_pos, y_new_pos), center_point)
            new_clock_line.setFill(color_rgb(0,175,0))
            new_clock_line.setWidth(2*(measure+1))
            new_clock_line.draw(win)
            if (clock_lines[measure]):
                clock_lines[measure].undraw()
            clock_lines[measure] = new_clock_line





        min_dist = 1000000
        curr_point = Point(0,0)
        curr_color = color_rgb(0,0,0)
        

        for circle, choose_color, num, mass in circles:
            curr_pos = circle.getCenter()

            #new_pos = Point(newX, newY)
            # gravity from center
            x_dist = (center_point.x - (curr_pos.x + velocities[num].x))  
            y_dist = (center_point.y - (curr_pos.y + velocities[num].y))            
            curr_dis = math.dist([center_point.x, center_point.y],[curr_pos.x + velocities[num].x, curr_pos.y + velocities[num].y])

            velocities[num].x += (x_dist / (curr_dis ** 2)) * gravity_constant * (mass * center_gravity) / ((mass/force_multiplier)**2)
            velocities[num].y += (y_dist / (curr_dis ** 2)) * gravity_constant * (mass * center_gravity) / ((mass/force_multiplier)**2)

            new_pos = Point(velocities[num].x, velocities[num].y)

            # gravity from clock masses
            for clock_ball, ball_mass, _ in clock_masses:
                x_dist = (clock_ball.getCenter().x - (curr_pos.x + velocities[num].x))  
                y_dist = (clock_ball.getCenter().y - (curr_pos.y + velocities[num].y))            
                new_dis = math.dist([clock_ball.getCenter().x, clock_ball.getCenter().y],[curr_pos.x + velocities[num].x, curr_pos.y + velocities[num].y])

                velocities[num].x += (x_dist / (new_dis ** 2)) * gravity_constant * (mass * ball_mass) / ((mass/force_multiplier)**2)
                velocities[num].y += (y_dist / (new_dis ** 2)) * gravity_constant * (mass * ball_mass) / ((mass/force_multiplier)**2)

            # central line
            if (curr_dis < min_dist):
                curr_point = Point(curr_pos.x + new_pos.x, curr_pos.y + new_pos.y)
                curr_color = choose_color
                min_dist = curr_dis

            circle_min_dist = 100000
            minor_point = Point(0,0)
            minor_color = color_rgb(0,0,0)
            minor_target = -1
            # gravity (and line calcs) from other planets/masses
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

            if (curr_dis > stopping_distance and (math.sqrt(math.pow(velocities[num].x, 2) * math.pow(velocities[num].y, 2)) > 1)):
                velocities[num] = Velocity()
            
            # remove this line when done checking spawn positions
            #velocities[num] = Velocity()

            new_pos = Point(velocities[num].x, velocities[num].y)
            circle.move(new_pos.x,new_pos.y)


            minor_line = Line(circle.getCenter(), minor_point)
            minor_line.setFill(minor_color)
            minor_line.setWidth(2)
            if (line_intensity == 1):
                minor_line.draw(win)
            elif (line_intensity == 2):

                if (minor_targets[minor_targets[num]] != num):    
                    minor_line.draw(win)
                

                
            if minor_lines[num]:
                minor_lines[num].undraw()
            minor_lines[num] = minor_line
          



        new_line = Line(center_point, curr_point)
        new_line.setFill(curr_color)
        new_line.setWidth(2)
        if (line_intensity > 0):
            new_line.draw(win)
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

main()