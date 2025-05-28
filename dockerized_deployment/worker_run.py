
import time
import stable_baselines3
import gymnasium as gym
import redis_utils
# import numpy as np
import os
import argparse


from stable_baselines3 import SAC
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.logger import configure
from stable_baselines3.common.evaluation import evaluate_policy

# def upload_file_to_blob(source_file_path, dest_file_path, redis_host, redis_port = 6379):
#     '''
#     Used to upload files to blob\n
#     Params

#     '''
#     redis_client = redis.Redis(host= f"{redis_host}", port= 6379, decode_responses=False)
#     # pickle_file = 

#     pass

# def upload_object_to_blob(obj, redis_host, redis_port = 6379):
#     '''
#     Used to upload objects to blob
#     '''
#     redis_client = redis.Redis(host= f"{redis_host}", port= 6379, decode_responses=False)
#     pass

def train_sac(
        vm_id, 
        seed, 
        total_timesteps, 
        learning_rate, 
        buffer_size,
        redis_host, 
        redis_host_port,
        storage_container = "rl-training-results"):
    '''
    Params \n
    vm_id : id of vm that algorithm is being ran in \n
    seed : seed to initialized model with \n
    total_timesteps : timesteps taken during training \n
    learning_rate : \n
    buffer_rate : \n
    '''
    # Create unique run ID
    run_id = f"vm{vm_id}_seed{seed}_{int(time.time())}"


    #  Configure logging and directories
    log_dir = os.path.join("logs", f"SAC_lunar_lander_{run_id}")
    model_dir = os.path.join("models", run_id)
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)


    # Create and wrap the environment
    env = gym.make("LunarLander-v2", render_mode=None)
    env = Monitor(env, log_dir)

    # Create evaluation environment
    eval_env = gym.make("LunarLander-v2", render_mode=None)
    eval_env = Monitor(eval_env, os.path.join(log_dir, "eval"))

    # Create the SAC model with custom parameters
    model = SAC(
        "MlpPolicy",
        env,
        learning_rate=learning_rate,
        buffer_size=buffer_size,
        learning_starts=10000,
        batch_size=256,
        tau=0.005,
        gamma=0.99,
        train_freq=1,
        gradient_steps=1,
        action_noise=None,
        ent_coef="auto",
        verbose=1,
        tensorboard_log=log_dir,
        seed=seed,
    )


    # Define callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=50000,
        save_path=model_dir,
        name_prefix=f"sac_model",
        save_replay_buffer=True,
        save_vecnormalize=True,
    )

    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=os.path.join(model_dir, "best"),
        log_path=os.path.join(log_dir, "eval"),
        eval_freq=10000,
        deterministic=True,
        render=False
    )

    # Train the model
    print(f"Starting training on VM {vm_id} with seed {seed}")
    model.learn(
        total_timesteps=total_timesteps,
        callback=[checkpoint_callback, eval_callback],
        log_interval=10,
    )

    # Save model
    final_model_path = os.path.join(model_dir, "sac_lunar_lander_final")
    model.save(final_model_path)
    print(f"Model saved to {final_model_path}")

    # Evalution trained model
    mean_reward, std_reward = evaluate_policy(model, eval_env, n_eval_episodes=10)
    print(f"Mean reward: {mean_reward:.2f} +/- {std_reward:.2f}")

    # Save evalution results
    eval_results = {
        "vm_id": vm_id,
        "seed": seed,
        "mean_reward": float(mean_reward),
        "std_reward": float(std_reward),
        "total_timesteps": total_timesteps,
        "learning_rate": learning_rate,
        "buffer_size": buffer_size,
        "timestamp": time.time()
    }

    # Upload model to blob/redis storage

    # Upload logs/evaluation to blob/redis storage


    return mean_reward, run_id
    pass
    



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train SAC for LunarLander on Azure VM")

    parser.add_argument("--vm-id", type=int, required=True, help="VM identifier")
    parser.add_argument("-redis_client", type = str ,required=True, help= "Address/domain of redis instance for blob storage")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    parser.add_argument("--timesteps", type=int, default=500000, help="Total timesteps to train")
    parser.add_argument("--lr", type=float, default=0.0003, help="Learning rate")
    parser.add_argument("--buffer-size", type=int, default=1000000, help="Replay buffer size")
    parser.add_argument("--redis_client_port", type = int , default=6379, help= "Port where redis instance is serviced from")
    # parser.add_argument("--container", type=str, default="rl-training-results", 
    #                      help="Azure storage container for results")
    
    args = parser.parse_args()
    
    mean_reward, run_id = train_sac(
        vm_id=args.vm_id,
        seed=args.seed,
        total_timesteps=args.timesteps,
        learning_rate=args.lr,
        buffer_size=args.buffer_size,
        storage_container=args.container
    )
    print(f"Training completed. Run ID: {run_id}, Mean reward: {mean_reward:.2f}")
    