import numpy as np

Config = {
    'vehicle': {
        'speed': 3,
        'safe_distance': 5,
        'body_length': 25,
        'body_width': 15,
        'safe_spawn_factor': 1.1
    },
    'simulator': {
        'screen_width': 800,
        'screen_height': 800,
        'bumper_distance': 5,
        'spawn_rate': {
            'fast': 3000,  # millisecond
            'medium': 14000,  # millisecond
            'slow': 14000000,  # millisecond
        },
        'frame_rate': 30,
        'gap_between_traffic_switch': 0,  # second
        'moving_averages_period': 1,  # second
        'static_duration': 1,  # second
        'seconds_before_extension': 1,  # second
        'fuzzy_notification_duration': 5  #second
    },
    'colors': {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'dark_gray': (169, 169, 169),
        'traffic_yellow': (250, 210, 1),
        'traffic_green': (34, 139, 94),
        'traffic_red': (184, 29, 19),
        'red': (255, 0, 0),
        'yellow': (255, 255, 0),
        'green': (0, 255, 0)
    },
    'traffic_light': {
        'red_light_duration': 10,  # second
        'yellow_light_duration': 1.5,  # second
        'green_light_duration': 8.5,  # second
        'distance_from_center': (40, 10),
        'body_height': 30,
        'body_width': 20
    },
    'background': {
        'road_marking_width': 2,
        'road_marking_alternate_lengths': (20, 10),
        'road_marking_gap_from_yellow_box': 10,
        'yellow_box_junction': (50, 50, 50, 50),  # top, right, bottom, left
    },
    'fuzzy': {
        'range': {
            'behind_red_light': np.arange(0, 34.1, 0.1),
            'arriving_green_light': np.arange(0, 13, 1),
            'extension': np.arange(-8.5, 8.5, 0.5)
        },
        'membership_function': {
            'behind_red_light': {
                'few': [0, 0, 11.33],
                'small': [0, 11.33, 22.67],
                'medium': [11.33, 22.67, 34],
                'many': [22.67, 34, 34]
            },
            'arriving_green_light': {
                'few': [0, 0, 4],
                'small': [0, 4, 8],
                'medium': [4, 8, 12],
                'many': [8, 12, 12]
            },
            'extension': {
                'zero': [-8.5, -8.5, -3],
                'short': [-8.5, -3, 2.5],
                'medium': [-3, 2.5, 8],
                'long': [2.5, 8, 8]
            }
        }
    }
}
