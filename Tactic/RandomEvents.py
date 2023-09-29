import random


class RandomEvents:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.hacked_unit = None  # To keep track of the unit that was hacked
        self.switched_unit_my_side = None  # To keep track of the unit switched from my side
        self.switched_unit_enemy_side = None  # To keep track of the unit switched from enemy side


        self.events = [
            {
                "func": self.commanders_insight_team,
                "restore": self.restore_commanders_insight_team,
                "name": "Commander's Insight",
                "description": "Swap the positions of any two units on your team.",
                "type": "good",
            },
            {
                "func": self.remote_hack_team,
                "restore": self.restore_remote_hack_team,
                "name": "Remote Hack",
                "description": "Take control of enemy mechanical units for one turn.",
                "type": "good",
            },
            {
                "func": self.divine_intervention_team,
                "restore": self.restore_divine_intervention_team,
                "name": "Divine Intervention",
                "description": "All units are healed back to full HP.",
                "type": "good",
            },
            {
                "func": self.weapon_jam_team,
                "restore": self.restore_weapon_jam_team,
                "name": "Weapon Jam",
                "description": "All units can't attack for the next turn.",
                "type": "bad",
            },
            {
                "func": self.skill_mastery_team,
                "restore": self.restore_skill_mastery_team,
                "name": "Skill Mastery",
                "description": "All units gain double damage for the next turn.",
                "type": "good",
            },
            {
                "func": self.artifact_team,
                "restore": self.restore_artifact_team,
                "name": "Artifact",
                "description": "A powerful artifact affects all units on the map, giving a additionnal action point.",
                "type": "good",
            },
            {
                "func": self.sabotage_team,
                "restore": self.restore_sabotage_team,
                "name": "Sabotage",
                "description": "All units are disabled for one turn.",
                "type": "bad",
            },
            {
                "func": self.equipment_malfunction_team,
                "restore": self.restore_equipment_malfunction_team,
                "name": "Equipment Malfunction",
                "description": "All units' weapons become less effective for a turn.",
                "type": "bad",
            },
            {
                "func": self.friendly_fire_team,
                "restore": self.restore_friendly_fire_team,
                "name": "Friendly Fire",
                "description": "Units on your team accidentally attack other units on your team.",
                "type": "bad",
            },
            {
                "func": self.damage_boost,
                "restore": self.restore_damage_boost,
                "name": "Damage Boost",
                "description": "Increases the damage of all units on your team for one turn.",
                "type": "good",
            },
            {
                "func": self.armor_plating,
                "restore": self.restore_armor_plating,
                "name": "Armor Plating",
                "description": "Increases the HP of all units on your team for one turn.",
                "type": "good",
            },
            {
                "func": self.adrenaline_rush,
                "restore": self.restore_adrenaline_rush,
                "name": "Adrenaline Rush",
                "description": "All units on your team get extra action points (AP) for one turn.",
                "type": "good",
            },
            {
                "func": self.quick_feet,
                "restore": self.restore_quick_feet,
                "name": "Quick Feet",
                "description": "Increases the Max Move Range of all units on your team for one turn.",
                "type": "good",
            },
            {
                "func": self.sniper_training,
                "restore": self.restore_sniper_training,
                "name": "Sniper Training",
                "description": "Increases the Max Attack Range of all units on your team for one turn.",
                "type": "good",
            },
            {
                "func": self.fuel_shortage,
                "restore": self.restore_fuel_shortage,
                "name": "Fuel Shortage",
                "description": "Increases the Move Cost of all units on your team for one turn.",
                "type": "bad",
            },
            {
                "func": self.gun_jam,
                "restore": self.restore_gun_jam,
                "name": "Gun Jam",
                "description": "Increases the Fire Cost of all units on your team for one turn.",
                "type": "bad",
            },
        ]

    def apply_event_by_name(self, name):
        choosen_event = None
        for event in self.events:
            if event["name"] == name:
                choosen_event = event
                break
            
        self.player1.apply_event(choosen_event["func"], choosen_event["restore"])
        #self.player2.apply_event(choosen_event["func"], choosen_event["restore"])
        return choosen_event             


    def random_event(self):
        event = random.choice(self.events)
        self.player1.apply_event(event["func"], event["restore"])
        self.player2.apply_event(event["func"], event["restore"])
        return event  # Return the event and restore function


# --- Good Events ---


    def commanders_insight_team(self, my_units, enemy_units):

        # Filter units where is_vehicle is True
        vehicle_units_my_side = [unit for unit in my_units if unit.is_vehicle]

        # Randomly select a vehicle unit from each side
        if vehicle_units_my_side:  # Check that both lists are not empty
            unit1 = random.choice(vehicle_units_my_side)
            while True:
                unit2 = random.choice(vehicle_units_my_side)
                if unit1 != unit2:
                    break
        else:
            return

        # Swap their positions
        unit1.x, unit2.x = unit2.x, unit1.x
        unit1.y, unit2.y = unit2.y, unit1.y

        # Swap their tiles
        tile_temp = unit1.tile
        unit1.tile = unit2.tile
        unit2.tile = tile_temp

        # Update the tile's unit reference
        unit1.tile.unit = unit1
        unit2.tile.unit = unit2

        unit1.swapped = True
        unit2.swapped = True                      

        # Store the swapped units for restoring later
        self.swapped_units = (unit1, unit2)

    def restore_commanders_insight_team(self, my_units, enemy_units):
        # Revert the swap
        unit1, unit2 = self.swapped_units  # Get the units that were swapped

        unit1.x, unit2.x = unit2.x, unit1.x
        unit1.y, unit2.y = unit2.y, unit1.y

        # Swap their tiles back
        tile_temp = unit1.tile
        unit1.tile = unit2.tile
        unit2.tile = tile_temp

        # Update the tile's unit reference
        unit1.tile.unit = unit1
        unit2.tile.unit = unit2

        unit1.swapped = False
        unit2.swapped = False

        # Clear the swapped_units attribute
        self.swapped_units = None


    def remote_hack_team(self, my_units, enemy_units):

        # Filter units where is_vehicle is True
        vehicle_units_enemy_side = [unit for unit in enemy_units if unit.is_vehicle]

        # Randomly select a vehicle unit from each side
        if vehicle_units_enemy_side:  # Check that both lists are not empty
            enemy_unit = random.choice(vehicle_units_enemy_side)
        else:
            return            

        # Swap the control (player attribute)
        enemy_unit.player = self.player1.number
        self.player2.units.remove(enemy_unit)
        self.player1.units.append(enemy_unit)

        enemy_unit.swapped = True
        self.swapped_units = enemy_unit

    def restore_remote_hack_team(self, my_units, enemy_units):
        # Swap the control (player attribute)
        enemy_unit = self.swapped_units
        enemy_unit.player = self.player2.number
        self.player1.units.remove(enemy_unit)
        self.player2.units.append(enemy_unit)

        enemy_unit.swapped = False
        self.swapped_units = None


    def divine_intervention_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.original_hp = unit.health
            unit.health = unit.max_health


    def restore_divine_intervention_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.health = unit.original_hp


    def skill_mastery_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.attack_damage *= 2


    def restore_skill_mastery_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.attack_damage /= 2


    def artifact_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.max_action_points += 1
            unit.action_points += 1


    def restore_artifact_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.max_action_points += 1
            unit.action_points -= 1


    # --- Bad Events ---


    def weapon_jam_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.can_attack = False


    def restore_weapon_jam_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.can_attack = True


    def sabotage_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.is_disabled = True


    def restore_sabotage_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.is_disabled = False


    def equipment_malfunction_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.attack_damage *= 0.5


    def restore_equipment_malfunction_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.attack_damage *= 2


    def friendly_fire_team(self, my_units, enemy_units):
        for unit1, unit2 in zip(my_units, enemy_units):
            unit2.health -= unit1.attack_damage
            if unit2.health <= 0:
                unit2.health = 1


    def restore_friendly_fire_team(self, my_units, enemy_units):
        for unit, original_hp in my_units:
            unit.health = unit.original_hp


    def damage_boost(self, my_units, enemy_units):
        for unit in my_units:
            unit.attack_damage *= 1.5  # 50% increase in damage


    def restore_damage_boost(self, my_units, enemy_units):
        for unit in my_units:
            unit.attack_damage /= 1.5  # Restore original damage


    def armor_plating(self, my_units, enemy_units):
        for unit in my_units:
            unit.health += 20  # Add 20 HP


    def restore_armor_plating(self, my_units, enemy_units):
        for unit in my_units:
            unit.health -= 20  # Restore original HP


    def adrenaline_rush(self, my_units, enemy_units):
        for unit in my_units:
            unit.action_points += 2  # Add 2 action points


    def restore_adrenaline_rush(self, my_units, enemy_units):
        for unit in my_units:
            unit.action_points -= 2  # Restore original action points


    def quick_feet(self, my_units, enemy_units):
        for unit in my_units:
            unit.max_move += 2  # Increase move range by 2


    def restore_quick_feet(self, my_units, enemy_units):
        for unit in my_units:
            unit.max_move -= 2  # Restore original move range


    def sniper_training(self, my_units, enemy_units):
        for unit in my_units:
            unit.max_attack_range += 2  # Increase attack range by 2


    def restore_sniper_training(self, my_units, enemy_units):
        for unit in my_units:
            unit.max_attack_range -= 2  # Restore original attack range


    def fuel_shortage(self, my_units, enemy_units):
        for unit in my_units:
            unit.move_cost += 1  # Increase move cost by 1


    def restore_fuel_shortage(self, my_units, enemy_units):
        for unit in my_units:
            unit.move_cost -= 1  # Restore original move cost


    def gun_jam(self, my_units, enemy_units):
        for unit in my_units:
            unit.fire_cost += 1  # Increase fire cost by 1


    def restore_gun_jam(self, my_units, enemy_units):
        for unit in my_units:
            unit.fire_cost -= 1  # Restore original fire cost
