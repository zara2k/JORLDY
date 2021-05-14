import os 

# 라이브러리 불러오기
import numpy as np
import random
import datetime
import os
from collections import deque
import gym

import torch
import torch.optim as optim
import torch.nn.functional as F
import torch.nn as nn

import time

# 파라미터 세팅  
algorithm = 'DQN'

# gym cartpole
state_size = 4
action_size = 2 

load_model = False
train_mode = True

batch_size = 32
mem_maxlen = 50000

discount_factor = 0.99
learning_rate = 0.0001

start_train_step = 2500
run_step = 50000
test_step = 10000

target_update_step = 500
print_episode = 10
save_step = 100000

epsilon_init = 1.0
epsilon_min = 0.1

date_time = datetime.datetime.now().strftime("%Y%m%d-%H-%M-%S")

save_path = "./saved_models/" + date_time
load_path = "./saved_models/20210205-18-52-50_DQN"

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
device_cpu = torch.device("cpu")

print("cpu count:", os.cpu_count())
num_actors = os.cpu_count() - 2
update_actor_step = 1

class Network(nn.Module):
    def __init__(self, network_name):
        super(Network, self).__init__()
        self.fc1 = nn.Linear(state_size, 512)
        self.fc2 = nn.Linear(512, 512)
        self.fc3 = nn.Linear(512, action_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

class DQN_Actor(object):
    def __init__(self, epsilon):
        self.env = gym.make('CartPole-v1')
        self.state = self.env.reset()
        
        self.epsilon = epsilon
        self.train_mode = True 
        
        self.model = Network("main"+str(epsilon)).to(device_cpu)

    def get_sample(self):
        action = self.get_action(self.state)
        state_next, reward, done, info = self.env.step(action)

        exp = [self.state, action, reward, state_next, done]
        
        if done:
            self.state = self.env.reset()
        else:
            self.state = state_next
        
        return exp
    
    def set_model(self, model):
        self.model.load_state_dict(model.state_dict())

    def get_action(self, state):
        if self.epsilon > np.random.rand():
            # 랜덤하게 행동 결정
            return np.random.randint(0, action_size)
        else:
            with torch.no_grad():
            # 네트워크 연산에 따라 행동 결정
                Q = self.model(torch.FloatTensor([state]))
            return np.argmax(Q.numpy())
                            
class DQN_Trainer(object):
    def __init__(self):
        self.model = Network("main").to(device)
        self.model_cpu = Network("main_cpu").to(device)
        self.target_model = Network("target").to(device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
    
    def train(self, memory):
        batch = random.sample(memory, batch_size)

        state_batch      = torch.FloatTensor(np.stack([b[0] for b in batch], axis=0)).to(device)
        action_batch     = torch.FloatTensor(np.stack([b[1] for b in batch], axis=0)).to(device)
        reward_batch     = torch.FloatTensor(np.stack([b[2] for b in batch], axis=0)).to(device)
        next_state_batch = torch.FloatTensor(np.stack([b[3] for b in batch], axis=0)).to(device)
        done_batch       = torch.FloatTensor(np.stack([b[4] for b in batch], axis=0)).to(device)
                
        eye = torch.eye(action_size).to(device)
        one_hot_action = eye[action_batch.view(-1).long()].to(device)
        q = (self.model(state_batch) * one_hot_action).sum(1)
                
        with torch.no_grad():
            max_Q = torch.max(q).item()
            next_q = self.target_model(next_state_batch)
            target_q = reward_batch + next_q.max(1).values * (discount_factor*(1 - done_batch))
            
        loss = F.smooth_l1_loss(q, target_q)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item(), max_Q
    
    def get_model(self):
        self.model_cpu.load_state_dict(self.model.state_dict())
        self.model_cpu.to(device_cpu)
        return self.model_cpu

    def update_target(self):
        self.target_model.load_state_dict(self.model.state_dict())

# 메인 함수
if __name__ == '__main__':   

    trainer = DQN_Trainer()

    actors = []
    for i in range(num_actors):
        epsilon_temp =i*(1/(num_actors-1))
        actor = DQN_Actor(epsilon_temp)
        actors.append(actor)

    model = trainer.get_model()
    
    futures = [actor.set_model(model) for actor in actors]

    replay_memory = deque(maxlen=mem_maxlen)
       
    episode = 0
    score = 0
    done_step = 0

    reward_list = []
    loss_list = []
    max_Q_list = []

    t = time.time()
    for step in range(100000):        
        samples = [actor.get_sample() for actor in actors]

        score += samples[0][2]

        replay_memory += samples 

        if step > start_train_step and train_mode:             
            loss, maxQ = trainer.train(replay_memory)
            loss_list.append(loss)
            max_Q_list.append(maxQ)

            if step % update_actor_step == 0:
                model = trainer.get_model()

                futures = [actor.set_model(model) for actor in actors]

            if step % target_update_step == 0:
                trainer.update_target()

        if samples[0][4]:
            reward_list.append(score)
            episode += 1
            score = 0
            done_step = step
            
        # 진행상황 출력 
        if step % 500 == 0:
            print("step: {} / episode: {} / score: {:.2f} / loss: {:.4f} / maxQ: {:.2f} / took time: {}".format
                  (step, episode, np.mean(reward_list), np.mean(loss_list), np.mean(max_Q_list), time.time() - t))

            t = time.time()
            reward_list = []
            loss_list = []
            max_Q_list = []
