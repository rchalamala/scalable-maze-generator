#!/usr/bin/env python3

from collections import deque
from numpy import floor, full
import pygame
from pygame import Rect, MOUSEBUTTONDOWN
from random import choice
from screeninfo import get_monitors
from sys import exit

delay = 10

heights = []
for m in get_monitors():
    heights.append(int(str(m)[str(m).find("height="):].split(',', 1)[0][7:]))

side = max(int(heights[0] // 100 * 1.5), 30)
border = int(max(side / 10, 1))

def coordinateOffset(operand, input = False):
    if input is False:
        return int(operand * (side + border) + border)
    else:
        return (operand - border) / (side + border)

gridSize = int(input("Enter Grid Size: "))
while gridSize < 2 or coordinateOffset(gridSize) + heights[0] / 1920 * 80 > heights[0]:
    print("Entered input is invalid. ")
    gridSize = int(input("Enter Grid Size: "))
consoleSize = coordinateOffset(gridSize)

colorKeys = list(pygame.color.THECOLORS.keys())
colorKeys.sort()

def printColors():
    for key in colorKeys:
        print(key)

colors = []

def colorInput(text):
    color = input(text).lower()
    while color == "p":
        printColors()
        color = input(text).lower()
    while color not in pygame.color.THECOLORS or color in colors:
        print("Entered input is invalid. ")
        color = input(text).lower()
        while color == "p":
            printColors()
            color = input(text).lower()
    colors.append(color)
    return pygame.color.THECOLORS[color]

blockColor = colorInput("Enter block color (Enter p to print all available colors): ")
borderColor = colorInput("Enter border color (Enter p to print all available colors): ")
trackerColor = colorInput("Enter tracker color (Enter p to print all available colors): ")

def checkForExit():
    pygame.event.pump()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

pygame.init()
console = pygame.display.set_mode((consoleSize, consoleSize))

class Maze:
    def __init__(self, gridSize, coordinates):
        self._gridSize = gridSize
        self._coordinates = coordinates
        self._gridArea = self._gridSize ** 2;
        self._stack, self._solutionStack = deque(), deque()
        self._visited = full((self._gridSize, self._gridSize), False)
        self._stack.append(self._coordinates[0])
        self._solutionStack.append(self._coordinates[0])
        self._visited[self._coordinates[0][0]][self._coordinates[0][1]] = True
        self._visitedCount = 1
    @staticmethod
    def _clearPath(first, second, color, offset = 0):
        start = Rect(coordinateOffset(first[0]) + offset, coordinateOffset(first[1]) + offset, side - 2 * offset, side - 2 * offset)
        end = Rect(coordinateOffset(second[0]) + offset, coordinateOffset(second[1]) + offset, side - 2 * offset, side - 2 * offset)
        pygame.draw.rect(console, color, start.union(end))
    @staticmethod
    def _updateTracker(first, second):
        pygame.draw.rect(console, blockColor, (coordinateOffset(first[0]), coordinateOffset(first[1]), side, side))
        pygame.draw.rect(console, trackerColor, (coordinateOffset(second[0]), coordinateOffset(second[1]), side, side))
    def _findNeighbors(self):
        neighbors = []
        top = self._stack[-1]
        if top[0] > 0 and not self._visited[top[0] - 1][top[1]]:
            neighbors.append((top[0] - 1, top[1]))
        if top[0] < self._gridSize - 1 and not self._visited[top[0] + 1][top[1]]:
            neighbors.append((top[0] + 1, top[1]))
        if top[1] > 0 and not self._visited[top[0]][top[1] - 1]:
            neighbors.append((top[0], top[1] - 1))
        if top[1] < self._gridSize - 1 and not self._visited[top[0]][top[1] + 1]:
            neighbors.append((top[0], top[1] + 1))
        return neighbors
    def _moveTo(self, pair):
        top = self._stack[-1]
        self._stack.append((pair[0], pair[1]))
        self._visited[pair[0]][pair[1]] = True
        self._visitedCount += 1
        pygame.time.delay(delay)
        self._clearPath(top, pair, blockColor)
        self._updateTracker(top, pair)
        pygame.display.set_caption("Rahul Chalamala - APCSP Create - Maze Generation Status: " + "%0.2f" % (self._visitedCount / self._gridArea * 100) + "%")
        pygame.display.update()
    def visitNeighbors(self):
        pygame.display.set_caption("Rahul Chalamala - APCSP Create - Maze Generation Status: 0.00%")
        while self._visitedCount != self._gridArea:
            neighbors = self._findNeighbors()
            if len(neighbors) != 0:
                randNeighbor = choice(neighbors)
                self._moveTo(randNeighbor)
                if self._solutionStack[-1] != coordinates[1]:
                    self._solutionStack.append(randNeighbor)
            else:
                top = self._stack[-1]
                self._stack.pop()
                self._updateTracker(top, self._stack[-1])
                if self._solutionStack[-1] != coordinates[1]:
                    self._solutionStack.pop()
            pygame.display.set_caption("Rahul Chalamala - APCSP Create - Maze Generation Status: " + "%0.2f" % (self._visitedCount / self._gridArea * 100) + "%")
            checkForExit()


    def traverseSolution(self):
        pygame.draw.rect(console, blockColor, (coordinateOffset(maze._stack[-1][0]), coordinateOffset(maze._stack[-1][1]), side, side))
        pygame.display.update()
        pygame.display.set_caption("Rahul Chalamala - APCSP Create - Maze Solution Status: 0.00%")
        originalSize = len(self._solutionStack)
        self._solutionStack.reverse()
        offset = int(border * 3)
        if originalSize == 1:
            pygame.draw.rect(console, trackerColor, (coordinateOffset(self._solutionStack[-1][0]) + offset, coordinateOffset(self._solutionStack[-1][1]) + offset, side - 2 * offset, side - 2 * offset))
            self._solutionStack.pop()
            pygame.display.set_caption("Rahul Chalamala - APCSP Create - Maze Solution Status: " + "%0.2f" % ((1 - (len(self._solutionStack)) / originalSize) * 100) + "%")
            pygame.display.update()
        firstCoordinate = False
        while len(self._solutionStack) > 0:
            pygame.time.delay(delay)
            top = self._solutionStack[-1]
            self._solutionStack.pop()
            self._clearPath(top, self._solutionStack[-1], trackerColor, offset)
            if firstCoordinate is False or len(self._solutionStack) == 1:
                if len(self._solutionStack) == 1:
                    top = self._solutionStack[-1]
                    self._solutionStack.pop()
                pygame.draw.rect(console, trackerColor, (coordinateOffset(top[0]), coordinateOffset(top[1]), side, side))
                pygame.draw.rect(console, blockColor, (coordinateOffset(top[0]) + offset, coordinateOffset(top[1]) + offset, side - 2 * offset, side - 2 * offset))
                firstCoordinate = True
            pygame.display.set_caption("Rahul Chalamala - APCSP Create - Maze Solution Status: " + "%0.2f" % ((1 - (len(self._solutionStack)) / originalSize) * 100) + "%")
            pygame.display.update()
            checkForExit()

pygame.draw.rect(console, borderColor, (0, 0, coordinateOffset(gridSize), coordinateOffset(gridSize)))
print("running")
for i in range(gridSize):
    for j in range(gridSize):
        pygame.draw.rect(console, blockColor, (coordinateOffset(i), coordinateOffset(j), side, side))
pygame.display.update()

coordinates = []

for i in range(2):
    if i == 0:
        text = "LEFT CLICK THE GENERATION/SOLUTION STARTING POINT"
    else:
        text = "LEFT CLICK THE SOLUTION ENDING POINT"
    pygame.display.set_caption(text)
    finding = False
    while finding is False:
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == MOUSEBUTTONDOWN:
                pair = pygame.mouse.get_pos()
                x = int(floor(coordinateOffset(pair[0], True)))
                y = int(floor(coordinateOffset(pair[1], True)))
                coordinates.append((x, y))
                finding = True
                break

maze = Maze(gridSize, coordinates)

maze.visitNeighbors()
maze.traverseSolution()

while True:
    checkForExit()
