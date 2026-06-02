PLAYER_ATTACK: int = 5

_FORWARD_DELTAS: dict[str, tuple[int, int]] = {
    "north": (0, 1), "east": (1, 0), "south": (0, -1), "west": (-1, 0),
}
_BACKWARD_DELTAS: dict[str, tuple[int, int]] = {
    "north": (0, -1), "east": (-1, 0), "south": (0, 1), "west": (1, 0),
}


class Player:
    def __init__(self, name: str, hp: int, mp: int):
        # Initializes the player with a name, hit points, mana points, and default position/facing/xp/level.
        self.name = name
        self.location = (0, 0)  # Starting location (x, y)
        self.facing = "north"  # Facing direction: 'north', 'east', 'south', 'west'
        self.hp = hp
        self.mp = mp
        self.xp = 0
        self.level = 1

    def __str__(self):
        # Returns a debug-friendly string representation of the player's current state.
        return f"Player(name={self.name!r}, location={self.location}, hp={self.hp}, mp={self.mp}, xp={self.xp}, level={self.level})"
    
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
        
    def attack(self, enemy) -> bool:
        # Runs one round of combat against an enemy: the player strikes, awards XP and levels up on a kill,
        # otherwise the enemy counter-attacks. Returns True if the enemy was defeated.
        enemy.hp -= PLAYER_ATTACK
        print(f"You attack {enemy.name} for {PLAYER_ATTACK} damage! ({enemy.hp} HP remaining)")
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
        self.hp -= enemy.attack
        print(f"{enemy.name} hits back for {enemy.attack} damage! (Your HP: {self.hp})")
        if self.hp <= 0:
            print("You have been defeated!")
        return False

    def cast_spell(self, spell, target):
        # Placeholder for spell casting logic
        print(f"{self.name} casts {spell} on {target}!")

    def use_item(self, item):
        # Placeholder for item usage logic
        print(f"{self.name} uses {item}!")