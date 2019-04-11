#
# Light Color Controller
#
# Args:
#
import sys
import logging
import time
import datetime

import appdaemon.plugins.hass.hassapi as hass


LOG = logging.getLogger(__name__)

# Which lights to fade and how
# Format:
# GROUPS key: name of the `input_select`
#        value: List of tuples
#               ('light / group to change', 'type of light')
GROUPS = {
    'input_select.light_mode_livingroom': [
        ('group.livingroom_rgb_lights', 'rgb'),
        ('light.livingroom_spots_main', 'whitespectrum'),
    ],
    'input_select.light_mode_bedroom': [
        ('group.bedroom_lights', 'whitespectrum')
    ],
    'input_select.light_mode_bathroom': [
        ('group.bathroom_lights', 'whitespectrum'),
    ],
}

INVERSE_GROUPS = {}
for state, lights in GROUPS.items():
    for light, light_type in lights:
        INVERSE_GROUPS[light] = (state, light_type)


FOCUS = {
    'rgb': {
        'brightness': 255,
        'hs_color': [31.861, 37.369]
    },
    'whitespectrum': {
        'brightness': 254,
        'color_temp': 250
    }
}

EVERY_DAY = {
    'rgb': {
        'brightness': 203,
        'hs_color': [29.812, 65.252]
    },
    'whitespectrum': {
        'brightness': 235,
        'color_temp': 370
    }
}

EVENING = {
    'rgb': {
        'brightness': 50,
        'hs_color': [29.164, 80.271]
    },
    'whitespectrum': {
        'brightness': 100,
        'color_temp': 454
    }
}

NIGHT = {
    'rgb': {
        'brightness': 1,
        'hs_color': [29.164, 80.271]
    },
    'whitespectrum': {
        'brightness': 1,
        'color_temp': 454
    }
}


TIME_TABLE = [
    #HH MM
    ( 0,  0, NIGHT),
    ( 6,  0, NIGHT),
    ( 6, 15, EVENING),
    ( 7, 00, FOCUS),
    (12, 00, FOCUS),
    (19, 00, EVERY_DAY),
    (22, 00, EVERY_DAY),
    (22, 30, EVENING),
    (24, 00, EVENING),
]


def mix(start:float, end:float, amount:float) -> float:
    return start*(1 - amount) + end*amount


def fade(from_state:dict, to_state:dict, amount:float) -> dict:
    if amount < 0:
        LOG.info('clipping fade amount to 0')
        amount = 0
    if amount > 1:
        amount = 1
        LOG.info('clipping fade amount to 1')
    result = {}
    for key, value in from_state.items():
        if isinstance(value, list):
            result[key] = [mix(from_state[key][i], to_state[key][i], amount) for i in range(len(value))]
        elif isinstance(value, dict):
            result[key] = fade(from_state[key], to_state[key], amount)
        else:
            result[key] = mix(from_state[key], to_state[key], amount)
    return result


def day_progress(now=None):
    if now is None:
        now = datetime.datetime.now()

    prev_hour, prev_minute, prev_state = TIME_TABLE[0]

    for hour, minute, state in TIME_TABLE:
        if hour > now.hour or hour == now.hour and minute > now.minute:
            break

        prev_state = state
        prev_hour = hour
        prev_minute = minute

    state_length = (hour - prev_hour) * 60 + (minute - prev_minute)
    time_left = (hour - now.hour) * 60 + (minute - now.minute)
    state_progrses = 1 - time_left / state_length
    return prev_state, state, state_progrses


def day_color():
    prev_state, state, state_progrses = day_progress()
    return fade(prev_state, state, state_progrses)


class LightColor(hass.Hass):
    def initialize(self):
        self.current_updates = {}
        self.current_color = day_color()
        data = self.get_state(entity='light')
        self.listen_state(self.state_change, entity='light')
        self.listen_state(self.input_change, entity='input_select')
        self.run_every(self.cron, datetime.datetime.now(), 60)

        for state_input, lights in GROUPS.items():
            for entity, light_type in lights:
                if not entity.startswith('group.'):
                    continue

                group_state = self.get_state(entity, attribute='all')
                for light in group_state['attributes']['entity_id']:
                    print('adding', light, 'to', state_input)
                    INVERSE_GROUPS[light] = (state_input, light_type)

    def cron(self, *args):
        self.current_color = day_color()
        # self.turn_on('light.t1', **{
        #     'brightness': 254,
        #     'color_temp': 250
        # })
        full_state = self.get_state()
        for state_input, lights in GROUPS.items():
            state = self.get_state(state_input)

            if state != 'auto':
                continue

            self.update_group(state_input)
    
    def update_group(self, state_input):
        for entity, light_type in GROUPS[state_input]:
            group_state = self.get_state(entity, attribute='all')

            if group_state['state'] == 'off':
                continue

            light_target_state = self.current_color[light_type]
            # if 'entity_id' in group_state['attributes']:
            # for light_id in sorted(group_state['attributes']['entity_id']):
            self.update(entity, light_target_state)    

    def update(self, light_id, light_target_state):
        self.current_updates[light_id] = {'s': light_target_state, 't': time.time()}
        self.turn_on(light_id, **light_target_state)

    def input_change(self, entity, attribute, old, new, kwargs):
        # print('state change!')
        # print(entity)
        # print(attribute)
        # print(old)
        # print(new)
        # print(kwargs)
        # print()
        
        if entity not in GROUPS:
            print(f'no group for "{entity}" defined')
            return
        
        if old == 'manual' and new == 'auto':
            print(f'{entity} changed to auto')
            self.update_group(entity)

        sys.stdout.flush()

    def state_change(self, entity, attribute, old, new, kwargs):
        if entity not in INVERSE_GROUPS:
            print('entity ignored', entity)
            sys.stdout.flush()
            return

        if new == 'off':
            return

        state_name, light_type = INVERSE_GROUPS[entity]
        state_name = state_name
        state = self.get_state(state_name)
        if state != 'auto':
            return

        light_target_state = self.current_color[light_type]

        if old == 'off' and new == 'on':
            self.update(entity, light_target_state)
            return

        light_state = self.get_state(entity, attribute='attributes')

        now = time.time()
        current_update = self.current_updates.get(entity)
        if current_update and now - current_update['t'] < 30:
            # most like this change event is due to the cron job
            # changing this light.
            self.current_updates[entity] = None
            return

        # light attributes where manuelly changed, end auto mode
        print(f'{entity} was changed manually, {state_name} set to "manual"')
        sys.stdout.flush()
        self.set_state(state_name, state='manual')