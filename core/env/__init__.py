from .gym_env import *
from .atari import *

class Env:
    dictionary = {
    "cartpole": CartPole,
    "pendulum": Pendulum,
    "breakout": Breakout,
    }
    
    def __new__(self, name, *args, **kwargs):
        expected_type = str
        if type(name) != expected_type:
            print("### name variable must be string! ###")
            raise Exception
        name = name.lower()
        if not name in self.dictionary.keys():
            print(f"### can use only follows {[opt for opt in self.dictionary.keys()]}")
            raise Exception
        return self.dictionary[name](*args, **kwargs)

'''
class TemplateEnvironment:
    def __init__(self):
        pass

    def reset(self):
        pass

    def step(self, action):
        pass

    def close(self):
        pass
'''