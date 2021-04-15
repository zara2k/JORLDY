from mlagents.envs import UnityEnvironment
import numpy as np 

class HopperMLAgent:
    def __init__(self, train_mode=True):
        self.env = UnityEnvironment(file_name="./core/env/mlagents/Hopper/Server/Hopper", worker_id=np.random.randint(65535))

        self.state_size = 19*4
        self.action_size = 3
        self.train_mode = train_mode
        
        self.score = 0
        
        self.default_brain = self.env.brain_names[0]
        self.brain = self.env.brains[self.default_brain]
        
        self.env_info = self.env.reset(train_mode=train_mode)[self.default_brain]
        
    def reset(self):
        self.score = 0
        self.env_info = self.env.reset(train_mode=self.train_mode)[self.default_brain]
        state = self.env_info.vector_observations

        return state

    def step(self, action):
        self.env_info = self.env.step(action)[self.default_brain]
        
        next_state = self.env_info.vector_observations
        reward = self.env_info.rewards
        done = self.env_info.local_done
        
        self.score += reward[0] 
        reward, done = map(lambda x: np.expand_dims(x, 0), [reward, done])
        return (next_state, reward, done)

    def close(self):
        self.env.close()

class PongMLAgent:
    def __init__(self, train_mode=True):
        self.env = UnityEnvironment(file_name="./core/env/mlagents/Pong/Server/Pong", worker_id=np.random.randint(65535))

        self.state_size = 8*4
        self.action_size = 3
        self.train_mode = train_mode
        
        self.score = 0
        
        self.default_brain = self.env.brain_names[0]
        self.brain = self.env.brains[self.default_brain]
        
        self.env_info = self.env.reset(train_mode=train_mode)[self.default_brain]
        
    def reset(self):
        self.score = 0
        self.env_info = self.env.reset(train_mode=self.train_mode)[self.default_brain]
        state = self.env_info.vector_observations
        return state

    def step(self, action):
        self.env_info = self.env.step(action)[self.default_brain]
        
        next_state = self.env_info.vector_observations
        reward = self.env_info.rewards
        done = self.env_info.local_done
        
        self.score += reward[0]
        
        reward, done = map(lambda x: np.expand_dims(x, 0), [reward, done])
        return (next_state, reward, done)

    def close(self):
        self.env.close()