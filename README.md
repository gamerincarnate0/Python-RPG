# Python RPG — Combat & Gameplay Guide

This project is a small Python RPG demo with a simple turn-based combat system. This document covers the combat mechanics, controls, and developer information (tests, balance, and tuning).

## Quick Start
- Run the control panel: `python3 main.py`
- Run the tests: `python3 -m unittest discover -s tests -v`

## Controls (Game Control Panel)
- **Display Player Stats**: prints current player stats.
- **Look at Inventory**: lists items in inventory.
- **Generate Selected Tier Enemy**: spawns a random enemy of the chosen tier.
- **Start Combat**: opens the combat window (non-blocking) where you can choose actions.
- **Use Health Potion**: uses a health potion from your inventory (if present).
- **View Combat Log**: opens a window showing the persistent `combat_log.txt` file.
- **Help**: shows this quick-help dialog in the UI.

## Combat Mechanics
- Combat is **turn-based**. The player acts first, then the enemy.
- Player actions:
  - **Attack**: deal damage based on player strength with small variance.
  - **Defend**: halves damage from the next enemy attack.
  - **Use Potion**: consumes a Health Potion from inventory to restore HP.
  - **Flee**: 50% chance to successfully escape.
- Enemy actions are decided by a simple AI (attack, defend, heal).
  - Enemies may carry Health Potions and will often heal if their HP is low.
- Damage resolves as: attack_power - defender_armor/defense with a minimum of 1 damage.

## XP, Gold & Loot
- Enemies grant XP and gold on defeat (scaled by tier and `GameplaySettings.GLOBAL_DIFFICULTY`).
- Enemies have a small chance to drop consumables or equipment as loot.
- Player levelling:
  - XP thresholds are defined in `settings.py` (`GameplaySettings.LEVEL_REQUIREMENTS_BASE` and `LEVEL_SCALAR`).
  - Leveling grants modest stat increases and partially restores HP.

## Balance & Configuration
- Difficulty scaling is controlled by `settings.GameplaySettings.GLOBAL_DIFFICULTY` (1–5).
- Enemy stats and rewards scale with difficulty; tune the multiplier in `enemy.py`.
- Tests exist in `tests/` to verify AI decisions, damage floors, XP/level behavior, and logging.

## Development Notes
- Combat manager: `combat.py` (supports both CLI and Tkinter GUI flows).
- Player state: `player.py` (module-level dict) and `player_helpers.py` (helper functions used by combat & tests).
- Enemy data and generation: `enemy.py`.
- Items: `items.py` (Item class and potions/equipment definitions).
- Tests: `tests/` contains unit tests for AI, player helpers, logging, and balance.
