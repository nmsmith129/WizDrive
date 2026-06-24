import random

_FORWARD_DELTAS: dict[str, tuple[int, int]] = {
    "north": (0, 1), "east": (1, 0), "south": (0, -1), "west": (-1, 0),
}
_BACKWARD_DELTAS: dict[str, tuple[int, int]] = {
    "north": (0, -1), "east": (-1, 0), "south": (0, 1), "west": (1, 0),
}


class Player:
    def __init__(self, name: str, hp: int | None = None, mp: int | None = None,
                 attack: float = 0.5, strength: int = 1, defense: int = 1,
                 max_hp: int = 10, intelligence: int = 1, mana: int = 1):
        # Initializes the player with a name, attributes, and default position/facing/xp/level.
        self.name = name
        self.location = (0, 0)  # Starting location (x, y)
        self.facing = "north"  # Facing direction: 'north', 'east', 'south', 'west'
        self.attack = attack  # Chance to hit on a strike (0.5 = 50%)
        self.strength = strength  # Base melee damage, added to the equipped weapon's strength
        self.defense = defense  # Subtracted from incoming damage (floored at 1)
        self.max_hp = max_hp
        self.intelligence = intelligence  # Spell effectiveness
        self.mana = mana  # Maximum mana; consumed once spells exist
        self.weapon = None  # Equipped weapon stub; future equipment system fills this slot
        self.hp = max_hp if hp is None else hp  # Current HP, starts full
        self.mp = mana if mp is None else mp  # Current mana, starts full
        self.xp = 0
        self.level = 1

    def __str__(self):
        # Returns a debug-friendly string representation of the player's current state.
        return (f"Player(name={self.name!r}, location={self.location}, hp={self.hp}/{self.max_hp}, "
                f"mp={self.mp}/{self.mana}, attack={self.attack}, strength={self.strength}, "
                f"defense={self.defense}, intelligence={self.intelligence}, xp={self.xp}, level={self.level})")

    def move(self, direction: str):
        # Steps the player forward or backward along their current facing direction.
        if direction == "forward":
            dx, dy = _FORWARD_DELTAS[self.facing]
        elif direction == "backward":
            dx, dy = _BACKWARD_DELTAS[self.facing]
        else:
            raise ValueError(f"Invalid direction: {direction!r}")
        x, y = self.location
        self.location = (x + dx, y + dy)

    def next_pos(self) -> tuple[int, int]:
        # Returns the grid coordinates one step ahead of the player, without moving.
        x, y = self.location
        dx, dy = _FORWARD_DELTAS[self.facing]
        return x + dx, y + dy

    def prev_pos(self) -> tuple[int, int]:
        # Returns the grid coordinates one step behind the player, without moving.
        x, y = self.location
        dx, dy = _BACKWARD_DELTAS[self.facing]
        return x + dx, y + dy

    def turn(self, direction: str):
        # Rotates the player's facing direction left or right by 90 degrees.
        directions = ["north", "east", "south", "west"]
        idx = directions.index(self.facing)
        if direction == "left":
            self.facing = directions[(idx - 1) % 4]
        elif direction == "right":
            self.facing = directions[(idx + 1) % 4]
        else:
            raise ValueError(f"Invalid turn direction: {direction!r}")

    def strike(self, enemy) -> bool:
        # Runs one round of combat: roll to hit, deal strength+weapon damage on a hit, award XP and
        # level up on a kill. A surviving or unhit enemy counter-attacks. Returns True if the enemy died.
        if random.random() < self.attack:
            damage = self.strength + (self.weapon.strength if self.weapon else 0)
            enemy.hp -= damage
            print(f"You hit {enemy.name} for {damage} damage! ({enemy.hp} HP remaining)")
            if enemy.hp <= 0:
                print(f"{enemy.name} is defeated!")
                xp_before = self.xp
                self.xp += enemy.xp
                print(f"You gained {enemy.xp} XP! (Total: {self.xp})")
                levels_gained = (self.xp // 10) - (xp_before // 10)
                if levels_gained > 0:
                    self.level += levels_gained
                    print(f"Level up! You are now level {self.level}!")
                return True
        else:
            print(f"You swing at {enemy.name} and miss!")
        taken = max(1, enemy.attack - self.defense)
        self.hp -= taken
        print(f"{enemy.name} hits back for {taken} damage! (Your HP: {self.hp})")
        if self.hp <= 0:
            print("You have been defeated!")
        return False

    def cast_spell(self, spell, target):
        # Placeholder for spell casting logic; INTELLIGENCE will scale the effect once spells exist.
        print(f"{self.name} casts {spell} on {target}!")

    def use_item(self, item):
        # Placeholder for item usage logic
        print(f"{self.name} uses {item}!")
