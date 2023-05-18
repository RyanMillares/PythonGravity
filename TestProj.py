from graphics import *
from random import randrange

def rand_color():
    """ Generate a random color and return it. """

    return color_rgb(randrange(256), randrange(256), randrange(256))


def main():
    x_dims = 1400
    y_dims = 750
    prev_y = -1
    prev_x = -1
    win = GraphWin('Space', x_dims, y_dims)
    win.setCoords(0,0,x_dims,y_dims)
    win.setBackground("black")
    #win.yUp()
    circles = []
    for x in [-1, 1]:
        for y in [-1, 1]:
                circle = Circle(Point(250, 250), 20)
                circle.setFill(rand_color())
                circle.draw(win)
                circles.append((circle, (x, y)))
    while(True):
        #P = win.getMouse()
        #if(prev_y != -1):
        #    line = Line(Point(P.x, P.y), Point(prev_x, prev_y))
        #    line.setFill(rand_color())
        #    line.draw(win)
        #circle = Circle(Point(P.x, P.y), 10)
        #circle.setFill(rand_color())
        #circle.draw(win)
        
        #prev_y = P.y 
        #prev_x = P.x
        if(True):
            
            move_values = [-2, -1, -1, 1, 1, 2]

            
            for circle, (x, y) in circles:
                circle.move(move_values[randrange(6)], move_values[randrange(6)])

    #win.close()
    

main()