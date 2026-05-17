class Enemy:
    def __init__(self, name: str, hp: int = 1, attack: int = 1, speed: int = 1):
        self.name = name # Name of the enemy, used for identification and display purposes
        self.hp = hp # Hit points, determines how much damage the enemy can take before being defeated
        self.attack = attack #``
        self.speed = speed  # Default speed, can be modified for different enemy types

    def __str__(self):
        return f"{self.name} (HP: {self.hp}, Attack: {self.attack}, Speed: {self.speed})"