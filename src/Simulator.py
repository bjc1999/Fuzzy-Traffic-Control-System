import pygame
import time

from src.Common import Lane, DoubleLane
from src.Config import Config
from src.Controller.VehicleController import VehicleController
from src.Controller.TrafficController import TrafficController
from src.Controller.BackgroundController import BackgroundController
from src.Wang_Mendel import Mangami, predict


class Simulator:
    def __init__(self, caption):
        self.caption = caption
        self.surface = pygame.display.set_mode((Config['simulator']['screen_width'],
                                                Config['simulator']['screen_height']))
        self.vehicle_ctrl = VehicleController(self.surface)
        self.traffic_ctrl = TrafficController(self.surface)
        self.background_ctrl = BackgroundController(self.surface,
                                                    self.traffic_ctrl.get_traffic_lights(DoubleLane.Horizontal) +
                                                    self.traffic_ctrl.get_traffic_lights(DoubleLane.Vertical))
        self.clock = pygame.time.Clock()
        self.gap_between_switch = Config['simulator']['gap_between_traffic_switch']

        self.L2R_SPAWN_EVENT = pygame.USEREVENT + 1
        self.T2B_SPAWN_EVENT = pygame.USEREVENT + 2
        self.R2L_SPAWN_EVENT = pygame.USEREVENT + 3
        self.B2T_SPAWN_EVENT = pygame.USEREVENT + 4

        self.switching_traffic = False
        self.switching_traffic_start_time = None
        self.start_time = time.time()
        self.moving_averages = self.vehicle_ctrl.get_moving_averages_num_vehicles_behind_traffic()

        self.is_extended = False
        self.green_light_remaining_time = Config['traffic_light']['green_light_duration']
        self.extension_notification_start_time = time.time() - 10
        Mangami(True)

    def spawn(self, lane: Lane):
        self.spawn_single_vehicle(lane)

    def spawn_single_vehicle(self, lane: Lane):
        self.vehicle_ctrl.create_vehicle(lane, self.traffic_ctrl.traffic_lights[lane])

    def main_loop(self):
        game_over = False

        pygame.time.set_timer(self.L2R_SPAWN_EVENT, Config['simulator']['spawn_rate']['medium'])
        pygame.time.set_timer(self.T2B_SPAWN_EVENT, Config['simulator']['spawn_rate']['medium'])
        pygame.time.set_timer(self.R2L_SPAWN_EVENT, Config['simulator']['spawn_rate']['medium'])
        pygame.time.set_timer(self.B2T_SPAWN_EVENT, Config['simulator']['spawn_rate']['medium'])

        while not game_over:

            for event in pygame.event.get():
                if event.type == self.L2R_SPAWN_EVENT:
                    rate = self.background_ctrl.get_spawn_rate(Lane.left_to_right)
                    pygame.time.set_timer(self.L2R_SPAWN_EVENT, Config['simulator']['spawn_rate'][rate])
                    self.spawn(Lane.left_to_right)

                if event.type == self.T2B_SPAWN_EVENT:
                    rate = self.background_ctrl.get_spawn_rate(Lane.top_to_bottom)
                    pygame.time.set_timer(self.T2B_SPAWN_EVENT, Config['simulator']['spawn_rate'][rate])
                    self.spawn(Lane.top_to_bottom)

                if event.type == self.R2L_SPAWN_EVENT:
                    rate = self.background_ctrl.get_spawn_rate(Lane.right_to_left)
                    pygame.time.set_timer(self.R2L_SPAWN_EVENT, Config['simulator']['spawn_rate'][rate])
                    self.spawn(Lane.right_to_left)

                if event.type == self.B2T_SPAWN_EVENT:
                    rate = self.background_ctrl.get_spawn_rate(Lane.bottom_to_top)
                    pygame.time.set_timer(self.B2T_SPAWN_EVENT, Config['simulator']['spawn_rate'][rate])
                    self.spawn(Lane.bottom_to_top)

                if event.type == pygame.QUIT:
                    game_over = True

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for lane in [Lane.left_to_right, Lane.top_to_bottom, Lane.right_to_left, Lane.bottom_to_top]:
                        for rate in ['slow', 'medium', 'fast']:
                            if self.background_ctrl.spawn_rate_buttons[lane][rate].collidepoint(event.pos):
                                self.background_ctrl.set_spawn_rate(lane, rate)

            self.background_ctrl.refresh_screen()
            self.background_ctrl.draw_road_markings()
            self.background_ctrl.draw_vehicle_count(self.vehicle_ctrl.counter)
            self.background_ctrl.draw_spawn_rate_buttons()
            self.background_ctrl.draw_light_durations(self.traffic_ctrl.get_green_light_extension())

            direction_changed = self.traffic_ctrl.update_and_draw_traffic_lights()
            self.vehicle_ctrl.destroy_vehicles_outside_canvas()
            self.vehicle_ctrl.update_and_draw_vehicles()
            self.vehicle_ctrl.update_num_vehicles_behind_traffic()

            if round((time.time() - self.start_time), 1) % Config['simulator']['static_duration'] == 0:
                self.moving_averages = self.vehicle_ctrl.get_moving_averages_num_vehicles_behind_traffic()
            self.background_ctrl.draw_moving_averages(self.moving_averages)

            if direction_changed:
                self.traffic_ctrl.clear_all_green_light_extension()
                fuzzy_score = self.calculate_fuzzy_score(self.moving_averages)
                self.l2r = self.moving_averages[Lane.left_to_right]
                self.t2b = self.moving_averages[Lane.top_to_bottom]
                self.r2l = self.moving_averages[Lane.right_to_left]
                self.b2t = self.moving_averages[Lane.bottom_to_top]
                self.traffic_ctrl.set_green_light_extension(fuzzy_score)
                self.extension_notification_start_time = time.time()

            if time.time() - self.extension_notification_start_time < Config['simulator']['fuzzy_notification_duration']:
                self.background_ctrl.draw_extension_notification(self.traffic_ctrl.get_green_light_extension(), self.traffic_ctrl.get_current_active_lane(), [self.l2r, self.t2b, self.r2l, self.b2t])

            pygame.display.update()
            self.clock.tick(Config['simulator']['frame_rate'])

    def calculate_fuzzy_score(self, moving_averages):
        traffic_state = self.traffic_ctrl.get_current_active_lane()
            
        if traffic_state == Lane.left_to_right:
            return predict([[moving_averages[Lane.left_to_right]], [moving_averages[Lane.top_to_bottom]+moving_averages[Lane.right_to_left]+moving_averages[Lane.bottom_to_top]]])
        elif traffic_state == Lane.top_to_bottom:
            return predict([[moving_averages[Lane.top_to_bottom]], [moving_averages[Lane.left_to_right]+moving_averages[Lane.right_to_left]+moving_averages[Lane.bottom_to_top]]])
        elif traffic_state == Lane.right_to_left:
            return predict([[moving_averages[Lane.right_to_left]], [moving_averages[Lane.left_to_right]+moving_averages[Lane.top_to_bottom]+moving_averages[Lane.bottom_to_top]]])
        elif traffic_state == Lane.bottom_to_top:
            return predict([[moving_averages[Lane.bottom_to_top]], [moving_averages[Lane.left_to_right]+moving_averages[Lane.right_to_left]+moving_averages[Lane.top_to_bottom]]])

    def initialize(self):
        self.spawn(Lane.left_to_right)
        self.spawn(Lane.top_to_bottom)
        self.spawn(Lane.right_to_left)
        self.spawn(Lane.bottom_to_top)

    def start(self):
        pygame.init()
        pygame.display.set_caption(self.caption)

        self.initialize()
        self.main_loop()

        pygame.quit()
        quit()
