# WizDrive - Feature Roadmap

A first-person dungeon crawler game inspired by Wizardry, built with Python and Pygame.

---

## Phase 1: Core Gameplay Foundation ⚙️

### Player System
- [x] Player class with position tracking
- [x] Player rotation system (facing direction)
- [ ] Movement validation (collision detection with walls)
- [ ] Player attributes (health, mana, experience, level)
- [ ] Player inventory system
- [ ] Character creation/customization

### Map System
- [x] Map data structure (grid-based representation)
- [ ] Map file format (`.lvlmap` support)
- [ ] Map validation and error handling
- [ ] Multiple map/level support
- [ ] Dynamic object placement on maps

### First-Person View Rendering
- [ ] Basic 3D perspective drawing system
- [ ] Wall rendering at various distances
- [ ] Texture mapping for walls
- [ ] Animated wall transitions
- [ ] Lighting/shadow system
- [ ] UI overlay for HUD

---

## Phase 2: Combat & Interaction 🎯

### Combat System
- [ ] Enemy detection in view
- [ ] Melee attack mechanics
- [ ] Attack hit calculation
- [ ] Damage calculation and application
- [ ] Enemy death handling and removal
- [ ] Combat animations

### Enemy System
- [ ] MazeObject class for enemies
- [ ] Enemy placement on maps
- [ ] Enemy AI (pathfinding, aggression)
- [ ] Enemy health/stats system
- [ ] Multiple enemy types
- [ ] Enemy visual representation in first-person view

### Item Interaction
- [ ] Item placement on maps (chests, torches)
- [ ] Item pickup mechanics
- [ ] Item use/equip system
- [ ] Item effects and properties
- [ ] Equipment slots (weapon, armor, etc.)

---

## Phase 3: Player Progression 📊

### Character Stats & Attributes
- [ ] Health/Hit Points (HP)
- [ ] Mana/Spell Points (MP)
- [ ] Experience points (XP)
- [ ] Level system
- [ ] Attribute system (Strength, Intelligence, Dexterity, Constitution, Wisdom, Charisma)
- [ ] Skill system

### Magic/Spell System
- [ ] Spell list/grimoire
- [ ] Spell casting mechanics
- [ ] Mana consumption
- [ ] Spell effects (damage, healing, buffs, debuffs)
- [ ] Spell animations
- [ ] Spell range and targeting

### Equipment & Inventory
- [ ] Inventory UI display
- [ ] Equipment system (weapon, armor, accessories)
- [ ] Item stats and bonuses
- [ ] Equipment weight/carrying capacity
- [ ] Item management (drop, sell, trade)

---

## Phase 4: Dungeon Exploration 🗺️

### Multiple Levels
- [ ] Level progression system
- [ ] Stairs/portals for level transitions
- [ ] Level-specific enemy types
- [ ] Level-specific treasure
- [ ] Difficulty scaling per level

### Dungeon Features
- [ ] Traps and hazards
- [ ] Doors and locked areas
- [ ] Hidden walls/secret passages
- [ ] Teleportation points
- [ ] Monster encounters
- [ ] Treasure rooms

### Environmental Interaction
- [ ] Door opening/closing
- [ ] Chest opening/looting
- [ ] Lever/switch activation
- [ ] Environmental damage (lava, poison)
- [ ] Weather/atmosphere effects

---

## Phase 5: User Interface & Menus 🖥️

### Main Menu
- [ ] Start new game
- [ ] Load game
- [ ] Settings
- [ ] Credits
- [ ] Exit game

### In-Game HUD
- [ ] Character stats display (HP, MP, level)
- [ ] Minimap
- [ ] Compass/direction indicator
- [ ] Current location display
- [ ] Inventory quick access
- [ ] Active spell/ability indicator

### Inventory UI
- [ ] Item list display
- [ ] Equipment screen
- [ ] Item descriptions
- [ ] Drop/use/equip controls
- [ ] Item filtering/sorting

### Combat UI
- [ ] Enemy health display
- [ ] Combat log
- [ ] Ability/spell shortcuts
- [ ] Action queue display

---

## Phase 6: Save & Configuration 💾

### Save System
- [ ] Save game functionality
- [ ] Load game functionality
- [ ] Multiple save slots
- [ ] Save file format (JSON or binary)
- [ ] Auto-save system
- [ ] Delete save file option

### Settings/Configuration
- [ ] Graphics settings (resolution, fullscreen)
- [ ] Audio settings (master volume, music, SFX)
- [ ] Control rebinding
- [ ] Difficulty settings
- [ ] Language selection
- [ ] Performance optimization options

---

## Phase 7: Audio & Visuals 🎨

### Sound System
- [ ] Background music
- [ ] Combat sound effects
- [ ] Movement/footstep sounds
- [ ] Enemy sounds
- [ ] Item pickup sounds
- [ ] UI interaction sounds
- [ ] Volume control

### Graphics Enhancements
- [ ] Sprite animations
- [ ] Wall texture variations
- [ ] Character/enemy sprites
- [ ] Particle effects
- [ ] Screen transitions
- [ ] Weather effects

### Art Assets
- [ ] Character sprites
- [ ] Enemy sprites
- [ ] Item sprites
- [ ] Wall textures
- [ ] UI elements/icons
- [ ] Visual effects

---

## Phase 8: Advanced Features 🚀

### NPCs & Dialogue
- [ ] NPC system
- [ ] Dialogue trees
- [ ] Quest givers
- [ ] Tavern/town hub
- [ ] Merchant system
- [ ] NPC AI routines

### Quest System
- [ ] Main quests
- [ ] Side quests
- [ ] Quest objectives tracking
- [ ] Quest rewards
- [ ] Quest journal/log

### Multiplayer (Optional)
- [ ] Shared dungeons
- [ ] Player-to-player trading
- [ ] PvP combat
- [ ] Cooperative gameplay

---

## Current Status 📝

### Completed
- Basic project structure
- Player movement and rotation
- Map loading and parsing
- First-person view rendering system
- MazeObject class for entities
- Constants and configuration

### In Progress
- Enemy placement and rendering
- First-person view visual refinement

### Not Started
- All features in Phases 1-8 (except listed above)

---

## Notes & Considerations

- **Wizardry Inspiration**: Focus on classic first-person perspective exploration, grid-based movement, and tactical combat
- **Performance**: Optimize rendering for smooth first-person experience
- **Modding**: Consider making maps and assets easily modifiable
- **Testing**: Comprehensive testing needed as features are added
- **Documentation**: Keep code well-documented for future maintainability

---

## Milestones

1. **Playable Demo**: Core movement, basic combat, enemies
2. **Alpha**: Multiple levels, inventory system, basic magic
3. **Beta**: Full dungeon, all mechanics implemented
4. **Release**: Polish, optimization, audio/visuals complete
