from gettext import lngettext
from hashlib import new
#from this import d
from tracemalloc import stop
from turtle import color
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

def find(parent, i):
    if parent[i] == i:
        return i
    return find(parent, parent[i])

def union(parent, rank, x, y):
    xroot = find(parent, x)
    yroot = find(parent, y)
 
    # Attach smaller rank tree under root of
    # high rank tree (Union by Rank)
    if rank[xroot] < rank[yroot]:
        parent[xroot] = yroot
    elif rank[xroot] > rank[yroot]:
        parent[yroot] = xroot
 
    # If ranks are same, then make one as root
    # and increment its rank by one
    else:
        parent[yroot] = xroot
        rank[xroot] += 1


def main():

    gravity_constant = (6.67408 * math.pow(10,-1))
    x_dims = 1550
    y_dims = 800
    prev_y = -1
    prev_x = -1
    win = GraphWin('Gravity Tree Screensaver', x_dims, y_dims) #4/26, branch from GravityScatter, applies Kruskals Algorithm in line drawing
    win.setCoords(0,0,x_dims,y_dims)
    win.setBackground("black")

    
    # ALL DEBUG VARIABLES -------------------------------------------------------------------------------------------------------
    
    # radius of central mass
    center_radius = 20

    # radius of spawn range for planet ring
    spawn_range = 350

    # number of planets
    circle_num = 30  # bring down to 20 if lines enabled

    # force multiplier on planet's gravity
    force_multiplier = 1.75

    # multiplier on (randomized?) initial velocities of planets
    debug_start_velocity = 3

    # modifier on first planet mass/radius (testing potential binary systems)
    first_planet_multiplier = 1

    # max distance constrant from center
    stopping_distance = 1500

    # line intensity (0, 1, 2), 0 = none, 1 = partial, 2 = full (limit to 20 planets)
    line_intensity = 0

    if (line_intensity > 1):
        circle_num = min(circle_num, 20)

    # --------------------------------------------------------------------------------------------------------------------------------
    
    
    # space range
    space_range = Circle(Point(x_dims/2, y_dims/2), stopping_distance)
    space_range.setFill(color_rgb(10,10,10))
    space_range.draw(win)

    circles = []
    centers = []
    has_drawn = []
    # Add Stars/Holes --------------------------------------------------------------------------------------------------

    pull_stars = []

    center_gravity = (center_radius**2)
    circle = Circle(Point(x_dims/4, y_dims/2), center_radius)
    circle.setFill(color_rgb(50,50,50))
    center_point = circle.getCenter()
    #circle.draw(win)
    centers.append((circle, center_gravity))

    pull_stars.append(circle)

    center_gravity2 = -((center_radius*0.75)**2)
    circle2 = Circle(Point(2 * x_dims/4, y_dims/2), center_radius*0.75)
    circle2.setFill(color_rgb(200,200,200))
    center_point = circle2.getCenter()
    #circle2.draw(win)
    centers.append((circle2, center_gravity2))

    push_star = circle2

    center_gravity3 = (center_radius**2)
    circle3 = Circle(Point(3 * x_dims/4, y_dims/2), center_radius)
    circle3.setFill(color_rgb(50,50,50))
    center_point = circle3.getCenter()
    #circle3.draw(win)
    centers.append((circle3, center_gravity3))
    pull_stars.append(circle3)
    #--------------------------------------------------------------------------------------------------------------------

    #offsets = [(spawn_dist, 0, 0), (spawn_dist/2,-spawn_dist/math.sqrt(3),1), (-spawn_dist/2, -spawn_dist/math.sqrt(3), 2), 
    #(-spawn_dist, 0, 3), (-spawn_dist/2, spawn_dist/math.sqrt(3), 4), (spawn_dist/2, spawn_dist/math.sqrt(3), 5)]

    tree_edges = []

    offsets = []
    for x in range(circle_num):
        offsets.append((spawn_range * math.cos(((math.pi * 2)/circle_num) * x), spawn_range * math.sin(((math.pi * 2)/circle_num) * x), x))

    # initialize circles
    first = True
    for (x_offset, y_offset, index) in offsets:
        has_drawn.append(False)
        planet_mass = randrange(5,11)

        # test huge masses by increasing one single planet
        if first:
            planet_mass *= first_planet_multiplier
            first = False
        circle = Circle(Point(x_dims/2 + x_offset, y_dims/2 + y_offset), planet_mass)
        choose_color = rand_color()
        circle.setFill(choose_color)
        #circle.draw(win)
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


    while(True):
        

        for circle, choose_color, num, mass in circles:
            curr_pos = circle.getCenter()


            #new_pos = Point(newX, newY)
            for center, center_mass in centers:
                curr_dis = math.dist([center.getCenter().x, center.getCenter().y],[curr_pos.x + velocities[num].x, curr_pos.y + velocities[num].y])

                x_dist = (center.getCenter().x - (curr_pos.x + velocities[num].x))  
                y_dist = (center.getCenter().y - (curr_pos.y + velocities[num].y))            
                curr_dis = math.dist([center.getCenter().x, center.getCenter().y],[curr_pos.x + velocities[num].x, curr_pos.y + velocities[num].y])

                velocities[num].x += (x_dist / (curr_dis ** 2)) * gravity_constant * (mass * center_mass) / ((mass/force_multiplier)**2)
                velocities[num].y += (y_dist / (curr_dis ** 2)) * gravity_constant * (mass * center_mass) / ((mass/force_multiplier)**2)
           

            new_pos = Point(velocities[num].x, velocities[num].y)
            circle.move(new_pos.x,new_pos.y)


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

            if (curr_dis > stopping_distance and (math.sqrt(math.pow(velocities[num].x, 2) * math.pow(velocities[num].y, 2)) > 1)):
                velocities[num] = Velocity()

            new_pos = Point(velocities[num].x, velocities[num].y)
            # remove this line when done checking spawn positions
            #velocities[num] = Velocity()
            circle.move(new_pos.x,new_pos.y)

            for pull_star in pull_stars:
                star_dist = math.dist([circle.getCenter().x, circle.getCenter().y], [pull_star.getCenter().x, pull_star.getCenter().y])
                if star_dist < center_radius:
                    contact_offset_x = circle.getCenter().x - pull_star.getCenter().x
                    contact_offset_y = circle.getCenter().y - pull_star.getCenter().y

                    transport_x = push_star.getCenter().x + contact_offset_x
                    transport_y = push_star.getCenter().y + contact_offset_y

                    circle.move((transport_x - circle.getCenter().x),(transport_y - circle.getCenter().y))
                    velocities[num].x *= 0.5
                    velocities[num].y *= 0.5
                    break

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
          
        # kruskals algorithm
        #   
        results = []
        sorted_index = 0 #i
        result_index = 0 #e
        graph = []
        edges = []
        pairs = []
        parent = []
        rank = []

        for circle, color, num, mass in circles:
            parent.append(num)
            rank.append(0)
            for other_circle, other_color, other_num, other_mass in circles:
                if num != other_num:   
                    dist_minor = math.dist([circle.getCenter().x, circle.getCenter().y], [other_circle.getCenter().x, other_circle.getCenter().y])
                    if (other_num, num) not in pairs:
                        pairs.append((num, other_num))
                        graph.append([num, other_num, dist_minor, color])

        graph = sorted(graph, key = lambda edge: edge[2])
        while result_index < len(circles) - 1:
            # pick smallest edge and increment index for next iteration
            u, v, w, c = graph[sorted_index]
            sorted_index += 1
            x = find(parent, u)
            y = find(parent, v)

            # include in result if including does not cause cycle, increment the result index
            if x != y:
                result_index += 1
                results.append([u, v, w, c])
                #added union
                union(parent, rank, x, y)

        # draw the spanning tree and undraw the previous frame's tree
        for u, v, weight, c in results:
            edge_line = Line(circles[u][0].getCenter(), circles[v][0].getCenter())
            edge_line.setFill(c)
            edges.append(edge_line)
            edge_line.draw(win)
        for old_edge in tree_edges:
            old_edge.undraw()
        tree_edges = edges



main()