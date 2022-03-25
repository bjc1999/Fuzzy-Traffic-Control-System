import numpy as np
import skfuzzy as fuzz
from src.Config import Config


class Fuzzy:

    def __init__(self):
        setting = Config['fuzzy']['range']
        self.x_behind_red_light = setting['behind_red_light']
        self.x_arriving_green_light = setting['arriving_green_light']
        self.x_extension = setting['extension']

        setting = Config['fuzzy']['membership_function']['arriving_green_light']
        self.arriving_green_light_few = fuzz.trimf(self.x_arriving_green_light, setting['few'])
        self.arriving_green_light_small = fuzz.trimf(self.x_arriving_green_light, setting['small'])
        self.arriving_green_light_medium = fuzz.trimf(self.x_arriving_green_light, setting['medium'])
        self.arriving_green_light_many = fuzz.trimf(self.x_arriving_green_light, setting['many'])

        setting = Config['fuzzy']['membership_function']['behind_red_light']
        self.behind_red_light_few = fuzz.trimf(self.x_behind_red_light, setting['few'])
        self.behind_red_light_small = fuzz.trimf(self.x_behind_red_light, setting['small'])
        self.behind_red_light_medium = fuzz.trimf(self.x_behind_red_light, setting['medium'])
        self.behind_red_light_many = fuzz.trimf(self.x_behind_red_light, setting['many'])

        setting = Config['fuzzy']['membership_function']['extension']
        self.extension_zero = fuzz.trimf(self.x_extension, setting['zero'])
        self.extension_short = fuzz.trimf(self.x_extension, setting['short'])
        self.extension_medium = fuzz.trimf(self.x_extension, setting['medium'])
        self.extension_long = fuzz.trimf(self.x_extension, setting['long'])

    def get_extension(self, arriving_green_light_car, behind_red_light_car, extension_count):
        behind_red_light_level_few = fuzz.interp_membership(self.x_behind_red_light, self.behind_red_light_few, behind_red_light_car)
        behind_red_light_level_small = fuzz.interp_membership(self.x_behind_red_light, self.behind_red_light_small, behind_red_light_car)
        behind_red_light_level_medium = fuzz.interp_membership(self.x_behind_red_light, self.behind_red_light_medium, behind_red_light_car)
        behind_red_light_level_many = fuzz.interp_membership(self.x_behind_red_light, self.behind_red_light_many, behind_red_light_car)

        arriving_green_light_level_few = fuzz.interp_membership(self.x_arriving_green_light, self.arriving_green_light_few, arriving_green_light_car)
        arriving_green_light_level_small = fuzz.interp_membership(self.x_arriving_green_light, self.arriving_green_light_small, arriving_green_light_car)
        arriving_green_light_level_medium = fuzz.interp_membership(self.x_arriving_green_light, self.arriving_green_light_medium, arriving_green_light_car)
        arriving_green_light_level_many = fuzz.interp_membership(self.x_arriving_green_light, self.arriving_green_light_many, arriving_green_light_car)

        # Rules:
        # Rule 1: If Arrival is few then Extension is zero.
        # Rule 2: If Arrival is small then Extension is short.
        # Rule 3: If Arrival is medium AND Queuse is (few OR small) then Extension is long.
        # Rule 4: If Arrival is medium AND Queue is medium then Extension is medium.
        # Rule 5: If Arrival is medium AND Queue is many then Extension is short.
        # Rule 6: If Arrival is many AND Queuse is (few OR small OR medium) then Extension is long.
        # Rule 7: If Arrival is many AND Queue is many then Extension is medium.      
        
        rule1 = arriving_green_light_level_few
        rule2 = arriving_green_light_level_small
        rule3 = np.fmin(arriving_green_light_level_medium,
                        np.fmax(behind_red_light_level_few, behind_red_light_level_small))
        rule4 = np.fmin(arriving_green_light_level_medium, behind_red_light_level_medium)
        rule5 = np.fmin(arriving_green_light_level_medium, behind_red_light_level_many)
        rule6 = np.fmin(arriving_green_light_level_many,
                        np.fmax(behind_red_light_level_few, np.fmax(behind_red_light_level_small, behind_red_light_level_medium)))
        rule7 = np.fmin(arriving_green_light_level_many, behind_red_light_level_many)
        
        extension_activation_zero = np.fmin(rule1, self.extension_zero)
        extension_activation_short = np.fmin(np.fmax(rule2, rule5), self.extension_short)
        extension_activation_medium = np.fmin(np.fmax(rule4, rule7), self.extension_medium)
        extension_activation_long = np.fmin(np.fmax(rule3, rule6), self.extension_long)

        aggregated = np.fmax(extension_activation_zero, np.fmax(extension_activation_short,
                                                                np.fmax(extension_activation_medium,
                                                                        extension_activation_long)))

        return fuzz.defuzz(self.x_extension, aggregated, 'centroid')
