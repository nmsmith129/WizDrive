# WizDrive - Dependency-Ordered Roadmap

Items are ordered so that every feature appears after all features it depends on.

## Implementation Sequence

### Core Map System
- [x] Map data structure (grid-based representation)
- [x] Map file format (`.lvlmap` support)
- [x] Map validation and error handling
- [x] Multiple map/level support
- [x] Dynamic object placement on maps
- [x] Item descriptions

### Core Entity Classes
- [x] Player class with position tracking
- [x] Player rotation system (facing direction)
- [x] MazeObject class for enemies
- [x] Enemy health/stats system
- [x] Multiple enemy types
- [x] Enemy placement on maps
- [x] Item placement on maps (chests, torches)

### Player Attributes & Progression
- [ ] Player attributes (health, mana, experience, level)
- [x] Health/Hit Points (HP)
- [x] Mana/Spell Points (MP)
- [ ] Experience points (XP)
- [ ] Level system
- [ ] Attribute system (Strength, Intelligence, Dexterity, Constitution, Wisdom, Charisma)
- [ ] Skill system
- [ ] Player inventory system

### Assets — Sprites & Textures
- [ ] Wall textures
- [ ] Character sprites
- [x] Enemy sprites
- [x] Item sprites
- [ ] Character/enemy sprites

### Rendering
- [ ] Basic 3D perspective drawing system
- [ ] Wall rendering at various distances
- [ ] Texture mapping for walls
- [ ] Wall texture variations
- [ ] UI overlay for HUD
- [ ] UI elements/icons

### Core Gameplay Mechanics
- [ ] Movement validation (collision detection with walls)
- [ ] Item effects and properties
- [ ] Item pickup mechanics
- [ ] Item use/equip system
- [ ] Equipment slots (weapon, armor, etc.)
- [ ] Equipment system (weapon, armor, accessories)
- [ ] Item stats and bonuses
- [ ] Equipment weight/carrying capacity
- [ ] Item management (drop, sell, trade)

### Enemy Systems
- [ ] Enemy detection in view
- [ ] Enemy visual representation in first-person view
- [ ] Enemy AI (pathfinding, aggression)

### Combat
- [ ] Melee attack mechanics
- [ ] Attack hit calculation
- [ ] Damage calculation and application
- [ ] Enemy death handling and removal

### Character & Level Progression
- [ ] Character creation/customization
- [ ] Level progression system
- [ ] Level-specific enemy types
- [ ] Level-specific treasure
- [ ] Difficulty scaling per level

### Spells
- [ ] Spell list/grimoire
- [ ] Spell casting mechanics
- [ ] Mana consumption
- [ ] Spell effects (damage, healing, buffs, debuffs)
- [ ] Spell range and targeting

### Visual Polish
- [ ] Sprite animations
- [ ] Particle effects
- [ ] Spell animations
- [ ] Combat animations
- [ ] Screen transitions
- [ ] Weather/atmosphere effects
- [ ] Weather effects
- [ ] Visual effects

### World Objects & Environment
- [ ] Stairs/portals for level transitions
- [ ] Traps and hazards
- [ ] Doors and locked areas
- [ ] Hidden walls/secret passages
- [ ] Teleportation points
- [ ] Monster encounters
- [ ] Treasure rooms
- [ ] Door opening/closing
- [ ] Chest opening/looting
- [ ] Lever/switch activation
- [ ] Environmental damage (lava, poison)

### HUD
- [ ] Minimap
- [ ] Compass/direction indicator
- [ ] Current location display
- [ ] Character stats display (HP, MP, level)
- [ ] Enemy health display
- [ ] Combat log
- [ ] Action queue display
- [ ] Ability/spell shortcuts
- [ ] Active spell/ability indicator
- [ ] Inventory UI display
- [ ] Inventory quick access
- [ ] Item list display
- [ ] Equipment screen
- [ ] Drop/use/equip controls
- [ ] Item filtering/sorting

### Save / Load System
- [ ] Save file format (JSON or binary)
- [ ] Save game functionality
- [ ] Load game functionality
- [ ] Multiple save slots
- [ ] Auto-save system
- [ ] Delete save file option

### NPC & Quest System
- [ ] NPC system
- [ ] NPC AI routines
- [ ] Dialogue trees
- [ ] Quest objectives tracking
- [ ] Quest givers
- [ ] Main quests
- [ ] Side quests
- [ ] Quest rewards
- [ ] Quest journal/log
- [ ] Merchant system
- [ ] Tavern/town hub

### Audio
- [ ] Volume control
- [ ] Background music
- [ ] Movement/footstep sounds
- [ ] Enemy sounds
- [ ] Item pickup sounds
- [ ] Combat sound effects
- [ ] UI interaction sounds
- [ ] Audio settings (master volume, music, SFX)

### Menus & Settings
- [ ] Start new game
- [ ] Load game
- [ ] Settings
- [ ] Graphics settings (resolution, fullscreen)
- [ ] Control rebinding
- [ ] Difficulty settings
- [ ] Language selection
- [ ] Performance optimization options
- [ ] Credits
- [ ] Exit game

### Multiplayer
- [ ] Shared dungeons
- [ ] Player-to-player trading
- [ ] PvP combat
- [ ] Cooperative gameplay
