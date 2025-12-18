import tkinter as tk

from enemy import *
from player import *
from items import *
from functions import *
from settings import *

window = tk.Tk()

window.title("Game Control Panel")
window.geometry("400x500")
window.configure(bg="lightgrey")

enemy = None

button_display_stats = tk.Button(window, text="Display Player Stats", command=lambda: display_player_stats())
button_display_stats.pack(pady=8)

button_look_inventory = tk.Button(window, text="Look at Inventory", command=lambda: display_only_inventory())
button_look_inventory.pack(pady=8)

button_generate_enemy_t1 = tk.Button(window, text="Generate Random Tier 1 Enemy", command=lambda: TextFuncs.var_speed_print(f"Generated random enemy: {enemy.name} with " + TextFuncs.color_text(f"{enemy.health} HP", "red") + " and " + TextFuncs.color_text(f"{enemy.attack_power} AP", "blue"), 0.03, 0.05) if (enemy := generate_enemy("tier1")) else None)
button_generate_enemy_t1.pack(pady=8)

button_generate_enemy_t2 = tk.Button(window, text="Generate Random Tier 2 Enemy", command=lambda: TextFuncs.var_speed_print(f"Generated random enemy: {enemy.name} with " + TextFuncs.color_text(f"{enemy.health} HP", "red") + " and " + TextFuncs.color_text(f"{enemy.attack_power} AP", "blue"), 0.03, 0.05) if (enemy := generate_enemy("tier2")) else None)
button_generate_enemy_t2.pack(pady=8)

button_generate_enemy_t3 = tk.Button(window, text="Generate Random Tier 3 Enemy", command=lambda: TextFuncs.var_speed_print(f"Generated random enemy: {enemy.name} with " + TextFuncs.color_text(f"{enemy.health} HP", "red") + " and " + TextFuncs.color_text(f"{enemy.attack_power} AP", "blue"), 0.03, 0.05) if (enemy := generate_enemy("tier3")) else None)
button_generate_enemy_t3.pack(pady=8)

button_generate_enemy_t4 = tk.Button(window, text="Generate Random Tier 4 Enemy", command=lambda: TextFuncs.var_speed_print(f"Generated random enemy: {enemy.name} with " + TextFuncs.color_text(f"{enemy.health} HP", "red") + " and " + TextFuncs.color_text(f"{enemy.attack_power} AP", "blue"), 0.03, 0.05) if (enemy := generate_enemy("tier4")) else None)
button_generate_enemy_t4.pack(pady=8)

button_generate_enemy_t5 = tk.Button(window, text="Generate Random Tier 5 Enemy", command=lambda: TextFuncs.var_speed_print(f"Generated random enemy: {enemy.name} with " + TextFuncs.color_text(f"{enemy.health} HP", "red") + " and " + TextFuncs.color_text(f"{enemy.attack_power} AP", "blue"), 0.03, 0.05) if (enemy := generate_enemy("tier5")) else None)
button_generate_enemy_t5.pack(pady=8)

button_give_health_potion = tk.Button(window, text="Give Health Potion", command=lambda: (player["inventory"].append(health_potion), TextFuncs.var_speed_print("Health Potion added to inventory.", 0.03, 0.05)))
button_give_health_potion.pack(pady=8)

button_use_health_potion = tk.Button(window, text="Use Health Potion", command=lambda: (health_potion.use(player), TextFuncs.var_speed_print("Health Potion used.", 0.03, 0.05)) if health_potion in player["inventory"] else TextFuncs.var_speed_print("No Health Potion in inventory.", 0.03, 0.05))
button_use_health_potion.pack(pady=8)

window.mainloop()