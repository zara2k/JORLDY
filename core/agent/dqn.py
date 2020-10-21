import torch
import torch.nn.functional as F
import random

from core.utils import ReplayBuffer
from core.network import Network
from core.optimizer import Optimizer

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

class DQNAgent:
    def __init__(self,
                state_size,
                action_size,
                network='dqn',
                optimizer='adam',
                learning_rate=3e-4,
                gamma=0.99,
                epsilon_init=1.0,
                epsilon_min=0.1,
                explore_step=90000,
                buffer_size=50000,
                batch_size=64,
                start_train_step=2000,
                target_update_term=500,
                ):
        
        self.action_size = action_size
        self.network = Network(network, state_size, action_size).to(device)
        self.target_network = Network(network, state_size, action_size).to(device)
        self.optimizer = Optimizer(optimizer, self.network.parameters(), lr=learning_rate)
        self.gamma = gamma
        self.epsilon = epsilon_init
        self.epsilon_init = epsilon_init
        self.epsilon_min = epsilon_min
        self.explore_step = explore_step
        self.memory = ReplayBuffer(buffer_size)
        self.batch_size = batch_size
        self.start_train_step = start_train_step
        self.target_update_term = target_update_term
        self.num_learn = 0
    
    def act(self, state, training=True):
        if random.random() < self.epsilon and training:
            self.network.train()
            action = random.randint(0, self.action_size-1)
        else:
            self.network.eval()
            action = torch.argmax(self.network(torch.FloatTensor(state).to(device))).item()
        return action

    def learn(self):
        if self.memory.length < max(self.batch_size, self.start_train_step):
            return None
        
        state, action, reward, next_state, done = self.memory.sample(self.batch_size)
    
        one_hot_action = torch.eye(self.action_size)[action.view(-1).long()]
        q = (self.network(torch.FloatTensor(state).to(device)) * one_hot_action.to(device)).sum(1, keepdims=True)
        next_q = self.target_network(torch.FloatTensor(next_state).to(device))
        target_q = reward.to(device) + next_q.max(1, keepdims=True).values * (self.gamma*(1 - done)).to(device)
        loss = F.smooth_l1_loss(q, target_q).mean()

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        if self.num_learn % self.target_update_term == 0:
            self.update_target()
        self.num_learn += 1
        
        result = {
            "loss" : loss.item(),
            "epsilon" : self.epsilon,
        }
        return result

    def update_target(self):
        self.target_network.load_state_dict(self.network.state_dict())
        
    def observe(self, state, action, reward, next_state, done):
        # Process per step
        self.memory.store(state, action, reward, next_state, done)
        
        # Process per step if train start
        if self.num_learn > 0:
            self.epsilon_decay()
        
        # Process per episode
        if done:
            pass
            
    def epsilon_decay(self):
        new_epsilon = self.epsilon - ((self.epsilon_init - self.epsilon_min)/\
                                      (self.explore_step - self.start_train_step))
        self.epsilon = max(self.epsilon_min, new_epsilon)
        
        
