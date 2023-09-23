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
                "name": "Team Commander's Insight",
                "description": "Swap the positions of any two units on your team.",
                "type": "good",
            },
            {
                "func": self.remote_hack_team,
                "restore": self.restore_remote_hack_team,
                "name": "Team Remote Hack",
                "description": "Take control of enemy mechanical units for one turn.",
                "type": "good",
            },
            {
                "func": self.divine_intervention_team,
                "restore": self.restore_divine_intervention_team,
                "name": "Team Divine Intervention",
                "description": "All units are healed back to full HP.",
                "type": "good",
            },
            {
                "func": self.weapon_jam_team,
                "restore": self.restore_weapon_jam_team,
                "name": "Team Weapon Jam",
                "description": "All units can't attack for the next turn.",
                "type": "bad",
            },
            {
                "func": self.skill_mastery_team,
                "restore": self.restore_skill_mastery_team,
                "name": "Team Skill Mastery",
                "description": "All units gain double damage or defense for the next turn.",
                "type": "good",
            },
            {
                "func": self.artifact_team,
                "restore": self.restore_artifact_team,
                "name": "Team Artifact",
                "description": "A powerful artifact affects all units on the map, giving a additionnal action point.",
                "type": "good",
            },
            {
                "func": self.sabotage_team,
                "restore": self.restore_sabotage_team,
                "name": "Team Sabotage",
                "description": "All units are disabled for one turn.",
                "type": "bad",
            },
            {
                "func": self.equipment_malfunction_team,
                "restore": self.restore_equipment_malfunction_team,
                "name": "Team Equipment Malfunction",
                "description": "All units' weapons become less effective for a turn.",
                "type": "bad",
            },
            {
                "func": self.friendly_fire_team,
                "restore": self.restore_friendly_fire_team,
                "name": "Team Friendly Fire",
                "description": "Units on your team accidentally attack other units on your team.",
                "type": "bad",
            },
            {
                "func": self.team_damage_boost,
                "restore": self.restore_team_damage_boost,
                "name": "Team Damage Boost",
                "description": "Increases the damage of all units on your team for one turn.",
                "type": "good",
            },
            {
                "func": self.team_armor_plating,
                "restore": self.restore_team_armor_plating,
                "name": "Team Armor Plating",
                "description": "Increases the HP of all units on your team for one turn.",
                "type": "good",
            },
            {
                "func": self.team_adrenaline_rush,
                "restore": self.restore_team_adrenaline_rush,
                "name": "Team Adrenaline Rush",
                "description": "All units on your team get extra action points (AP) for one turn.",
                "type": "good",
            },
            {
                "func": self.team_quick_feet,
                "restore": self.restore_team_quick_feet,
                "name": "Team Quick Feet",
                "description": "Increases the Max Move Range of all units on your team for one turn.",
                "type": "good",
            },
            {
                "func": self.team_sniper_training,
                "restore": self.restore_team_sniper_training,
                "name": "Team Sniper Training",
                "description": "Increases the Max Attack Range of all units on your team for one turn.",
                "type": "good",
            },
            {
                "func": self.team_fuel_shortage,
                "restore": self.restore_team_fuel_shortage,
                "name": "Team Fuel Shortage",
                "description": "Increases the Move Cost of all units on your team for one turn.",
                "type": "bad",
            },
            {
                "func": self.team_gun_jam,
                "restore": self.restore_team_gun_jam,
                "name": "Team Gun Jam",
                "description": "Increases the Fire Cost of all units on your team for one turn.",
                "type": "bad",
            },
        ]

    def random_event(self):
        event = random.choice(self.events)
        self.player1.apply_event(event["func"], event["restore"])
        self.player2.apply_event(event["func"], event["restore"])
        return event  # Return the event and restore function


# --- Good Events ---


    def commanders_insight_team(self, my_units, enemy_units):
        # Randomly select one unit from each side
        unit1 = random.choice(my_units)
        unit2 = random.choice(enemy_units)

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

        # Clear the swapped_units attribute
        self.swapped_units = None


    def remote_hack_team(self, my_units, enemy_units):
        # Randomly select one unit from my side and one unit from the enemy side
        my_unit = random.choice(my_units)
        enemy_unit = random.choice(enemy_units)

        # Swap the control (player attribute)
        my_unit.player, enemy_unit.player = enemy_unit.player, my_unit.player

        # Store the switched units for restoring later
        self.switched_unit_my_side = my_unit
        self.switched_unit_enemy_side = enemy_unit

    def restore_remote_hack_team(self, my_units, enemy_units):
        # Revert the control swap
        if self.switched_unit_my_side and self.switched_unit_enemy_side:
            self.switched_unit_my_side.player, self.switched_unit_enemy_side.player = \
                self.switched_unit_enemy_side.player, self.switched_unit_my_side.player

            # Clear the switched_unit attributes
            self.switched_unit_my_side = None
            self.switched_unit_enemy_side = None


    def divine_intervention_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.original_hp = unit.health
            unit.health = unit.max_hp


    def restore_divine_intervention_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.health = unit.original_hp


    def skill_mastery_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.damage *= 2


    def restore_skill_mastery_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.damage /= 2


    def artifact_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.action_points += 1


    def restore_artifact_team(self, my_units, enemy_units):
        for unit in my_units:
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
            unit.damage *= 0.5


    def restore_equipment_malfunction_team(self, my_units, enemy_units):
        for unit in my_units:
            unit.damage *= 2


    def friendly_fire_team(self, my_units, enemy_units):
        for unit1, unit2 in zip(my_units, enemy_units):
            unit2.health -= unit1.damage
            if unit2.health <= 0:
                unit2.health = 1


    def restore_friendly_fire_team(self, my_units, enemy_units):
        for unit, original_hp in my_units:
            unit.health = unit.original_hp


    def damage_boost(self, my_units, enemy_units):
        for unit in my_units:
            unit.Damage *= 1.5  # 50% increase in damage


    def restore_damage_boost(self, my_units, enemy_units):
        for unit in my_units:
            unit.Damage /= 1.5  # Restore original damage


    def armor_plating(self, my_units, enemy_units):
        for unit in my_units:
            unit.health += 20  # Add 20 HP


    def restore_armor_plating(self, my_units, enemy_units):
        for unit in my_units:
            unit.health -= 20  # Restore original HP


    def adrenaline_rush(self, my_units, enemy_units):
        for unit in my_units:
            unit.AP += 2  # Add 2 action points


    def restore_adrenaline_rush(self, my_units, enemy_units):
        for unit in my_units:
            unit.AP -= 2  # Restore original action points


    def quick_feet(self, my_units, enemy_units):
        for unit in my_units:
            unit.Max_Move_Range += 2  # Increase move range by 2


    def restore_quick_feet(self, my_units, enemy_units):
        for unit in my_units:
            unit.Max_Move_Range -= 2  # Restore original move range


    def sniper_training(self, my_units, enemy_units):
        for unit in my_units:
            unit.Max_Attack_Range += 2  # Increase attack range by 2


    def restore_sniper_training(self, my_units, enemy_units):
        for unit in my_units:
            unit.Max_Attack_Range -= 2  # Restore original attack range


    def fuel_shortage(self, my_units, enemy_units):
        for unit in my_units:
            unit.Move_Cost += 1  # Increase move cost by 1


    def restore_fuel_shortage(self, my_units, enemy_units):
        for unit in my_units:
            unit.Move_Cost -= 1  # Restore original move cost


    def gun_jam(self, my_units, enemy_units):
        for unit in my_units:
            unit.Fire_Cost += 1  # Increase fire cost by 1


    def restore_gun_jam(self, my_units, enemy_units):
        for unit in my_units:
            unit.Fire_Cost -= 1  # Restore original fire cost
