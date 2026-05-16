import pygame
import io
from time import sleep
from sys import exit

class Player:
    def __init__(self, name, x, y, facing):
        self.name = name
        self.location = (x, y)
        self.facing = facing
    
    def move(self, direction):
        if direction == "forward":
            if self.facing == "north" and self.location[1] > 0:
                self.location[1] -= 1
            elif self.facing == "south" and self.location[1] < 9:
                self.location[1] += 1
            elif self.facing == "east" and self.location[0] < 9:
                self.location[0] += 1
            elif self.facing == "west" and self.location[0] > 0:
                self.location[0] -= 1
        elif direction == "backward":
            if self.facing == "north" and self.location[1] < 9:
                self.location[1] += 1
            elif self.facing == "south" and self.location[1] > 0:
                self.location[1] -= 1
            elif self.facing == "east" and self.location[0] > 0:
                self.location[0] -= 1
            elif self.facing == "west" and self.location[0] < 9:
                self.location[0] += 1
    
    def turn(self, turnDirection):
        if turnDirection == "left":
            if self.facing == "north":
                self.facing = "west"
            elif self.facing == "south":
                self.facing = "east"
            elif self.facing == "east":
                self.facing = "north"
            elif self.facing == "west":
                self.facing = "south"
        elif turnDirection == "right":
            if self.facing == "north":
                self.facing = "east"
            elif self.facing == "south":
                self.facing = "west"
            elif self.facing == "east":
                self.facing = "south"
            elif self.facing == "west":
                self.facing = "north"