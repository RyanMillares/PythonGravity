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
    win = GraphWin('Space + Kruskals', x_dims, y_dims) #4/26, branch from v10
    win.setCoords(0,0,x_dims,y_dims)
    win.setBackground("black")

    
    # ALL DEBUG VARIABLES -------------------------------------------------------------------------------------------------------
    
    # radius of central mass
    center_radius = 12

    # radius of spawn range for planet ring
    spawn_range = 350

    # number of planets
    circle_num = 20  # bring down to 20 if lines enabled

    # force multiplier on planet's gravity
    force_multiplier = 1

    # multiplier on (randomized?) initial velocities of planets
    debug_start_velocity = 5

    # modifier on first planet mass/radius (testing potential binary systems)
    first_planet_multiplier = 1

    # max distance constrant from center
    stopping_distance = 700

    # line intensity (0, 1, 2), 0 = none, 1 = partial, 2 = full (limit to 20 planets)
    line_intensity = 0

    # length of experimental trails
    trail_length = 0

    # influence radius
    influence_radius = 25

    # border handler (1 = Cancel All Velocity, 2 = Invert and Dampen Velocity, 3 = Set velocity to center-mass gravity force, 4 = tp to center)
    border_handler = 2

    # collision handler (0 = none, 1 = Influence nearby velocities and repel at close distances, 2 = physics attempt)
    collision_handler = 0

    # original spawn velocity pattern (0 = none, 1 = random, 2 = circular)
    original_spawn_setting = 2

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

    center_gravity = center_radius**3
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
        planet_mass = randrange(4,9)

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

    @dataclass 
    class Edge:
        start: int
        end: int
        distance: float

    tree_edges = []
    # initialize velocities
    velocities = []
    collision_velocities = []
    minor_lines = []
    minor_targets = []
    for x in range(circle_num):
        if original_spawn_setting == 0:
            velocities.append(Velocity())
        elif original_spawn_setting == 1:
            velocities.append(Velocity(randrange(-200, 200) / 100, randrange(-200,200) / 100))
        elif original_spawn_setting == 2:
            velocities.append(Velocity(debug_start_velocity * math.cos(((math.pi * 2)/circle_num) * x + (math.pi/2)), debug_start_velocity * math.sin(((math.pi * 2)/circle_num) * x + (math.pi/2))))
        collision_velocities.append(Velocity())
        minor_lines.append(None)
        minor_targets.append(-1)


    old_line = None
    centerOfMass = None
    mass_sum = 0
    while(True):
        min_dist = 1000000
        curr_point = Point(0,0)
        curr_color = color_rgb(0,0,0)
        for _,_,num,mass in circles:
            collision_velocities[num] = velocities[num]

        for circle, choose_color, num, mass in circles:
            curr_trail_circle = Circle(circle.getCenter(), circle.getRadius())
            curr_trail_color = choose_color

            curr_pos = circle.getCenter()

            #new_pos = Point(newX, newY)
            x_dist = (center_point.x - (curr_pos.x + velocities[num].x))  
            y_dist = (center_point.y - (curr_pos.y + velocities[num].y))            
            curr_dis = math.dist([center_point.x, center_point.y],[curr_pos.x + velocities[num].x, curr_pos.y + velocities[num].y])

            velocities[num].x += (x_dist / (curr_dis ** 2)) * gravity_constant * (mass * center_gravity) / ((mass/force_multiplier)**2)# * (1 if (curr_dis > 3*(center_radius + circle.getRadius())) else -1)
            velocities[num].y += (y_dist / (curr_dis ** 2)) * gravity_constant * (mass * center_gravity) / ((mass/force_multiplier)**2)# * (1 if (curr_dis > 3*(center_radius + circle.getRadius())) else -1)

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

            # for v2 collision handling
            collision_velocity_x = velocities[num].x
            collision_velocity_y = velocities[num].y
            colls = 0
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

                    velocities[num].x += (x_minor / (dist_minor ** 2)) * (gravity_constant) * (mass * other_mass) / ((mass/force_multiplier)**2) * ((1 if (dist_minor > (other_circle.getRadius() + circle.getRadius())) else -1) if (collision_handler == 1) else 1)
                    velocities[num].y += (y_minor / (dist_minor ** 2)) * (gravity_constant) * (mass * other_mass) / ((mass/force_multiplier)**2) * ((1 if (dist_minor > (other_circle.getRadius() + circle.getRadius())) else -1) if (collision_handler == 1) else 1)

                    collision_velocity_x += (x_minor / (dist_minor ** 2)) * (gravity_constant) * (mass * other_mass) / ((mass/force_multiplier)**2) * ((1 if (dist_minor > (other_circle.getRadius() + circle.getRadius())) else -1) if (collision_handler == 1) else 1)
                    collision_velocity_y += (y_minor / (dist_minor ** 2)) * (gravity_constant) * (mass * other_mass) / ((mass/force_multiplier)**2) * ((1 if (dist_minor > (other_circle.getRadius() + circle.getRadius())) else -1) if (collision_handler == 1) else 1)

                    # v1 collision handling
                    if ((dist_minor < influence_radius) and mass_sum != 0 and collision_handler == 1):
                        velocity_offset_x = velocities[other_num].x - velocities[num].x
                        velocity_offset_y = velocities[other_num].y - velocities[num].y

                        velocities[num].x += math.pi*velocity_offset_x * (other_mass / mass_sum) / (mass**1.5 / force_multiplier)
                        velocities[num].y += math.pi*velocity_offset_y * (other_mass / mass_sum) / (mass**1.5 / force_multiplier)

                    # v2 collision handling
                    elif (collision_handler == 2 and dist_minor <= (circle.getRadius() + other_circle.getRadius())):
                        colls += 1

                        # third version, sqrt'ing added collision velocity, same issue as v2
                        #initial_collision_x = collision_velocities[num].x + 2*(other_mass / (mass + other_mass))*(collision_velocities[other_num].x - collision_velocities[num].x)
                        #initial_collision_y = collision_velocities[num].y + 2*(other_mass / (mass + other_mass))*(collision_velocities[other_num].y - collision_velocities[num].y)

                        #collision_velocity_x += math.sqrt(abs(initial_collision_x)) * (initial_collision_x / abs(initial_collision_x)) / 6
                        #collision_velocity_y += math.sqrt(abs(initial_collision_y)) * (initial_collision_y / abs(initial_collision_y)) / 6

                        # second version, add all calculated collision velocities (huge explosive increases in velocity???)
                        #collision_velocity_x += collision_velocities[num].x + 2*(other_mass / (mass + other_mass))*(collision_velocities[other_num].x - collision_velocities[num].x)
                        #collision_velocity_y += collision_velocities[num].y + 2*(other_mass / (mass + other_mass))*(collision_velocities[other_num].y - collision_velocities[num].y)
                        #print("Mass ", num, " collided with Mass ", other_num)
                        #print("Current velocity: (", velocities[num],"), Mass: ", mass)
                        #print("Other velocity: (", velocities[other_num],"), Mass: ", other_mass)
                        # first version, set velocity to calculated collision (causes weird sticking)
                        collision_velocity_x = collision_velocities[num].x + 2*(other_mass / (mass + other_mass))*(collision_velocities[other_num].x - collision_velocities[num].x)
                        collision_velocity_y = collision_velocities[num].y + 2*(other_mass / (mass + other_mass))*(collision_velocities[other_num].y - collision_velocities[num].y)
                        #print("Resulting velocity: (", collision_velocity_x, ", ", collision_velocity_y ,")\n")
                        #velocities[num] = Velocity(collision_velocity_x, collision_velocity_y)
                        
                    

            if (collision_handler == 2 and colls > 0):
                #print("Old: ",velocities[num].x, ", ", velocities[num].y)
                velocities[num] = Velocity(collision_velocity_x,collision_velocity_y)
                #print("New: ",velocities[num].x, ", ", velocities[num].y, "\n")
               



                    

            if (curr_dis > stopping_distance and (True if (border_handler == 4) else (math.sqrt(math.pow(velocities[num].x, 2) * math.pow(velocities[num].y, 2)) > 1))):
                if (border_handler) == 1:
                    velocities[num] = Velocity()
                elif border_handler == 2:
                    velocities[num] = Velocity(-velocities[num].x/2, -velocities[num].y/2)
                elif border_handler == 3:
                    velocities[num].x = (x_dist / (curr_dis ** 2)) * gravity_constant * (mass * center_gravity) / (mass / force_multiplier)
                    velocities[num].y = (y_dist / (curr_dis ** 2)) * gravity_constant * (mass * center_gravity) / (mass / force_multiplier)
                elif border_handler == 4: # only to be used with low center radius/gravity
                    circle.move(center_point.x - curr_pos.x, center_point.y - curr_pos.y)
                    velocities[num] = Velocity(velocities[num].x/2, velocities[num].y/2)



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
        #curr_pos = circle.getCenter()
        #mass_sum = total_mass
        #new_pos = Point(newX, newY)
        #for circle, _, num, _ in circles:
        #    x_dist = (centered_x - (circle.getCenter().x + velocities[num].x))  
        #    y_dist = (centered_y - (circle.getCenter().y + velocities[num].y))            
        #    curr_dis = math.dist([centered_x, centered_y],[circle.getCenter().x, circle.getCenter().y])

            #velocities[num].x += (x_dist / (curr_dis ** 2)) * gravity_constant * (mass * math.pow((total_mass/circle_num), 1)*3) / ((mass/force_multiplier)**2)
            #velocities[num].y += (y_dist / (curr_dis ** 2)) * gravity_constant * (mass * math.pow((total_mass/circle_num), 1)*3) / ((mass/force_multiplier)**2)
            #circle.move(velocities[num].x, velocities[num].y)
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
                union(parent, rank, x, y)

        for u, v, weight, c in results:
            edge_line = Line(circles[u][0].getCenter(), circles[v][0].getCenter())
            edge_line.setFill(c)
            edges.append(edge_line)
            edge_line.draw(win)
        for old_edge in tree_edges:
            old_edge.undraw()
        tree_edges = edges








main()