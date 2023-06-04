import requests
import random


class Pokemon:
    def __init__(self, name, level, moves):
        self.name = name.lower()
        self.level = level
        self.hp =0
        self.attack = 0
        self.defense = 0
        self.spattack = 0
        self.spdefense = 0
        self.speed = 0
        self.types = []
        self.moves = moves
        self.ability = ''
        url = f"https://pokeapi.co/api/v2/pokemon/{self.name}"
        response = requests.get(url)
        if response.status_code == 200:
            self.pokemon_data = response.json()
            self.set_type()
            self.set_stats()
        else:
            print("Error: Failed to fetch Pokémon data.")


    def set_type(self):
        types = self.pokemon_data['types']
        pokemon_types = [type_data['type']['name'] for type_data in types]
        return pokemon_types



    def set_stats(self):
        stats = self.pokemon_data['stats']
        for stat in stats:
            stat_name = stat['stat']['name']
            stat_value = stat['base_stat']

            if stat_name == 'speed':
                self.speed = stat_value
            elif stat_name == 'attack':
                self.attack = stat_value
            elif stat_name == 'defense':
                self.defense = stat_value
            elif stat_name == 'special-attack':
                self.spattack = stat_value
            elif stat_name == 'special-defense':
                self.spdefense = stat_value
            elif stat_name == 'hp':
                self.hp = stat_value

class Pokemon_Move:
    def __init__(self, name):
        self.name = name
        self.pp = 0
        self.power = 0
        self.effect = None
        self.priority = 0
        self.accuracy = 0
        self.type = ''
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

    def display(self):
        print(f'{self.name}: {self.pp} pp, {self.power} power, {self.accuracy} accuracy, {self.type}')

class Pokemon_Battle:
    def __init__(self, Pokemon1, Pokemon2):
        self.Pokemon1 = Pokemon1
        self.Pokemon2 = Pokemon2
        self.turn = False

    def battle(self):
        while self.Pokemon1.hp > 0 and self.Pokemon2.hp > 0:
            print(f'{self.Pokemon1.name.capitalize} has {self.Pokemon1.hp} hp.')
            print(f'{self.Pokemon2.name.capitalize} has {self.Pokemon2.hp} hp.')

            if self.Pokemon1.speed > self.Pokemon2.speed:
                self.perform_turn(self.Pokemon1, self.Pokemon2)
                if self.Pokemon2.hp > 0:  # Check if the battle has already ended
                    self.perform_turn(self.Pokemon2, self.Pokemon1)
            elif self.Pokemon2.speed > self.Pokemon1.speed:
                self.perform_turn(self.Pokemon2, self.Pokemon1)
                if self.Pokemon1.hp > 0:  # Check if the battle has already ended
                    self.perform_turn(self.Pokemon1, self.Pokemon2)
            else:
                # If both Pokemon have the same speed, randomly determine which one moves first
                first_pokemon = random.choice([self.Pokemon1, self.Pokemon2])
                second_pokemon = self.Pokemon2 if first_pokemon == self.Pokemon1 else self.Pokemon1
                self.perform_turn(first_pokemon, second_pokemon)
                if second_pokemon.hp > 0:  # Check if the battle has already ended
                    self.perform_turn(second_pokemon, first_pokemon)

    def perform_turn(self, attacking_Pokemon, defending_Pokemon):
        damage = 0
        STAB = False

        for move in attacking_Pokemon.moves:
            move.display()
        user_choice = input('Choose a move: ').lower()
        for move in attacking_Pokemon.moves:
            if user_choice == move.name:
                if move.type == attacking_Pokemon.type:





    def get_TypeDamage(self, type):
            url = f'https://pokeapi.co/api/v2/type/{type}/'
            response1 = requests.get(url)
            if response1.status_code == 200:
                type_data = response1.json()
                weakness_data = type_data['damage_relations']['double_damage_from']
                type_names = [t["name"] for t in weakness_data]
                for name in type_names:
                    print(name)
            else:
                print("Error getting Type Information")


blastoise = Pokemon('blastoise',  5, [Pokemon_Move('crunch'), Pokemon_Move('tackle'), Pokemon_Move('water gun'), Pokemon_Move('hydro pump')])
Charizard = Pokemon('charizard', 10, [Pokemon_Move('fly'), Pokemon_Move('flamethrower'), Pokemon_Move('wing attack'), Pokemon_Move('bite')])


