import pygame

from src.Common import Direction, Lane, TrafficStatus
from src.Config import Config


class Vehicle:
    def __init__(self, x, y, lane:Lane, image, surface, traffic_light, direction, turning_point):
        if lane != traffic_light.lane:
            raise Exception('The lane of traffic light and vehicle must be same.')
        self.x = x
        self.y = y
        self.lane = lane
        if lane in [Lane.left_to_right, Lane.right_to_left]:
            self.image = pygame.transform.scale(image, (Config['vehicle']['body_length'], Config['vehicle']['body_width']))
        elif lane in [Lane.top_to_bottom, Lane.bottom_to_top]:
            self.image = pygame.transform.scale(image, (Config['vehicle']['body_width'], Config['vehicle']['body_length']))
        self.surface = surface
        self.traffic_light = traffic_light
        self.direction = direction
        self.turning_point = turning_point
        self.switched = False

    @property
    def center_x(self):
        return self.x + self.width / 2

    @property
    def center_y(self):
        return self.y + self.height / 2

    @property
    def width(self):
        return self.image.get_width()

    @property
    def height(self):
        return self.image.get_height()

    def draw(self):
        self.surface.blit(self.image, (self.x, self.y))
        self.switch_lane()

    def move(self, front_vehicle=None):
        safe_distance = Config['vehicle']['safe_distance']
        speed = Config['vehicle']['speed']
        stopping_non_green_light = self.traffic_light.status != TrafficStatus.green and self.is_behind_traffic_light()

        if self.lane == Lane.left_to_right:
            self.x += speed
            self.y += 0
            if front_vehicle and self.is_behind_traffic_light() and not self.switched:
                self.x = min(self.x, front_vehicle.x - safe_distance - self.width)
            if stopping_non_green_light:
                self.x = min(self.x, self.traffic_light.x - self.traffic_light.width/2 - self.width)

        elif self.lane == Lane.right_to_left:
            self.x -= speed
            self.y += 0
            if front_vehicle and self.is_behind_traffic_light() and not self.switched:
                self.x = max(self.x, front_vehicle.x + front_vehicle.width + safe_distance)
            if stopping_non_green_light:
                self.x = max(self.x, self.traffic_light.x + self.traffic_light.width*3/2)

        elif self.lane == Lane.bottom_to_top:
            self.x += 0
            self.y -= speed
            if front_vehicle and self.is_behind_traffic_light() and not self.switched:
                self.y = max(self.y, front_vehicle.y + front_vehicle.height + safe_distance)
            if stopping_non_green_light:
                self.y = max(self.y, self.traffic_light.y + self.traffic_light.height)

        elif self.lane == Lane.top_to_bottom:
            self.x += 0
            self.y += speed
            if front_vehicle and self.is_behind_traffic_light() and not self.switched:
                self.y = min(self.y, front_vehicle.y - safe_distance - self.height)
            if stopping_non_green_light:
                self.y = min(self.y, self.traffic_light.y - self.traffic_light.height/2 - self.height)

    def is_behind_traffic_light(self):
        if self.lane == Lane.left_to_right:
            return self.x + self.width <= self.traffic_light.x + self.traffic_light.width
        elif self.lane == Lane.right_to_left:
            return self.traffic_light.x + self.traffic_light.width <= self.x
        elif self.lane == Lane.bottom_to_top:
            return self.traffic_light.y <= self.y
        elif self.lane == Lane.top_to_bottom:
            return self.y + self.height <= self.traffic_light.y
        return False

    def inside_canvas(self) -> bool:
        return self.x >= 0 and \
                self.x + self.width <= Config['simulator']['screen_width'] and \
                self.y >= 0 and \
                self.y + self.height <= Config['simulator']['screen_height']

    def blitRotateCenter(self, angle):
        rotated_image = pygame.transform.rotate(self.image, angle)
        new_rect = rotated_image.get_rect(center = self.image.get_rect(topleft = (self.x, self.y)).center)

        self.surface.blit(rotated_image, new_rect)
        self.image = rotated_image
        self.x, self.y = new_rect[0], new_rect[1]
    
    def switch_lane(self):
        if self.lane in [Lane.left_to_right, Lane.right_to_left]:
            point = 0
        else:
            point = 1

        if self.direction == Direction.left:
            if ((self.lane in [Lane.left_to_right, Lane.top_to_bottom] and (self.center_x, self.center_y)[point] >= self.turning_point[point]) or
                (self.lane in [Lane.right_to_left, Lane.bottom_to_top] and (self.center_x, self.center_y)[point] <= self.turning_point[point])):
                self.blitRotateCenter(90)
                self.direction = Direction.forward
                if self.lane == Lane.left_to_right:
                    self.lane = Lane.bottom_to_top
                    self.x = self.turning_point[2]
                    self.draw()
                elif self.lane == Lane.right_to_left:
                    self.lane = Lane.top_to_bottom
                    self.x = self.turning_point[2]
                    self.draw()
                elif self.lane == Lane.bottom_to_top:
                    self.lane = Lane.right_to_left
                    self.y = self.turning_point[2]
                    self.draw()
                elif self.lane == Lane.top_to_bottom:
                    self.lane = Lane.left_to_right
                    self.y = self.turning_point[2]
                    self.draw()
                self.switched = True
        elif self.direction == Direction.right:
            if ((self.lane in [Lane.left_to_right, Lane.top_to_bottom] and (self.center_x, self.center_y)[point] >= self.turning_point[point]) or
                (self.lane in [Lane.right_to_left, Lane.bottom_to_top] and (self.center_x, self.center_y)[point] <= self.turning_point[point])):
                self.blitRotateCenter(-90)
                self.direction = Direction.forward
                if self.lane == Lane.left_to_right:
                    self.lane = Lane.top_to_bottom
                    self.x = self.turning_point[2]
                    self.draw()
                elif self.lane == Lane.right_to_left:
                    self.lane = Lane.bottom_to_top
                    self.x = self.turning_point[2]
                    self.draw()
                elif self.lane == Lane.bottom_to_top:
                    self.lane = Lane.left_to_right
                    self.y = self.turning_point[2]
                    self.draw()
                elif self.lane == Lane.top_to_bottom:
                    self.lane = Lane.right_to_left
                    self.y = self.turning_point[2]
                    self.draw()
                self.switched = True