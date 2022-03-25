import time
from src.Common import TrafficStatus, Lane
from src.Config import Config
import pygame


class TrafficLight:
    def __init__(self, x, y, lane, images, surface, status=TrafficStatus.green):
        self.x = x
        self.y = y
        self.lane = lane
        self.images = images  # expected to be dictionary with TrafficStatus as keys
        self.surface = surface
        self.duration = {
            TrafficStatus.green: Config['traffic_light']['green_light_duration'],
            TrafficStatus.red: Config['traffic_light']['red_light_duration'],
            TrafficStatus.yellow: Config['traffic_light']['yellow_light_duration']
        }
        self.duration_extension = {
            TrafficStatus.green: 0,
            TrafficStatus.red: 0,
            TrafficStatus.yellow: 0
        }
        self.start_time = {
            TrafficStatus.green: time.time(),
            TrafficStatus.red: time.time(),
            TrafficStatus.yellow: time.time()
        }
        self.status = status
        if lane == Lane.right_to_left:
            self.factor = 2
        elif lane == Lane.bottom_to_top:
            self.factor = 3
        else:
            self.factor = 1

    @property
    def center_x(self):
        return self.x + self.width / 2

    @property
    def center_y(self):
        return self.y + self.height / 2

    @property
    def width(self):
        return Config['traffic_light']['body_width']

    @property
    def height(self):
        return Config['traffic_light']['body_height']

    def draw(self):
        self.surface.blit(self.images[self.status], (self.x, self.y))

    def change_status(self, status: TrafficStatus):
        self.status = status
        self.start_time[self.status] = time.time()

    def auto_update(self, green_lane: Lane):
        over_time = (self.duration[self.status] * self.factor + self.duration_extension[self.status]) - \
                    (time.time() - self.start_time[self.status])

        to_change_status = over_time < 0

        new_status = None

        if to_change_status: 
            if self.status == TrafficStatus.green:
                self.status = TrafficStatus.yellow
                new_status = TrafficStatus.yellow
                self.factor = 1
            elif self.status == TrafficStatus.yellow:
                self.status = TrafficStatus.red
                new_status = TrafficStatus.red
                self.factor = 3
            elif self.status == TrafficStatus.red:
                # if opposite is red, do not update
                if green_lane != self.lane:
                    return
                if abs(over_time) < Config['simulator']['gap_between_traffic_switch']:
                    return
                self.status = TrafficStatus.green
                new_status = TrafficStatus.green
                self.factor = 1
                self.duration_extension[TrafficStatus.red] = 0
            self.start_time[self.status] = time.time()

        return new_status

    def draw_countdown(self):
        font = pygame.font.SysFont('Comic Sans MS', 12, True)
        countdown = (self.duration[self.status] * self.factor + self.duration_extension[self.status]) - (time.time() - self.start_time[self.status])
        if countdown < 0: 
            countdown = 0.0
        text_color = Config['colors']['black']
        if self.status == TrafficStatus.green:
            text_color = Config['colors']['traffic_green']
        elif self.status == TrafficStatus.yellow:
            text_color = Config['colors']['traffic_yellow']
        elif self.status == TrafficStatus.red:
            text_color = Config['colors']['traffic_red']
        text_surface = font.render('{}'.format(round(countdown, 1)), True, text_color)
        pos_x = self.x
        pos_y = self.y
        if self.lane == Lane.left_to_right:
            pos_y = self.y - self.height
        elif self.lane == Lane.right_to_left:
            pos_y = self.y + self.height*5/4
        elif self.lane == Lane.top_to_bottom:
            pos_x = self.x + self.width*2
        elif self.lane == Lane.bottom_to_top:
            pos_x = self.x - self.width*2
        self.surface.blit(text_surface, (pos_x, pos_y))

    def set_green_light_extension(self, extension):
        self.duration_extension[TrafficStatus.green] = extension

    def set_red_light_extension(self, extension):
        extension = -8.5 if extension < -8.5 else extension
        if self.duration_extension[TrafficStatus.red] != 0:
            self.duration_extension[TrafficStatus.red] += extension
        else:
            self.duration_extension[TrafficStatus.red] = extension

    def get_green_light_remaining_time(self):
        return (self.duration[self.status] * self.factor + self.duration_extension[self.status]) - (time.time() - self.start_time[self.status])
