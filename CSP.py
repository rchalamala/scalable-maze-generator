#!/usr/bin/env python3
# ^ shebang so unix environments can execute file easily

# imports modules needed for various actions
from collections import deque
from random import choice
from numpy import floor, full
import pygame
from pygame import Rect, MOUSEBUTTONDOWN
from screeninfo import get_monitors
import sys

# initializes global variables to N/A or 0 if applicable
side = 0
border = 0
delay = 0
gridSize = 0
consoleSize = 0
console = None

# creates dictionary to access all colors, which results in the user being able to enter a color name, rather than a RGB color code
colorKeys = list(pygame.color.THECOLORS.keys())

# function to convert coordinate grid points to pixel locations
def coordinateOffset(operand, userInput=False):
    if userInput is False:
        return int(operand * (side + border) + border)
    return (operand - border) / (side + border)

# prints all colors in dictionary for user to see
def printColors():
    for key in colorKeys:
        print(key)

# stores used color so user does not pick the same color multiple times
colors = []

# takes in color input and checks to see if it has already been used, if so a loop runs until a color is entered that hasn't been used
def colorInput(inputText):
    color = input(inputText).lower()
    while color == "p":
        printColors()
        color = input(inputText).lower()
    while color not in pygame.color.THECOLORS or color in colors:
        print("Entered input is invalid. ")
        color = input(inputText).lower()
        while color == "p":
            printColors()
            color = input(inputText).lower()
    colors.append(color)
    return pygame.color.THECOLORS[color]

# initializes all variables and console/screen
def initialize():
    colorKeys.sort() # sorts colors in dictionary
    heights = [] # vertical resolution of display
    for m in get_monitors(): # gets monitor size, so console will scale accordingly
        heights.append(int(str(m)[str(m).find("height="):].split(',', 1)[0][7:]))
    global side
    side = max(int(heights[0] // 100 * 1.5), 30) # generates side length by scaling with respect to monitor vertical resolution
    global border
    border = int(max(side / 10, 1)) # the borderwidth of each block
    global delay
    delay = int(input("Enter the delay of the pointer in milliseconds (-1 for default (10ms)): ")) # the delay of the "head" of the algorithm
    if delay == -1: # defaults to 10 milliseconds
        delay = 10
    global gridSize
    gridSize = int(input("Enter Grid Size: ")) # gets user to input grid size (n * n)
    while gridSize < 2 or coordinateOffset(gridSize) + heights[0] / 1920 * 80 > heights[0]: # checks if grid will fit in screen or if grid is 1 * 1 or lower
        print("Entered input is invalid. ")
        gridSize = int(input("Enter Grid Size: "))
    global consoleSize
    consoleSize = coordinateOffset(gridSize) # gets console pixel size based on grid size
    global blockColor
    blockColor = colorInput("Enter block color (Enter p to print all available colors): ") # gets block colors
    global borderColor
    borderColor = colorInput("Enter border color (Enter p to print all available colors): ") # gets border colors
    global trackerColor
    trackerColor = colorInput("Enter tracker color (Enter p to print all available colors): ") # gets color for "head" of the algorithm
    pygame.init() # initializes pygame module
    global console
    console = pygame.display.set_mode((consoleSize, consoleSize)) # sets up console

# event handler to check if user clicks red x to exit, and exits if so
def checkForExit():
    pygame.event.pump()
    for action in pygame.event.get():
        if action.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

# class to handle maze generation
class Maze:
    # class constructor
    def __init__(self, _gridSize, _coordinates):
        # sets private variables
        self._gridSize = _gridSize
        self._coordinates = _coordinates
        self._gridArea = self._gridSize ** 2
        self._stack, self._solutionStack = deque(), deque() # uses deque (double ended queue) as a stack data structure
        self._visited = full((self._gridSize, self._gridSize), False) # stores points that have been visited
        self._stack.append(self._coordinates[0]) # adds start coordinate to stack
        self._solutionStack.append(self._coordinates[0]) # adds start coordinate to solution stack
        self._visited[self._coordinates[0][0]][self._coordinates[0][1]] = True # marks start coordinate as visited
        self._visitedCount = 1 # stores coordinates visited, so application does not have to traverse all of visited to access the coordinate (time-complexity > space-complexity in this instance)

    # clears the border between two coordinates
    @staticmethod
    def _clearPath(first, second, color, offset=0):
        start = Rect(coordinateOffset(first[0]) + offset, coordinateOffset(first[1]) + offset, side - 2 * offset, side - 2 * offset)
        end = Rect(coordinateOffset(second[0]) + offset, coordinateOffset(second[1]) + offset, side - 2 * offset, side - 2 * offset)
        pygame.draw.rect(console, color, start.union(end))


    # updates head/tracker so user can easily tell where the algorithm is in its progress
    @staticmethod
    def _updateTracker(first, second):
        pygame.draw.rect(console, blockColor, (coordinateOffset(first[0]), coordinateOffset(first[1]), side, side)) # covers old coordinate with block color
        pygame.draw.rect(console, trackerColor, (coordinateOffset(second[0]), coordinateOffset(second[1]), side, side)) # sets new coordinate as tracker color

    # finds all unvisited neighbors of a coordinate
    def _findNeighbors(self):
        neighbors = [] # list of neighbors
        top = self._stack[-1] # grabs top of stack
        if top[0] > 0 and not self._visited[top[0] - 1][top[1]]:
            neighbors.append((top[0] - 1, top[1]))
        if top[0] < self._gridSize - 1 and not self._visited[top[0] + 1][top[1]]:
            neighbors.append((top[0] + 1, top[1]))
        if top[1] > 0 and not self._visited[top[0]][top[1] - 1]:
            neighbors.append((top[0], top[1] - 1))
        if top[1] < self._gridSize - 1 and not self._visited[top[0]][top[1] + 1]:
            neighbors.append((top[0], top[1] + 1))
        return neighbors # returns all unvisited valid neighbors in a list

    # moves from one coordinate to another
    def _moveTo(self, _pair):
        top = self._stack[-1] # grabs top of stack
        self._stack.append((_pair[0], _pair[1])) # adds new coordinate to stack
        self._visited[_pair[0]][_pair[1]] = True # marks new coordinate as visited
        self._visitedCount += 1 # increments visited count
        pygame.time.delay(delay) # delays if necessary
        self._clearPath(top, _pair, blockColor) # clears path from old coordinate to new coordinate
        self._updateTracker(top, _pair) # sets new coordinate as head/tracker
        pygame.display.set_caption("APCSP Create - Maze Generation Status: " + "%0.2f" % (self._visitedCount / self._gridArea * 100) + "%") # updates window caption
        pygame.display.update()

    # visits all unvisited neighbors of coordinate in a random order
    def visitNeighbors(self):
        pygame.display.set_caption("APCSP Create - Maze Generation Status: 0.00%") # sets caption
        while self._visitedCount != self._gridArea: # while every coordinate hasn't been visited
            neighbors = self._findNeighbors() # gets neighbors of current coordinate
            if len(neighbors) != 0: # checks if there is at least one neighbor
                randNeighbor = choice(neighbors) # chooses a random neighbor
                self._moveTo(randNeighbor) # moves current coordinate to be the new coordinate
                if self._solutionStack[-1] != self._coordinates[1]: # if solution hasn't been found yet, new coordinate will be a part of the solution
                    self._solutionStack.append(randNeighbor)
            else: # backtracks to last node
                top = self._stack[-1] # grabs top of stack
                self._stack.pop() # remove coordinate from stack
                self._updateTracker(top, self._stack[-1]) # sets head/trackker as last coordinate
                if self._solutionStack[-1] != self._coordinates[1]:  # if solution hasn't been found yet, coordinate has to be removed
                    self._solutionStack.pop()
            pygame.display.set_caption("APCSP Create - Maze Generation Status: " + "%0.2f" % (self._visitedCount / self._gridArea * 100) + "%") # updates window caption
            checkForExit() # checks if player exits

    # uses solution stack to display solution
    def traverseSolution(self):
        pygame.draw.rect(console, blockColor, (coordinateOffset(self._stack[-1][0]), coordinateOffset(self._stack[-1][1]), side, side)) # removes old tracker
        pygame.display.update()
        pygame.display.set_caption("APCSP Create - Maze Solution Status: 0.00%") # updates window caption
        originalSize = len(self._solutionStack) # gets amount of coordinates in solution so that percent completed can be generated
        self._solutionStack.reverse() # reverses stack, as top would be the solution starting
        offset = int(border * 3) # offsets size of block so solution is clearly visible
        if originalSize == 1: # if start coordinate and end coordinate were the same
            pygame.draw.rect(console, trackerColor, (coordinateOffset(self._solutionStack[-1][0]) + offset, coordinateOffset(self._solutionStack[-1][1]) + offset, side - 2 * offset, side - 2 * offset))
            self._solutionStack.pop() # removes top of stack
            pygame.display.set_caption("APCSP Create - Maze Solution Status: " + "%0.2f" % ((1 - (len(self._solutionStack)) / originalSize) * 100) + "%") # updates window caption
            pygame.display.update()
        firstCoordinate = False
        while len(self._solutionStack) > 0:
            pygame.time.delay(delay) # delays if necessary
            top = self._solutionStack[-1] # grabs top of stack
            self._solutionStack.pop() # removes top of stack
            self._clearPath(top, self._solutionStack[-1], trackerColor, offset) # draws path from old coordinate to new coordinate
            if firstCoordinate is False or len(self._solutionStack) == 1: # if element is first or last element
                if len(self._solutionStack) == 1:
                    top = self._solutionStack[-1]
                    self._solutionStack.pop()
                pygame.draw.rect(console, trackerColor, (coordinateOffset(top[0]), coordinateOffset(top[1]), side, side))
                pygame.draw.rect(console, blockColor, (coordinateOffset(top[0]) + offset, coordinateOffset(top[1]) + offset, side - 2 * offset, side - 2 * offset))
                firstCoordinate = True
            pygame.display.set_caption("APCSP Create - Maze Solution Status: " + "%0.2f" % ((1 - (len(self._solutionStack)) / originalSize) * 100) + "%") # updates window caption
            pygame.display.update()
            checkForExit()

# main function to setup everything and get other needed inputs
def main():
    initialize() # calls initialize function
    pygame.draw.rect(console, borderColor, (0, 0, coordinateOffset(gridSize), coordinateOffset(gridSize))) # fills screen with border color
    for i in range(gridSize):
        for j in range(gridSize):
            pygame.draw.rect(console, blockColor, (coordinateOffset(i), coordinateOffset(j), side, side)) # adds blocks on top of border color
    pygame.display.update() # updates display, otherwise the console would stay blank
    coordinates = [] # coordinates of maze's start and end point
    for i in range(2):
        if i == 0:
            text = "LEFT CLICK THE GENERATION/SOLUTION STARTING POINT"
        else:
            text = "LEFT CLICK THE SOLUTION ENDING POINT"
        pygame.display.set_caption(text) # sets text as window caption
        print(text) # prints text to console
        finding = False # checks if coordinate was pressed
        # event handler
        while finding is False:
            pygame.event.pump() # adds "fake" events to the queue, so that the application does not think it has froze
            for action in pygame.event.get():
                if action.type == pygame.QUIT: # checks if user clicks red x to exit, and exits if so
                    pygame.quit()
                    sys.exit()
                elif action.type == MOUSEBUTTONDOWN: # checks if user clicked a point, and takes the floor of the x and y, so that the top right of the block is still considered part of the block
                    pair = pygame.mouse.get_pos()
                    x = int(floor(coordinateOffset(pair[0], True)))
                    y = int(floor(coordinateOffset(pair[1], True)))
                    coordinates.append((x, y)) # adds to coordinates
                    finding = True
                    break
    maze = Maze(gridSize, coordinates) # initializes object with grid size and coordinates
    maze.visitNeighbors() # generates maze
    maze.traverseSolution() # solves maze from selected start point to selected end point
    # checks if user clicks red x to exit, and exits if so
    while True:
        checkForExit()

# calls main
if __name__ == '__main__':
    main()
