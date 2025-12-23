import tkinter as tk
import math

from combat import RARITY_COLORS, RARITY_EMOJIS
from enemy import *
from player import *
from items import *
from functions import *
from settings import *
from plugins.loader import load_plugins

PLUGIN_REGISTRY = load_plugins()

window = tk.Tk()

window.title("Game Control Panel")
if GraphicalSettings.FULLSCREEN:
    window.state('zoomed')
else:
    window.geometry(f"{GraphicalSettings.RESOLUTION[0]}x{GraphicalSettings.RESOLUTION[1]}")
window.configure(bg="lightgrey")

# Exit handler: autosave on exit
def on_exit():
    try:
        ok = save_game()
        if ok:
            TextFuncs.var_speed_print('Game autosaved.', 0.02, 0.04)
        else:
            TextFuncs.var_speed_print('Failed to save game on exit.', 0.02, 0.04)
    except Exception:
        TextFuncs.var_speed_print('Error while autosaving on exit.', 0.02, 0.04)
    try:
        window.destroy()
    except Exception:
        pass

# bind protocol
window.protocol('WM_DELETE_WINDOW', on_exit)

enemy = None

button_display_stats = tk.Button(window, text="Display Player Stats", command=lambda: display_player_stats())
button_display_stats.pack(pady=8)

def _clear_content_frame():
    try:
        children = list(content_frame.winfo_children())
    except Exception:
        # Tk may have been destroyed (tests may call on_exit); fail-safe to avoid Tk errors
        return
    for w in children:
        try:
            w.destroy()
        except Exception:
            pass
    content_frame.is_inventory_view = False


def view_inventory_gui(parent_frame=None):
    """Render the inventory inside the main `content_frame`. Keeps compatibility if a parent_frame is passed."""
    # render into the provided parent_frame (if given) or the global content_frame
    parent = parent_frame or content_frame
    _clear_content_frame()
    parent.is_inventory_view = True

    txt_frame = tk.Frame(parent)
    txt_frame.pack(fill='both', expand=True, padx=6, pady=6)

    inv = player['inventory']
    if not inv:
        lbl = tk.Label(txt_frame, text='(Inventory is empty)')
        lbl.pack()
        return

    # show list of items and create clickable buttons for details
    frame = tk.Frame(txt_frame)
    frame.pack(pady=6)
    row = 0
    for it in inv:
        lbl = tk.Label(frame, text=it.name)
        lbl.grid(row=row, column=0, sticky='w')
        btn = tk.Button(frame, text='Inspect', command=lambda itm=it: inspect_item(itm, frame))
        btn.grid(row=row, column=1, padx=6)
        row += 1


def inspect_item(item, parent=None):
    """Show an item's details. If `parent` is a Frame inside `content_frame` then render
    the inspection as an embedded panel; otherwise fall back to a Toplevel."""
    try:
        if parent is not None and getattr(parent, 'winfo_exists', lambda: False)():
            # render inline panel inside parent
            pnl = tk.Frame(parent, relief='groove', bd=1)
            pnl.grid(row=0, column=2, padx=6, sticky='n')
            pnl.title = item.name  # lightweight metadata for tests
            color = RARITY_COLORS.get(getattr(item, 'rarity', 'common'), 'black')
            title = tk.Label(pnl, text=f"{item.name} ({getattr(item, 'rarity', 'common')})", fg=color, font=(None, 12, 'bold'))
            title.pack(pady=6)
            desc = tk.Text(pnl, height=8, width=50, state='normal')
            desc.insert('end', item.description())
            desc.config(state='disabled')
            desc.pack(padx=8, pady=6)

            btn_frame = tk.Frame(pnl)
            btn_frame.pack(pady=6)
            if getattr(item, 'item_type', None) == 'equipment':
                eq_btn = tk.Button(btn_frame, text='Equip', command=lambda itm=item: _equip_and_refresh_main(itm, pnl))
                eq_btn.grid(row=0, column=0, padx=4)
            sell_btn = tk.Button(btn_frame, text='Sell', command=lambda itm=item: _sell_and_refresh_main(itm, pnl))
            sell_btn.grid(row=0, column=1, padx=4)

            close = tk.Button(pnl, text='Close', command=pnl.destroy)
            close.pack(pady=6)
            return

        # fallback to previous behaviour (separate window)
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

            # If equip was done from the Inventory view, refresh it (close + reopen)
            try:
                parent = getattr(window_ref, 'master', None)
                if parent and getattr(parent, 'winfo_exists', lambda: False)() and (
                    getattr(parent, 'title', lambda: '')() == 'Inventory' or getattr(parent, 'is_inventory_view', False)
                ):
                    try:
                        parent.destroy()
                    except Exception:
                        pass
                    try:
                        view_inventory_gui()
                    except Exception:
                        pass
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

def rest_and_heal():
    """Rest at an inn to heal and recover."""
    try:
        cost_to_heal = player['max_health'] - player['health']
        if player['gold'] < cost_to_heal:
            TextFuncs.var_speed_print("You don't have enough gold to heal.", 0.02, 0.04)
            return
        elif player['health'] >= player['max_health']:
            TextFuncs.var_speed_print("You are already fully healed.", 0.02, 0.04)
            return
        elif player.get('health', 0) <= 0:
            TextFuncs.var_speed_print("You are already dead.", 0.02, 0.04)
            return
        player['health'] = player['max_health']
        player['gold'] -= cost_to_heal
        TextFuncs.var_speed_print(f"You have been fully healed for {cost_to_heal} gold.", 0.02, 0.04)
    except Exception:
        pass

# --- Navigation: single-window content area --------------------------------
nav_frame = tk.Frame(window)
nav_frame.pack(pady=6)

nav_buttons = {}

btn_inventory = tk.Button(nav_frame, text='Inventory', command=lambda: view_inventory_gui())
btn_inventory.grid(row=0, column=0, padx=4)
nav_buttons['inventory'] = btn_inventory

btn_start = tk.Button(nav_frame, text='Start Combat (Generate Enemy)', command=lambda: start_combat())
btn_start.grid(row=0, column=1, padx=4)
nav_buttons['start'] = btn_start

btn_rest = tk.Button(nav_frame, text='Rest and Heal', command=lambda: rest_and_heal())
btn_rest.grid(row=0, column=2, padx=4)
nav_buttons['rest'] = btn_rest

btn_log = tk.Button(nav_frame, text='Combat Log', command=lambda: view_combat_log_in_frame())
btn_log.grid(row=0, column=3, padx=4)
nav_buttons['log'] = btn_log

btn_help = tk.Button(nav_frame, text='Help', command=lambda: view_help_in_frame())
btn_help.grid(row=0, column=4, padx=4)
nav_buttons['help'] = btn_help

# content frame - all views render into here
content_frame = tk.Frame(window, relief='flat')
content_frame.pack(padx=8, pady=6, fill='both', expand=True)

# keep a flag to indicate whether content_frame is showing inventory
content_frame.is_inventory_view = False

# --- Global message box (replaces terminal var_speed_print usage) ----------------
messages_frame = tk.Frame(window, relief='groove', bd=2)
messages_frame.pack(padx=8, pady=6, fill='x')

# Controls frame: Clear, Save, Max lines
_msg_ctrl = tk.Frame(messages_frame)
_msg_ctrl.pack(fill='x', padx=4, pady=(4,0))

btn_clear = tk.Button(_msg_ctrl, text='Clear', command=lambda: clear_messages())
btn_clear.pack(side='left')

btn_save = tk.Button(_msg_ctrl, text='Save Log', command=lambda: save_messages_to_file())
btn_save.pack(side='left', padx=6)

tk.Label(_msg_ctrl, text='Max Lines:').pack(side='left', padx=(12,4))
_max_var = tk.IntVar(value=500)
spin_max = tk.Spinbox(_msg_ctrl, from_=10, to=10000, increment=10, width=6, textvariable=_max_var)
spin_max.pack(side='left')

messages_box = tk.Text(messages_frame, height=6, wrap='word', state='disabled')
messages_box.pack(fill='both', expand=True, padx=4, pady=4)

# maximum number of lines to retain in the message box
max_messages_lines = _max_var.get()

# When the spinbox changes, update the global
def _on_max_change(*a):
    global max_messages_lines
    try:
        max_messages_lines = int(_max_var.get())
    except Exception:
        max_messages_lines = 500

# set a trace to update when spinbox changes (some tk versions may not call command reliably)
try:
    _max_var.trace_add('write', _on_max_change)
except Exception:
    try:
        _max_var.trace('w', _on_max_change)
    except Exception:
        pass

# function to append messages to the messages_box (optional rarity for color)
def log_message(text, rarity=None):
    # compute small emoji/icon based on rarity or text
    try:
        from combat import message_icon, RARITY_COLORS
        icon = message_icon(text, rarity)
    except Exception:
        icon = ''
        RARITY_COLORS = {}

    final_text = f"{icon} {text}" if icon else text

    try:
        messages_box.configure(state='normal')
        start_index = messages_box.index('end')
        messages_box.insert('end', final_text + '\n')

        if rarity:
            tag = f"rarity_{rarity}"
            if tag not in messages_box.tag_names():
                color = RARITY_COLORS.get(rarity, 'black')
                try:
                    messages_box.tag_configure(tag, foreground=color, font=(None, 10, 'bold'))
                except Exception:
                    messages_box.tag_configure(tag, foreground=color)
            messages_box.tag_add(tag, start_index, f"{start_index} lineend")

        # Trim if too many lines
        try:
            lines = int(messages_box.index('end-1c').split('.')[0])
            if lines > max_messages_lines:
                to_delete = lines - max_messages_lines
                # delete earliest lines
                messages_box.delete('1.0', f"{to_delete + 1}.0")
        except Exception:
            pass

        messages_box.see('end')
        messages_box.configure(state='disabled')
    except Exception:
        # last-resort fallback to terminal to avoid silent failures
        try:
            from functions import TextFuncs
            TextFuncs.var_speed_print(text, 0.0, 0.0)
        except Exception:
            pass


def clear_messages():
    try:
        messages_box.configure(state='normal')
        messages_box.delete('1.0', 'end')
        messages_box.configure(state='disabled')
    except Exception:
        pass


def save_messages_to_file(path='messages_log.txt'):
    try:
        messages_box.configure(state='normal')
        content = messages_box.get('1.0', 'end').rstrip('\n')
        messages_box.configure(state='disabled')
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(content)
        # notify user
        try:
            log_message(f"Saved messages to {path}.")
        except Exception:
            pass
        return True
    except Exception:
        return False

# register the global logger so TextFuncs.var_speed_print sends to the GUI
try:
    from functions import TextFuncs
    TextFuncs.set_gui_logger(log_message)
except Exception:
    pass

# hide the old standalone button (kept for tests compatibility but not shown)
# button_look_inventory = tk.Button(window, text="Look at Inventory", command=view_inventory_gui)
# button_look_inventory.pack(pady=8)

# --- Equipped items display + quick actions ---------------------------
equipment_frame = tk.Frame(window, relief='groove', bd=2)
equipment_frame.pack(pady=8, fill='x', padx=8)

# small slot emoji map for quick recognition
SLOT_EMOJIS = {
    'weapon': '⚔️',
    'armor': '🛡️',
    'accessory': '📿',
}


def format_equipment_text(slot, item):
    """Return a nicely formatted label text for the equipment slot including emojis and rarity."""
    slot_icon = SLOT_EMOJIS.get(slot, '')
    if item:
        rarity_icon = RARITY_EMOJIS.get(getattr(item, 'rarity', 'common'), '')
        space = ' ' if slot_icon else ''
        rspace = ' ' if rarity_icon else ''
        return f"{slot.capitalize()}: {slot_icon}{space}{item.name}{rspace}{rarity_icon}"
    else:
        space = ' ' if slot_icon else ''
        return f"{slot.capitalize()}: {slot_icon}{space}(None)"


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
    wtxt = format_equipment_text('weapon', weapon)
    lbl_w = tk.Label(equipment_frame, text=wtxt)
    lbl_w.grid(row=1, column=0, sticky='w', padx=4)
    update_equipment_panel.widgets.append(lbl_w)
    state_w = 'normal' if weapon else 'disabled'
    btn_w = tk.Button(equipment_frame, text='Unequip', state=state_w, command=lambda: unequip_slot('weapon'))
    btn_w.grid(row=1, column=1, padx=4)
    update_equipment_panel.widgets.append(btn_w)

    # Armor
    armor = player['equipment'].get('armor')
    atxt = format_equipment_text('armor', armor)
    lbl_a = tk.Label(equipment_frame, text=atxt)
    lbl_a.grid(row=2, column=0, sticky='w', padx=4)
    update_equipment_panel.widgets.append(lbl_a)
    state_a = 'normal' if armor else 'disabled'
    btn_a = tk.Button(equipment_frame, text='Unequip', state=state_a, command=lambda: unequip_slot('armor'))
    btn_a.grid(row=2, column=1, padx=4)
    update_equipment_panel.widgets.append(btn_a)

    # Accessory
    acc = player['equipment'].get('accessory')
    txt_acc = format_equipment_text('accessory', acc)
    lbl_acc = tk.Label(equipment_frame, text=txt_acc)
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



'''start_combat_button = tk.Button(window, text="Start Combat (Generate Enemy)", command=lambda: start_combat())
start_combat_button.pack(pady=8)'''

# Save / Load buttons
save_btn = tk.Button(window, text='Save Game', command=lambda: (save_game() and TextFuncs.var_speed_print('Game saved.', 0.02, 0.04)) or TextFuncs.var_speed_print('Failed to save game.', 0.02, 0.04))
save_btn.pack(pady=8)
load_btn = tk.Button(window, text='Load Game', command=lambda: (load_game() and (update_equipment_panel(), TextFuncs.var_speed_print('Game loaded.', 0.02, 0.04))) or TextFuncs.var_speed_print('No save file found or failed to load.', 0.02, 0.04))
load_btn.pack(pady=8)


def disable_nav(disabled=True):
    try:
        for btn in nav_buttons.values():
            btn.configure(state='disabled' if disabled else 'normal')
    except Exception:
        pass


def start_combat():
    # Prevent combat if player is dead
    if player.get('health', 0) <= 0:
        show_death_screen()
        return

    from combat import Combat
    # Generate an enemy scaled to player level
    try:
        from enemy import generate_enemy_for_player
        new_enemy = generate_enemy_for_player(player.get('level', 1))
    except Exception:
        TextFuncs.var_speed_print("Failed to generate enemy.", 0.03, 0.05)
        return

    # Render combat inside content_frame as a modal-like panel
    _clear_content_frame()
    disable_nav(True)

    try:
        combat_frame = tk.Frame(content_frame, relief='groove', bd=2)
        combat_frame.pack(fill='both', expand=True, padx=6, pady=6)
    except Exception:
        disable_nav(False)
        return

    def on_combat_end(won: bool):
        disable_nav(False)
        if won:
            TextFuncs.var_speed_print("You won the combat!", 0.03, 0.05)
        else:
            # Player death consequences
            TextFuncs.var_speed_print("You were defeated...", 0.03, 0.05)
            player['experience'] = 0
            player['level'] = max(1, player['level'] - 1)
            show_death_screen()
            return
        try:
            combat_frame.after(500, lambda: _clear_content_frame())
        except Exception:
            pass

    combat = Combat(player, new_enemy)
    combat.start_gui(combat_frame, on_end=on_combat_end, on_refresh=update_equipment_panel)

def show_death_screen():
    _clear_content_frame()
    disable_nav(True)
    death_frame = tk.Frame(content_frame, relief='ridge', bd=3, bg='black')
    death_frame.pack(fill='both', expand=True, padx=30, pady=30)
    lbl = tk.Label(death_frame, text="You have died!", fg='red', bg='black', font=(None, 20, 'bold'))
    lbl.pack(pady=20)
    info = tk.Label(death_frame, text=f"Level reset to {player['level']}, XP set to 0.", fg='white', bg='black', font=(None, 14))
    info.pack(pady=10)
    btn = tk.Button(death_frame, text="Continue", font=(None, 14, 'bold'), command=lambda: (death_frame.destroy(), disable_nav(False), player.update({'health': player['max_health']})))
    btn.pack(pady=20)

HELP_TEXT = (
    "Combat Help:\n"
    "- Click 'Start Combat' to generate an enemy appropriate for your level and open the combat window.\n"
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
        from functions import get_data_dir
        log_path = os.path.join(get_data_dir(), 'combat_log.txt')
        with open(log_path, 'r', encoding='utf-8') as fh:
            content = fh.read()
    except FileNotFoundError:
        content = '(No combat log entries found yet)'

    top = tk.Toplevel(window)
    top.title('Combat Log')
    txt = tk.Text(top, wrap='word', height=30, width=80)
    txt.insert('end', content)
    txt.configure(state='disabled')
    txt.pack(padx=8, pady=8)


def view_combat_log_in_frame():
    """Display combat log inside the main content_frame."""
    _clear_content_frame()
    try:
        from functions import get_data_dir
        log_path = os.path.join(get_data_dir(), 'combat_log.txt')
        with open(log_path, 'r', encoding='utf-8') as fh:
            content = fh.read()
    except FileNotFoundError:
        content = '(No combat log entries found yet)'

    txt = tk.Text(content_frame, wrap='word', height=30, width=80)
    txt.insert('end', content)
    txt.configure(state='disabled')
    txt.pack(padx=8, pady=8)


def view_help_in_frame():
    """Display help inside the main content_frame."""
    _clear_content_frame()
    txt = tk.Text(content_frame, wrap='word', height=18, width=80)
    txt.insert('end', HELP_TEXT)
    txt.configure(state='disabled')
    txt.pack(padx=8, pady=8)

window.mainloop()