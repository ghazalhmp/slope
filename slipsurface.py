# -*- coding: utf-8 -*-
"""
Created on Sun Apr 16 17:13:32 2023

@author: arshansystem
"""

class SlipSurface:
    def __init__(self, size_x, size_y, x_center_circle, y_center_circle, radius):
        self.size_x = size_x
        self.size_y = size_y
        # self.x_center_circle = random.randint(10, self.size_x)
        self.x_center_circle = x_center_circle
        self.y_center_circle = y_center_circle
        # self.y_center_circle = random.randint(0, self.size_y)
        self.radius = radius
