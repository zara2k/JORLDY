### IQN Pong_ML-Agents Config ###

env = {
    "name": "pong_mlagent",
    "train_mode": True
}

agent = {
    "name": "iqn",
    "network": "iqn",
    "gamma": 0.99,
    "epsilon_init": 1.0,
    "epsilon_min": 0.1,
    "explore_step": 450000,
    "buffer_size": 50000,
    "batch_size": 32,
    "start_train_step": 25000,
    "target_update_period": 1000,
    
    "num_sample": 64,
    "embedding_dim": 64,
    "sample_min": 0,
    "sample_max": 1.0
}

optim = {
    "name": "adam",
    "eps": 1e-2/agent['batch_size'],
    "lr": 5e-5,
}

train = {
    "training" : True,
    "load_path" : None,
    "run_step" : 200000,
    "print_period" : 5000,
    "save_period" : 50000,
    "eval_iteration": 10,
    # distributed setting
    "update_period" : 8,
    "num_workers" : 16,
}