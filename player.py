class Player:
    def __init__(self, name: str, hp: int, mp: int):
        # Initializes the player with a name, hit points, mana points, and default position/facing/xp.
        self.name = name
        self.location = (0, 0)  # Starting location (x, y)
        self.facing = "north"  # Facing direction: 'north', 'east', 'south', 'west'
        self.hp = hp
        self.mp = mp
        self.xp = 0

    def __str__(self):
        # Returns a debug-friendly string representation of the player's current state.
        return f"Player(name={self.name!r}, location={self.location}, hp={self.hp}, mp={self.mp}, xp={self.xp})"
    
    def move(self, direction: str):
        # Steps the player forward or backward along their current facing direction.
        x, y = self.location
        if direction == "forward":
            if self.facing == "north":
                self.location = (x, y + 1)
            elif self.facing == "east":
                self.location = (x + 1, y)
            elif self.facing == "south":
                self.location = (x, y - 1)
            elif self.facing == "west":
                self.location = (x - 1, y)
        elif direction == "backward":
            if self.facing == "north":
                self.location = (x, y - 1)
            elif self.facing == "east":
                self.location = (x - 1, y)
            elif self.facing == "south":
                self.location = (x, y + 1)
            elif self.facing == "west":
                self.location = (x + 1, y)
        else:
            raise ValueError(f"Invalid direction: {direction!r}")
        
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
        
    def attack(self, target, weapon):
        # Placeholder for attack logic
        print(f"{self.name} attacks {target} with {weapon}!")

    def cast_spell(self, spell, target):
        # Placeholder for spell casting logic
        print(f"{self.name} casts {spell} on {target}!")

    def use_item(self, item):
        # Placeholder for item usage logic
        print(f"{self.name} uses {item}!")