## Left double click to make point
## Right double click to make rigid / fixed point
## Left click once to select a point and left click once on another point to make an stick / edge connecting them 

import math
import cv2
import numpy as np
import time
import random

canvas = np.ones((500, 500, 3), dtype = np.uint8) * 255
WindDX = 1
WindDY = 1

precision = 3

def wind() : 
    offset = 2.41
    omega = 0.1
    t = time.time()
    x = WindDY * ((random.random() - 0.5) * 50 + 50) * math.cos(omega * t) ** 2
    y = WindDX * ((random.random() - 0.5) * 50 + 50) * math.cos(omega * t + offset) ** 2
    return x, y

lastWind = wind()

deltaTime = 1 / 30

iterations = 100

g = 500

class Point : 
    def __init__(self, pos, lock = False) : 
        self.pos = pos
        self.prevpos = pos
        self.isLocked = lock
    def lock(self) : 
        self.isLocked = True
    def unLock(self) : 
        self.isLocked = False

class Stick : 
    def __init__(self, point1 : Point, point2 : Point) : 
        self.point1, self.point2 = point1, point2
        self.updateLength()
    def updateLength (self) : 
        self.targetLen = distance(self.point1, self.point2)
    def getCurrLen(self) : 
        return distance(self.point1, self.point2)
    
def distance(point1 : Point, point2 : Point) : 
    (x1, y1), (x2, y2) = point1.pos, point2.pos
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def simulate(points, sticks) :
    global lastWind
    lastWind = wind()
    xW, yW = lastWind
    for point in points : 
        if not point.isLocked : 
            x, y = point.pos
            _x, _y = point.prevpos
            point.prevpos = point.pos
            x, y = 2 * x - _x, 2 * y - _y
            point.pos = (x + xW * deltaTime * deltaTime, y + 0.5 * g * deltaTime * deltaTime + yW * deltaTime * deltaTime)
    for iteration in range(iterations) : 
        for stick in sticks :
            (x1, y1), (x2, y2) = stick.point1.pos, stick.point2.pos 
            center = ((x1 + x2) / 2, (y1 + y2) / 2)
            currLen = stick.getCurrLen()
            if currLen == 0 : 
                print(stick.point1.pos, stick.point2.pos)
                print(sticks.index(stick))
            if not stick.point2.isLocked : 
                x2, y2 = center[0] + (x2 - center[0]) / currLen * stick.targetLen, center[1] + (y2 - center[1]) / currLen * stick.targetLen
            if not stick.point1.isLocked :
                x1, y1 = center[0] + (x1 - center[0]) / currLen * stick.targetLen, center[1] + (y1 - center[1]) / currLen * stick.targetLen
            stick.point1.pos = (x1, y1)
            stick.point2.pos = (x2, y2)

def convertInt(point) : 
    return int(point[0]), int(point[1])

def display(points, sticks) : 
    global canvas
    canvas = np.zeros((1000, 1900, 3), dtype = np.uint8) * 255

    for stick in sticks : 
        point1, point2 = stick.point1, stick.point2
        cv2.line(canvas, convertInt(point1.pos), convertInt(point2.pos), (255, 100, 100), 2)
    
    for point in points : 
        color =  (100, 255, 100)
        if point.isLocked : 
            color = (100, 100, 255)
        cv2.circle(canvas, convertInt(point.pos), 4, color, -1)
    
    cv2.putText(canvas, 'FPS : ' + str(int(1 / deltaTime)), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (100, 100, 255), 2)

    origin = (50, 600)
    delX, delY = lastWind
    d = math.sqrt((delX)**2 + (delY)**2)
    l = 40
    delX *= l / d
    delY *= l / d

    cv2.putText(canvas, 'Wind', (origin[0] - 10, origin[1] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 255), 2)
    cv2.arrowedLine(canvas, origin, convertInt((origin[0] + delX, origin[1])), (255, 100, 100), 3)
    cv2.arrowedLine(canvas, (origin[0], origin[1] + 5), convertInt((origin[0], origin[1] + 5 + delY)), (255, 100, 100), 3)
    
    cv2.imshow('Sim', canvas)
    return cv2.waitKey(2) & 0xFF

class RopeGenUI :
    def __init__(self) :
        self.points = []
        self.sticks = []
        self.stickPairs = []
        self.lastclicked = None
        self.canvas = np.zeros((1000, 1900, 3), dtype = np.uint8) * 255
        cv2.imshow('Construct Window', self.canvas)
        cv2.setMouseCallback('Construct Window', self._callback)
    def _callback(self, event, x, y, flags, param) : 
        # cv2.EVENT_MOUSEHWHEEL : Mouse wheel scroll 
        # cv2.EVENT_LBUTTONDOWN : Left button down
        # cv2.EVENT_LBUTTONUP   : Left button up
        # cv2.EVENT_MBUTTONDOWN : Scroll button down
        # cv2.EVENT_MBUTTONUP   : Scroll button up
        # cv2.EVENT_RBUTTONDOWN : Right button down
        # cv2.EVENT_RBUTTONUP   : Right button up
        
        # if event != 0 : print('Event : {}\nPos : {}, {}'.format(event, x, y))
        
        # if event == cv2.EVENT_MOUSEHWHEEL : print('Mousewheel Event\nPos : {} {}'.format(x, y))
        # elif event == cv2.EVENT_LBUTTONDOWN : print('LButtonDown Event\nPos : {} {}'.format(x, y))
        # elif event == cv2.EVENT_LBUTTONUP : print('LButtonUp Event\nPos : {} {}'.format(x, y))
        # elif event == cv2.EVENT_MBUTTONDOWN : print('MbuttonDown Event\nPos : {} {}'.format(x, y))
        # elif event == cv2.EVENT_MBUTTONUP : print('Mbuttonup Event\nPos : {} {}'.format(x, y))
        # elif event == cv2.EVENT_RBUTTONDOWN : print('RbuttonDown Event\nPos : {} {}'.format(x, y))
        # elif event == cv2.EVENT_RBUTTONUP : print('RbuttonUp Event\nPos : {} {}'.format(x, y))
        # else :
        #     return
        
        if event == cv2.EVENT_LBUTTONDBLCLK :
            new_point = Point((x, y))
            self.points.append(new_point)
            self.lastclicked = None
        elif event == cv2.EVENT_RBUTTONDBLCLK :
            new_point = Point((x, y), lock = True)
            self.points.append(new_point)
            self.lastclicked = None
        elif event == cv2.EVENT_LBUTTONDOWN : 
            pos = x, y
            for point in range(len(self.points)) :
                if math.sqrt((self.points[point].pos[0] - pos[0]) ** 2 + (self.points[point].pos[1] - pos[1]) ** 2) < precision :
                    if self.lastclicked is None :
                        self.lastclicked = point
                    else :
                        if point == self.lastclicked : 
                            print('Edge to same point cannot be made, removing response')
                        else :
                            if (self.lastclicked, point) not in self.stickPairs and (point, self.lastclicked) not in self.stickPairs : 
                                self.sticks.append(Stick(self.points[self.lastclicked], self.points[point]))
                                self.stickPairs.append((self.lastclicked, point))
                            else :
                                print('Stick already there between the point pair')
                        self.lastclicked = None
                    
                    break
            else :
                print('Click on some existing point to make an edge')
                self.lastclicked = None
    def construct(self) :
        key = None
        while key != 27 :
            key = self._display()     

        cv2.destroyWindow('Construct Window')  
    def _display(self) :
        self.canvas = np.zeros((1000, 1900, 3), dtype = np.uint8) * 255
        # cv2.imshow('Construct Window', Canvas)
        # cv2.setMouseCallback('Construct Window', self._callback)

        for stick in self.sticks : 
            point1, point2 = stick.point1, stick.point2
            cv2.line(self.canvas, convertInt(point1.pos), convertInt(point2.pos), (255, 100, 100), 2)
        
        for point in self.points : 
            color =  (100, 255, 100)
            
            if point.isLocked : 
                color = (100, 100, 255)
            
            if self.lastclicked is not None and self.points[self.lastclicked] == point :
                color = (255, 100, 100)
            
            cv2.circle(self.canvas, convertInt(point.pos), 4, color, -1)
        
        cv2.putText(self.canvas, 'FPS : ' + str(int(1 / deltaTime)), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (100, 100, 255), 2)

        # origin = (50, 600)
        # delX, delY = lastWind
        # d = math.sqrt((delX)**2 + (delY)**2)
        # l = 40
        # delX *= l / d
        # delY *= l / d

        # cv2.putText(canvas, 'Wind', (origin[0] - 10, origin[1] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 255), 2)
        # cv2.arrowedLine(canvas, origin, convertInt((origin[0] + delX, origin[1])), (255, 100, 100), 3)
        # cv2.arrowedLine(canvas, (origin[0], origin[1] + 5), convertInt((origin[0], origin[1] + 5 + delY)), (255, 100, 100), 3)
        
        cv2.imshow('Construct Window', self.canvas)
        return cv2.waitKey(2) & 0xFF

def main() : 
    global deltaTime
    global WindDX, WindDY
    points = []
    sticks = []

    # # construct points and sticks
    # d = 30
    # n = 29
    # offset = (10, 50)

    # # Standard Rope Design
    # points += [Point(offset)]                                                                               # 0
    # points += [Point((offset[0] + math.sqrt(3) / 2 * d, offset[1] - 1 / 2 * d))]                            # 1
    # points += [Point((offset[0] + math.sqrt(3) / 2 * d, offset[1] + 1 / 2 * d))]                            # 2
    # points += [Point((offset[0] + math.sqrt(3) / 1 * d, offset[1]))]                                        # 3
    # points += [Point((offset[0] + math.sqrt(3) / 1 * d + d * i, offset[1])) for i in range(1, n)]           # 3 + i
    # print(points[3].pos, points[4].pos)
    # points[-1].lock()

    # sticks += [Stick(points[0], points[1])]                                                                 # 0
    # sticks += [Stick(points[0], points[2])]                                                                 # 1
    # sticks += [Stick(points[1], points[3])]                                                                 # 2
    # sticks += [Stick(points[2], points[3])]                                                                 # 3
    # sticks += [Stick(points[1], points[2])]
    # sticks += [Stick(points[3 + i], points[4 + i]) for i in range(n - 1)]                                   # 4 + i

    # print(sticks[3].point1.pos, sticks[3].point2.pos)

    ropeGenerator = RopeGenUI()
    ropeGenerator.construct()

    points = ropeGenerator.points
    sticks = ropeGenerator.sticks

    display(points, sticks)

    # cv2.setMouseCallback("Sim", _callback, None)

    cv2.waitKey(0)

    
    start = time.time()
    key = None
    i = 0
    # Update Loop
    while key != 27 :
        simulate(points, sticks)
        key = display(points, sticks)
        now = time.time()
        deltaTime = now - start
        start = now
        i += 1
        if i % 200 == 0 : 
            if random.choice([0]*200 + [1] *200) : 
                WindDX = random.choice([-1, 1])
            if random.choice([0]*200 + [1] *200) : 
                WindDY *= random.choice([-1, 1])

# construct()

main()

cv2.destroyAllWindows()

# main()