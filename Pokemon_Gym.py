#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install gym')
get_ipython().system('pip install stable_baselines3[extra]')


# In[1]:


from Pokemon import Pokemon, Pokemon_Move, Pokemon_Battle
import gymnasium as gym
from gymnasium import Env
from gymnasium.spaces import Discrete, Box, Tuple, MultiBinary, MultiDiscrete
from gymnasium.wrappers import FlattenObservation
import numpy as np
import random
import os


# In[18]:


class BattleEnv(gym.Env):
    def __init__(self):
        #Four moves for Pokemon
        self.action_space = Discrete(4)
        self.done = False

        # Define the observation space for continuous attributes (Pokemon stats and move damage dealt)
        self.num_stats = 6  # Number of Pokemon stats (HP, Attack, Defense, SpAttack, SpDefense, Speed)
        self.num_moves = 4  # Number of moves each Pokemon can have
        self.observation_stats_low = np.zeros(self.num_stats)
        self.observation_stats_high = np.array([255.0] * self.num_stats)

        self.observation_damage_low = np.zeros(self.num_moves)
        self.observation_damage_high = np.array([100.0] * self.num_moves)

        # Define the observation space for discrete attributes (types, move types, and previously used moves)
        self.num_types = 18  # Number of Pokemon types
        self.num_damage_types = 3  # Number of damage types (special, physical, status)
        self.pokemon_types = ['normal', 'fighting', 'flying', 'poison', 'ground', 'rock', 'bug', 'ghost', 'steel', 'fire', 'water', 'grass', 'electric', 'psychic', 'ice', 'dragon', 'dark', 'fairy']
        self.type_to_index = {type_name: idx for idx, type_name in enumerate(self.pokemon_types)}
        self.damage_types = ['physical', 'special', 'status']

        # Combine the continuous and discrete attributes
        # Combine the continuous and discrete attributes
        self.observation_space = gym.spaces.Dict({
            'player_stats': gym.spaces.Box(low=self.observation_stats_low, high=self.observation_stats_high, dtype=np.float32),
            'player_pokemon_types': gym.spaces.MultiBinary(self.num_types),
            'player_move_types': gym.spaces.MultiDiscrete([self.num_types, self.num_types, self.num_types, self.num_types]),
            'player_move_damage': gym.spaces.Box(low=self.observation_damage_low, high=self.observation_damage_high, dtype=np.float32),
            'player_previous_moves': gym.spaces.MultiBinary(self.num_moves),
            'opponent_move_types': gym.spaces.MultiDiscrete([self.num_types, self.num_types, self.num_types, self.num_types]),
            'opponent_previous_moves': gym.spaces.MultiBinary(self.num_moves),
        })


        
    def step(self, action):
        opponent_action = Discrete(4).sample()

        if self.Pokemon1.speed > self.Pokemon2.speed:
            self.battle.perform_turn(self.Pokemon1, self.Pokemon2, action)
            if self.Pokemon2.hp > 0:  # Check if the battle has already ended
                self.battle.perform_turn(self.Pokemon2, self.Pokemon1, opponent_action)
        elif self.Pokemon2.speed > self.Pokemon1.speed:
            self.battle.perform_turn(self.Pokemon2, self.Pokemon1, opponent_action)
            if self.Pokemon1.hp > 0:
                self.battle.perform_turn(self.Pokemon1, self.Pokemon2, action)
        else:
            first_pokemon = random.choice([self.Pokemon1, self.Pokemon2])
            second_pokemon = self.Pokemon2 if first_pokemon == self.Pokemon1 else self.Pokemon1
            self.battle.perform_turn(first_pokemon, second_pokemon, action if first_pokemon == self.Pokemon1 else opponent_action)
            if second_pokemon.hp > 0:  # Check if the battle has already ended
                self.battle.perform_turn(second_pokemon, first_pokemon, action if second_pokemon == self.Pokemon1 else opponent_action)

        if self.Pokemon1.hp <= 0:
            print(f'{self.Pokemon1.name.capitalize()} has fainted.')
            self.done = True
        if self.Pokemon2.hp <= 0:
            print(f'{self.Pokemon2.name.capitalize()} has fainted.')
            self.done = True

        observation = self.get_observation()
        reward = self.get_reward()
        info = {}

        return observation, reward, self.done, info

            
    def render(self):
        print(f'{self.Pokemon1.name.capitalize()} has {self.Pokemon1.hp} hp.')
        print(f'{self.Pokemon2.name.capitalize()} has {self.Pokemon2.hp} hp.')
    
    def reset(self, seed=None):
        self.Pokemon1 = self.get_random_pokemon()  # Get a random player Pokemon
        self.Pokemon2 = self.get_random_pokemon()  # Get a random opponent Pokemon
        self.current_turn_number = 1
        self.any_status_condition_active = False
        self.previous_action = None
        self.previous_opponent_action = None
        self.battle = Pokemon_Battle(self.Pokemon1, self.Pokemon2)

        # Get the initial observation
        observation = self.get_observation()
        
        info = {}

        return observation, info
    
    def get_reward(self):
        
        if self.done:
            if self.Pokemon1.hp <= 0:
                # Player Pokemon has fainted, so the agent lost the battle
                reward = -100  # Penalty for losing the battle
            elif self.Pokemon2.hp <= 0:
                # Opponent Pokemon has fainted, so the agent won the battle
                reward = 100  # Reward for winning the battle
            else:
                # The battle ended in a draw or some other unknown condition
                reward = 0
        else:
            reward = self.Pokemon1.damage
        
        return reward
    
    def get_observation(self):
        # Observation for player's Pokemon
        player_observation_stats = np.array([self.Pokemon1.hp, self.Pokemon1.attack, self.Pokemon1.defense,
                                             self.Pokemon1.spattack, self.Pokemon1.spdefense, self.Pokemon1.speed],
                                            dtype=np.float32)

        player_observation_types = np.zeros(self.num_types, dtype=np.int8)
        for type_name in self.Pokemon1.types:
            type_idx = self.type_to_index[type_name]
            player_observation_types[type_idx] = 1.0

        player_observation_move_types = np.zeros(self.num_moves, dtype=np.int64)
        for move_idx, move in enumerate(self.Pokemon1.moves):
            move_type_idx = self.type_to_index[move.type]
            player_observation_move_types[move_idx] = 1.0


        player_observation_move_damage = np.zeros(self.num_moves, dtype=np.float32)
        for move_idx, move in enumerate(self.Pokemon1.moves):
            if not np.isnan(self.Pokemon1.damage):
                player_observation_move_damage[move_idx] = np.clip(self.Pokemon1.damage, 0.0, 100.0)
            else:
                player_observation_move_damage[move_idx] = 0.0

        player_observation_previous_moves = np.zeros(self.num_moves, dtype=np.int8)
        for move_idx, move in enumerate(self.Pokemon1.moves):
            if move in self.Pokemon1.previous_moves:
                player_observation_previous_moves[move_idx] = 1.0

        # Observation for opponent's Pokemon (types and previously used moves are not visible)
        opponent_observation_move_types = np.zeros(self.num_moves, dtype=np.int64)
        for move_idx, move in enumerate(self.Pokemon2.moves):
            move_type_idx = self.type_to_index[move.type]
            opponent_observation_move_types[move_idx] = 1.0


        opponent_observation_previous_moves = np.zeros(self.num_moves, dtype=np.int8)
        for move_idx, move in enumerate(self.Pokemon2.moves):
            if move in self.Pokemon2.previous_moves:
                opponent_observation_previous_moves[move_idx] = 1.0

        observation = {
            'player_stats': player_observation_stats,
            'player_pokemon_types': player_observation_types,
            'player_move_types': player_observation_move_types,
            'player_move_damage': player_observation_move_damage,
            'player_previous_moves': player_observation_previous_moves,
            'opponent_move_types': opponent_observation_move_types,
            'opponent_previous_moves': opponent_observation_previous_moves,
        }

        return observation


    def get_random_pokemon(self):
        #dictionary of pokemon
        pre_built_pokemon = {
        "bulbasaur": ["tackle", "vine-whip", "leer", "razor-leaf"],
        "charmander": ["scratch", "ember", "metal-claw", "flamethrower"],
        "squirtle": ["tackle", "water-gun", "bubble", "hydro-pump"],
        "pikachu": ["growl", "thunder-shock", "electro-ball", "thunderbolt"],
        "jigglypuff": ["pound", "leer", "double-slap", "hyper-voice"],
        "meowth": ["scratch", "crunch", "bite", "growl"],
    }
        
        PokeName = random.choice(list(pre_built_pokemon.keys()))
        moves = pre_built_pokemon[PokeName]
        list_moves = []
        for move in moves:
            list_moves.append(Pokemon_Move(move))
        pokemon = Pokemon(PokeName, list_moves)

        return pokemon


# In[19]:


env = BattleEnv()


# In[46]:


env.observation_space.sample()


# In[4]:


env.reset()


# In[6]:


from stable_baselines3.common.env_checker import check_env


# In[7]:


check_env(env, warn=True)


# In[30]:


Discrete(4).sample()


# In[20]:


episodes = 2
for episode in range(1, episodes+1):
    state = env.reset()
    done = False
    score = 0 
    
    while not done:
        env.render()
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        score+=reward
    print('Episode:{} Score:{}'.format(episode, score))
env.close()


# In[ ]:




