import tkinter as tk

from combat import RARITY_COLORS
from enemy import *
from player import *
from items import *
from functions import *
from settings import *

window = tk.Tk()

window.title("Game Control Panel")
window.geometry("400x800")
window.configure(bg="lightgrey")

enemy = None
enemy_tiers = ["tier1", "tier2", "tier3", "tier4", "tier5"]

button_display_stats = tk.Button(window, text="Display Player Stats", command=lambda: display_player_stats())
button_display_stats.pack(pady=8)

def view_inventory_gui():
    top = tk.Toplevel(window)
    top.title('Inventory')
    txt = tk.Text(top, width=60, height=20)
    txt.pack(padx=6, pady=6)

    inv = player['inventory']
    if not inv:
        txt.insert('end', '(Inventory is empty)')
        txt.config(state='disabled')
        return

    # show list of items and create clickable buttons for details
    frame = tk.Frame(top)
    frame.pack(pady=6)
    row = 0
    for it in inv:
        lbl = tk.Label(frame, text=it.name)
        lbl.grid(row=row, column=0, sticky='w')
        btn = tk.Button(frame, text='Inspect', command=lambda itm=it: inspect_item(itm, top))
        btn.grid(row=row, column=1, padx=6)
        row += 1


def inspect_item(item, parent=None):
    try:
        t = tk.Toplevel(parent or window)
        t.title(item.name)
        color = RARITY_COLORS.get(getattr(item, 'rarity', 'common'), 'black')
        title = tk.Label(t, text=f"{item.name} ({getattr(item, 'rarity', 'common')})", fg=color, font=(None, 12, 'bold'))
        title.pack(pady=6)
        desc = tk.Text(t, height=8, width=50, state='normal')
        desc.insert('end', item.description())
        desc.config(state='disabled')
        desc.pack(padx=8, pady=6)

        btn_frame = tk.Frame(t)
        btn_frame.pack(pady=6)
        if getattr(item, 'item_type', None) == 'equipment':
            eq_btn = tk.Button(btn_frame, text='Equip', command=lambda itm=item: _equip_and_refresh_main(itm, t))
            eq_btn.grid(row=0, column=0, padx=4)
        sell_btn = tk.Button(btn_frame, text='Sell', command=lambda itm=item: _sell_and_refresh_main(itm, t))
        sell_btn.grid(row=0, column=1, padx=4)

        close = tk.Button(t, text='Close', command=t.destroy)
        close.pack(pady=6)
    except Exception:
        # fallback
        TextFuncs.var_speed_print(item.description(), 0.02, 0.04)


def _equip_and_refresh_main(item, window_ref):
    try:
        from player_helpers import equip_item
        ok = equip_item(item)
        if ok:
            TextFuncs.var_speed_print(f"{item.name} equipped.", 0.02, 0.04)
            try:
                window_ref.destroy()
            except Exception:
                pass
            # refresh equipment panel
            try:
                update_equipment_panel()
            except Exception:
                pass
        else:
            TextFuncs.var_speed_print("Could not equip item (no space to unequip or invalid).", 0.02, 0.04)
    except Exception:
        pass


def _sell_and_refresh_main(item, window_ref):
    try:
        from player_helpers import sell_item
        gold = sell_item(item)
        if gold > 0:
            TextFuncs.var_speed_print(f"Sold {item.name} for {gold} gold.", 0.02, 0.04)
            try:
                window_ref.destroy()
            except Exception:
                pass
            try:
                update_equipment_panel()
            except Exception:
                pass
        else:
            TextFuncs.var_speed_print("Could not sell item (not in inventory).", 0.02, 0.04)
    except Exception:
        pass

button_look_inventory = tk.Button(window, text="Look at Inventory", command=view_inventory_gui)
button_look_inventory.pack(pady=8)

# --- Equipped items display + quick actions ---------------------------
equipment_frame = tk.Frame(window, relief='groove', bd=2)
equipment_frame.pack(pady=8, fill='x', padx=8)

def update_equipment_panel():
    # Clear or create labels
    for widget in getattr(update_equipment_panel, 'widgets', []):
        try:
            widget.destroy()
        except Exception:
            pass
    update_equipment_panel.widgets = []

    tk.Label(equipment_frame, text='Equipped:', font=(None, 10, 'bold')).grid(row=0, column=0, sticky='w', padx=4)

    # Weapon
    weapon = player['equipment'].get('weapon')
    wtxt = weapon.name if weapon else '(None)'
    lbl_w = tk.Label(equipment_frame, text=f"Weapon: {wtxt}")
    lbl_w.grid(row=1, column=0, sticky='w', padx=4)
    update_equipment_panel.widgets.append(lbl_w)
    state_w = 'normal' if weapon else 'disabled'
    btn_w = tk.Button(equipment_frame, text='Unequip', state=state_w, command=lambda: unequip_slot('weapon'))
    btn_w.grid(row=1, column=1, padx=4)
    update_equipment_panel.widgets.append(btn_w)

    # Armor
    armor = player['equipment'].get('armor')
    atxt = armor.name if armor else '(None)'
    lbl_a = tk.Label(equipment_frame, text=f"Armor: {atxt}")
    lbl_a.grid(row=2, column=0, sticky='w', padx=4)
    update_equipment_panel.widgets.append(lbl_a)
    state_a = 'normal' if armor else 'disabled'
    btn_a = tk.Button(equipment_frame, text='Unequip', state=state_a, command=lambda: unequip_slot('armor'))
    btn_a.grid(row=2, column=1, padx=4)
    update_equipment_panel.widgets.append(btn_a)

    # Accessory
    acc = player['equipment'].get('accessory')
    txt_acc = acc.name if acc else '(None)'
    lbl_acc = tk.Label(equipment_frame, text=f"Accessory: {txt_acc}")
    lbl_acc.grid(row=3, column=0, sticky='w', padx=4)
    update_equipment_panel.widgets.append(lbl_acc)
    state_acc = 'normal' if acc else 'disabled'
    btn_acc = tk.Button(equipment_frame, text='Unequip', state=state_acc, command=lambda: unequip_slot('accessory'))
    btn_acc.grid(row=3, column=1, padx=4)
    update_equipment_panel.widgets.append(btn_acc)

    # Stats summary
    atk = (player.get('strength', 0) // 2) + player.get('attack_power_bonus', 0)
    arm = player.get('armor_bonus', 0)
    stats_lbl = tk.Label(equipment_frame, text=f"Attack ~ {atk}   Armor bonus: {arm}")
    stats_lbl.grid(row=4, column=0, columnspan=2, pady=4, sticky='w', padx=4)
    update_equipment_panel.widgets.append(stats_lbl)

# Ensure the panel is shown at start
update_equipment_panel()


def unequip_slot(slot):
    """Wrapper for unequipping from the UI that refreshes the equipment panel."""
    try:
        from player_helpers import unequip_item
        ok = unequip_item(slot)
        if ok:
            TextFuncs.var_speed_print(f"Unequipped {slot} to inventory.", 0.02, 0.04)
        else:
            TextFuncs.var_speed_print(f"Could not unequip {slot} (no inventory space or already empty).", 0.02, 0.04)
    except Exception:
        TextFuncs.var_speed_print(f"Error while attempting to unequip {slot}.", 0.02, 0.04)

    try:
        update_equipment_panel()
    except Exception:
        pass

selected_enemy = tk.StringVar(window)
selected_enemy.set(enemy_tiers[0])

enemy_tier_select = tk.OptionMenu(window, selected_enemy, *enemy_tiers)
enemy_tier_select.pack(pady=8)

def generate_and_set_enemy():
    global enemy
    enemy = generate_enemy(selected_enemy.get())
    TextFuncs.var_speed_print(f"Generated random enemy: {enemy.name} with " + TextFuncs.color_text(f"{enemy.health} HP", "red") + " and " + TextFuncs.color_text(f"{enemy.attack_power} AP", "blue"), 0.03, 0.05)


generate_selected_enemy = tk.Button(window, text="Generate Selected Tier Enemy", command=generate_and_set_enemy)
generate_selected_enemy.pack(pady=8)


start_combat_button = tk.Button(window, text="Start Combat", command=lambda: start_combat())
start_combat_button.pack(pady=8)


def start_combat():
    if enemy is None:
        TextFuncs.var_speed_print("No enemy generated. Generate one first.", 0.03, 0.05)
        return
    from combat import Combat
    top = tk.Toplevel(window)
    top.title("Combat")
    top.geometry("520x360")
    top.transient(window)

    def on_combat_end(won: bool):
        if won:
            TextFuncs.var_speed_print("You won the combat!", 0.03, 0.05)
        else:
            TextFuncs.var_speed_print("You were defeated...", 0.03, 0.05)

    combat = Combat(player, enemy)
    # pass a refresh callback so combat tooltips can update the main UI when equipping/selling
    combat.start_gui(top, on_end=on_combat_end, on_refresh=update_equipment_panel)

button_use_health_potion = tk.Button(window, text="Use Health Potion", command=lambda: (health_potion.use(player), TextFuncs.var_speed_print("Health Potion used.", 0.03, 0.05)) if health_potion in player["inventory"] else TextFuncs.var_speed_print("No Health Potion in inventory.", 0.03, 0.05))
button_use_health_potion.pack(pady=8)


HELP_TEXT = (
    "Combat Help:\n"
    "- Generate an enemy and click 'Start Combat' to open the combat window.\n"
    "- In combat: Attack, Defend (halves next incoming damage), Use Potion, or Flee (50% chance).\n"
    "- Enemy AI may heal or defend when hurt; some enemies carry potions.\n"
    "- Victory grants XP, gold, and occasional loot (added to your inventory if space).\n"
    "- Use 'View Combat Log' to see a timestamped log of recent combat outcomes.\n"
)


def view_help():
    top = tk.Toplevel(window)
    top.title('Help')
    txt = tk.Text(top, wrap='word', height=18, width=80)
    txt.insert('end', HELP_TEXT)
    txt.configure(state='disabled')
    txt.pack(padx=8, pady=8)


def view_combat_log():
    try:
        with open('combat_log.txt', 'r', encoding='utf-8') as fh:
            content = fh.read()
    except FileNotFoundError:
        content = '(No combat log entries found yet)'

    top = tk.Toplevel(window)
    top.title('Combat Log')
    txt = tk.Text(top, wrap='word', height=30, width=80)
    txt.insert('end', content)
    txt.configure(state='disabled')
    txt.pack(padx=8, pady=8)


button_view_log = tk.Button(window, text="View Combat Log", command=view_combat_log)
button_view_log.pack(pady=8)

button_help = tk.Button(window, text="Help", command=view_help)
button_help.pack(pady=8)

window.mainloop()