import requests
import random
import math

class Pokemon:
    def __init__(self, name, moves):
        #Initialize all Pokemon variables
        self.name = name.lower()
        self.level = 50
        self.hp =0
        self.attack = 0
        self.defense = 0
        self.spattack = 0
        self.spdefense = 0
        self.speed = 0
        self.evasion = 0
        self.types = []
        self.moves = moves
        self.previous_moves = []
        self.damage = 0
        url = f"https://pokeapi.co/api/v2/pokemon/{self.name}"
        response = requests.get(url)
        if response.status_code == 200:
            #Check if response is valid, then gather data
            self.pokemon_data = response.json()
            self.set_type()
            self.set_stats()
        else:
            print("Error: Failed to fetch Pokémon data.")


    def set_type(self):
        types = self.pokemon_data['types']
        pokemon_types = [type_data['type']['name'] for type_data in types]
        self.types = pokemon_types



    def set_stats(self):
        stats = self.pokemon_data['stats']
        for stat in stats:
            stat_name = stat['stat']['name']
            stat_value = stat['base_stat']
            #adjusted formulas to ignore EV, IV, and nature
            if stat_name == 'speed':
                self.speed = math.floor(0.01 * (2 * stat_value) * self.level) + 5
            elif stat_name == 'attack':
                self.attack = math.floor(0.01 * (2 * stat_value) * self.level) + 5
            elif stat_name == 'defense':
                self.defense = math.floor(0.01 * (2 * stat_value) * self.level) + 5
            elif stat_name == 'special-attack':
                self.spattack = math.floor(0.01 * (2 * stat_value) * self.level) + 5
            elif stat_name == 'special-defense':
                self.spdefense = math.floor(0.01 * (2 * stat_value) * self.level) + 5
            elif stat_name == 'hp':
                self.hp = math.floor(0.01 * (2 * stat_value) * self.level) + self.level + 10

    def use_move(self, move_name, damage):
        if len(self.previous_moves) >= 4:
            self.previous_moves.pop(0)  # Remove the oldest move if the list is full
        self.previous_moves.append(move_name)
        self.damage = damage
        

class Pokemon_Move:
    def __init__(self, name):
        self.name = name
        self.pp = 0
        self.power = 0
        self.effect = None
        self.priority = 0
        self.accuracy = 0
        self.type = ''
        self.damage_class = ''
        self.status = 0
        self.status_stat = ''
        self.get_data()

    def get_data(self):
        url = f'https://pokeapi.co/api/v2/move/{self.name.lower()}/'
        response = requests.get(url)
        move_data = response.json()
        self.pp = move_data['pp']
        self.power = move_data['power']
        self.accuracy = move_data['accuracy']
        self.priority = move_data['priority']
        self.type = move_data['type']['name']
        self.damage_class = move_data['damage_class']['name']
        self.type_effectiveness = self.get_type_effectiveness(self.type)

        if self.accuracy == None:
            self.accuracy = 100

        if self.damage_class == 'status':

            status_data = move_data['stat_changes']
            self.status_stat = status_data[0]['stat']['name']
            stage_modifier = status_data[0]['change']
            negative_stat_multipliers = {
                -6: 0.25, -5: 0.285, -4: 0.33, -3: 0.4, -2: 0.5, -1: 0.66
            }
            if stage_modifier < 0:
                self.status = negative_stat_multipliers.get(stage_modifier, 0)
            elif stage_modifier == 0:
                self.status = 0
            else:
                self.status = 1 + (stage_modifier * 0.5)
                
        if self.power == None:
            self.power = 0


    def get_type_effectiveness(self, type):
            url = f'https://pokeapi.co/api/v2/type/{type}/'
            response1 = requests.get(url)
            if response1.status_code == 200:
                type_data = response1.json()
                weakness_data = type_data.get('damage_relations')

                if weakness_data is None:
                    print(f"No damage_relations found for type '{type}'")
                    return {}

                type_effectiveness = {
                    'double_damage_from': [],
                    'double_damage_to': [],
                    'half_damage_from': [],
                    'half_damage_to': [],
                    'no_damage_from': [],
                    'no_damage_to': []
                }

                for relation_name, relation_types in weakness_data.items():
                    for relation_type in relation_types:
                        type_effectiveness[relation_name].append(relation_type['name'])

                return type_effectiveness
            else:
                print("Error getting Type Information")
                return {}


    def display(self):
        print(f'{self.name.capitalize()}: {self.pp} pp, {self.power} power, {self.accuracy} accuracy, {self.type}')

class Pokemon_Battle:
    def __init__(self, Pokemon1, Pokemon2):
        self.Pokemon1 = Pokemon1
        self.Pokemon2 = Pokemon2
        self.turn = False
        #self.battle()


    def perform_turn(self, attacking_Pokemon, defending_Pokemon, action):
        damage = 0
        chance = random.randint(1, 100)

        for move1 in attacking_Pokemon.moves:
            move1.display()
            
        move = attacking_Pokemon.moves[action]
        
        if chance <= move.accuracy:
            #If move lands, compute damage/effect
            #Status moves such as sleep, paralysis, etc. not added yet
            modifier = self.get_effectiveness(move, defending_Pokemon)
            
            if move.damage_class == 'physical':
                damage = (((2 * attacking_Pokemon.level / 5 + 2) * move.power * (attacking_Pokemon.attack / defending_Pokemon.defense) / 50) + 2) * modifier
            elif move.damage_class == 'special':
                damage = (((2 * attacking_Pokemon.level / 5 + 2) * move.power * (attacking_Pokemon.spattack / defending_Pokemon.spdefense) / 50) + 2) * modifier
            elif move.damage_class == 'status':
                if move.status_stat == 'speed':
                    if move.status > 1:
                        attacking_Pokemon.speed *= move.status
                    else:
                        defending_Pokemon.speed *= move.status
                elif move.status_stat == 'defense':
                    if move.status > 1:
                        attacking_Pokemon.defense *= move.status
                    else:
                        defending_Pokemon.defense *= move.status
                elif move.status_stat == 'attack':
                    if move.status > 1:
                        attacking_Pokemon.attack *= move.status
                    else:
                        defending_Pokemon.attack *= move.status
                elif move.status_stat == 'special-attack':
                    if move.status > 1:
                        attacking_Pokemon.spattack *= move.status
                    else:
                        defending_Pokemon.spattack *= move.status
                elif move.status_stat == 'special-defense':
                    if move.status > 1:
                        attacking_Pokemon.spdefense *= move.status
                    else:
                        defending_Pokemon.spdefense *= move.status
                damage = 0

                if move.type in attacking_Pokemon.types:
                    damage = damage * 1.5
            print(f'{attacking_Pokemon.name.capitalize()} used {move.name.capitalize()}!')
            defending_Pokemon.hp -= damage
        else:
            print(f'{move.name.capitalize()} missed!')
        
        attacking_Pokemon.use_move(move.name, damage)




    def get_effectiveness(self, move, defending_pokemon):
        damage_modifier = 1.0
        dtypes = defending_pokemon.types
        type_effectiveness = move.type_effectiveness

        for type in dtypes:
            for damage_relation, types in type_effectiveness.items():
                if type in types:
                    if damage_relation == 'double_damage_to':
                        damage_modifier *= 2.0
                        print('Super Effective!')
                    elif damage_relation == 'half_damage_to':
                        damage_modifier *= 0.5
                        print('Not very effective')
                    elif damage_relation == 'no_damage_to':
                        print('No damage done')
                        damage_modifier *= 0.0
        print(damage_modifier)
        return damage_modifier



