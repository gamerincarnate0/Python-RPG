# Turn-based combat manager with optional Tkinter GUI support
import random
from functions import TextFuncs
import player
from player_helpers import get_attack_power, use_health_potion
import os

try:
    import tkinter as tk
except Exception:
    tk = None

# Map item rarities to display colors in GUI
RARITY_COLORS = {
    'common': 'black',
    'uncommon': 'green',
    'rare': 'blue',
    'epic': 'purple',
    'legendary': 'orange',
}

# Small emoji decorations used in messages and summaries
RARITY_EMOJIS = {
    'common': '',
    'uncommon': '✨',
    'rare': '💠',
    'epic': '🌟',
    'legendary': '🔥',
}

SLOT_EMOJIS = {
    'weapon': '⚔️',
    'armor': '🛡️',
    'accessory': '📿',
}


def _format_with_rarity(text, rarity):
    return f"{text} ({rarity})" if rarity else text


def message_icon(text, rarity=None):
    """Return a small emoji prefix for `text` or `rarity` to improve readability."""
    # Rarity-based icon takes precedence for loot-related lines
    if rarity:
        return RARITY_EMOJIS.get(rarity, '')
    # Infer from keywords
    low = (text or '').lower()
    if 'hit' in low and 'you' not in low or 'hits you' in low or 'you hit' in low:
        return '⚔️'
    if 'braces' in low or 'defend' in low or 'defending' in low:
        return '🛡️'
    if 'potion' in low or 'used a health potion' in low:
        return '🧪'
    if 'fled' in low or 'flee' in low:
        return '🏃'
    if 'defeated' in low or 'defeat' in low or 'you were defeated' in low:
        return '💀'
    if 'earned' in low or 'xp' in low or 'gained' in low:
        return '✨'
    if 'gold' in low or 'found' in low:
        return '💰'
    if 'loot' in low or 'acquired' in low or 'found loot' in low:
        return '📦'
    return ''


def enemy_is_fightable(enemy_obj):
    """Return True if `enemy_obj` is a live enemy that can be engaged."""
    if enemy_obj is None:
        return False
    try:
        return enemy_obj.is_alive()
    except Exception:
        return False


class Combat:
    """Combat manager that supports both CLI and Tkinter GUI flows.

    Use `start_gui(parent, on_end=...)` to run combat in a non-blocking GUI window.
    """

    def __init__(self, player_obj, enemy_obj):
        self.player = player_obj
        self.enemy = enemy_obj
        self.player_defending = False
        self.enemy_defending = False
        self._gui_widgets = {}
        self._on_end = None

    # --- GUI integration -------------------------------------------------
    def start_gui(self, parent, on_end=None, on_refresh=None):
        if tk is None:
            raise RuntimeError("Tkinter is not available in this environment")
        self._on_end = on_end
        self._on_refresh = on_refresh
        # Create top-level UI inside provided parent (should be a Toplevel or Frame)
        self.win = parent

        # Layout
        self._gui_widgets['player_label'] = tk.Label(self.win, text=f"{self.player['name']} HP: {self.player['health']}/{self.player['max_health']}")
        self._gui_widgets['player_label'].pack(pady=4)

        self._gui_widgets['enemy_label'] = tk.Label(self.win, text=f"{self.enemy.name} HP: {self.enemy.health}")
        self._gui_widgets['enemy_label'].pack(pady=4)

        # Message area
        self._gui_widgets['messages'] = tk.Text(self.win, height=8, width=60, state='disabled')
        self._gui_widgets['messages'].pack(padx=6, pady=6)

        # Buttons
        btn_frame = tk.Frame(self.win)
        btn_frame.pack(pady=6)
        self._gui_widgets['attack_btn'] = tk.Button(btn_frame, text="Attack", width=10, command=lambda: self._player_action('attack'))
        self._gui_widgets['attack_btn'].grid(row=0, column=0, padx=4)
        self._gui_widgets['defend_btn'] = tk.Button(btn_frame, text="Defend", width=10, command=lambda: self._player_action('defend'))
        self._gui_widgets['defend_btn'].grid(row=0, column=1, padx=4)
        self._gui_widgets['potion_btn'] = tk.Button(btn_frame, text="Use Potion", width=10, command=lambda: self._player_action('potion'))
        self._gui_widgets['potion_btn'].grid(row=0, column=2, padx=4)
        self._gui_widgets['flee_btn'] = tk.Button(btn_frame, text="Flee", width=10, command=lambda: self._player_action('flee'))
        self._gui_widgets['flee_btn'].grid(row=0, column=3, padx=4)

        # Simple rarity legend
        legend_frame = tk.Frame(self.win)
        legend_frame.pack(pady=4)
        tk.Label(legend_frame, text='Rarity:').grid(row=0, column=0, padx=4)
        col = 1
        for r, color in RARITY_COLORS.items():
            lbl = tk.Label(legend_frame, text=r.capitalize(), fg=color)
            lbl.grid(row=0, column=col, padx=4)
            col += 1

        # Start with player turn
        self.append_message(f"Combat started: {self.player['name']} vs {self.enemy.name}")
        self._set_buttons_state('normal')
        self._update_labels()

    def append_message(self, text, rarity=None):
        """Append a message to the GUI message area (if present) or print via TextFuncs.

        If `rarity` is provided and a GUI text widget exists, the message line will be tagged
        and displayed in the color associated with that rarity.
        """
        # Compute a small icon to improve readability
        icon = message_icon(text, rarity)
        if rarity and not icon:
            # When rarity is provided but no emoji was chosen, prefer the rarity emoji
            icon = RARITY_EMOJIS.get(rarity, '')

        final_text = f"{icon} {text}" if icon else text

        if 'messages' in self._gui_widgets:
            txt = self._gui_widgets['messages']
            txt.configure(state='normal')
            start_index = txt.index('end')
            txt.insert('end', final_text + '\n')

            if rarity:
                tag = f"rarity_{rarity}"
                if tag not in txt.tag_names():
                    # configure tag with color and bold style
                    color = RARITY_COLORS.get(rarity, 'black')
                    try:
                        txt.tag_configure(tag, foreground=color, font=(None, 10, 'bold'))
                    except Exception:
                        # some Tk variants may not accept font tuple; fallback to color only
                        txt.tag_configure(tag, foreground=color)
                # apply tag to the last inserted line
                txt.tag_add(tag, start_index, f"{start_index} lineend")

            txt.see('end')
            txt.configure(state='disabled')
        else:
            if rarity:
                final_text = f"{icon} {_format_with_rarity(text, rarity)}" if icon else _format_with_rarity(text, rarity)
            TextFuncs.var_speed_print(final_text, 0.02, 0.04)

    def _set_buttons_state(self, state):
        for k in ('attack_btn', 'defend_btn', 'potion_btn', 'flee_btn'):
            w = self._gui_widgets.get(k)
            if w:
                w.configure(state=state)

    def _update_labels(self):
        pl = self._gui_widgets.get('player_label')
        el = self._gui_widgets.get('enemy_label')
        if pl:
            pl.configure(text=f"{self.player['name']} HP: {self.player['health']}/{self.player['max_health']}")
        if el:
            el.configure(text=f"{self.enemy.name} HP: {self.enemy.health}")

    # --- Gameplay logic -------------------------------------------------
    def _player_action(self, action):
        # Disable buttons until enemy turn completes
        self._set_buttons_state('disabled')

        if action == 'attack':
            dmg = get_attack_power() - getattr(self.enemy, 'armor', 0)
            dmg = max(1, dmg + random.randint(-1, 1))
            if self.enemy_defending:
                dmg = dmg // 2
                self.enemy_defending = False
            self.enemy.take_damage(dmg)
            self.append_message(f"You hit {self.enemy.name} for {dmg} damage.")

        elif action == 'defend':
            self.player_defending = True
            self.append_message(f"{self.player['name']} braces for incoming attacks.")

        elif action == 'potion':
            used = use_health_potion()
            if used:
                self.append_message("You used a Health Potion.")
            else:
                self.append_message("No Health Potion to use!")

        elif action == 'flee':
            if random.random() < 0.5:
                self.append_message("You fled successfully.")
                self._end_combat('fled')
                return
            else:
                self.append_message("Flee failed!")

        else:
            self.append_message("Unknown action.")

        self._update_labels()

        # Check if enemy defeated
        if not self.enemy.is_alive():
            self.append_message(f"{self.enemy.name} has been defeated!")
            self._end_combat(True)
            return

        # Enemy turn after short delay
        if hasattr(self.win, 'after'):
            self.win.after(700, self._enemy_turn)
        else:
            # fallback immediate
            self._enemy_turn()

    def _enemy_turn(self):
        self.append_message(f"-- Enemy Turn -- {self.enemy.name}")

        action = 'attack'
        try:
            action = self.enemy.decide_action(self.player)
        except Exception:
            # fallback
            action = 'attack'

        if action == 'attack':
            dmg = self.enemy.attack()
            player_defense = self.player.get('agility', 0) // 3
            dmg = max(1, dmg - player_defense + random.randint(-1, 1))
            if self.player_defending:
                dmg = dmg // 2
                self.player_defending = False
            self.player['health'] = max(0, self.player['health'] - dmg)
            self.append_message(f"{self.enemy.name} hits you for {dmg} damage!")

        elif action == 'defend':
            self.enemy_defending = True
            self.append_message(f"{self.enemy.name} braces for your next attack.")

        elif action == 'heal':
            used_potion = False
            for it in list(getattr(self.enemy, 'inventory', [])):
                if getattr(it, 'name', None) == 'Health Potion':
                    # Use the potion on the enemy object
                    it.use(self.enemy)
                    used_potion = True
                    healed_amount = getattr(self.enemy, 'health', 0)
                    self.append_message(f"{self.enemy.name} uses a Health Potion.")
                    break

            if not used_potion:
                # fallback: small self-heal
                heal_amt = max(1, self.enemy.max_health // 6)
                prev = self.enemy.health
                self.enemy.heal(heal_amt)
                self.append_message(f"{self.enemy.name} regenerates {self.enemy.health - prev} HP!")

        else:
            # unknown action -> attack as fallback
            dmg = self.enemy.attack()
            player_defense = self.player.get('agility', 0) // 3
            dmg = max(1, dmg - player_defense + random.randint(-1, 1))
            self.player['health'] = max(0, self.player['health'] - dmg)
            self.append_message(f"{self.enemy.name} hits you for {dmg} damage!")

        self._update_labels()

        # Check if player defeated
        if self.player.get('health', 0) <= 0:
            self.append_message("You were defeated...")
            self._end_combat(False)
            return

        # Re-enable buttons for next player turn
        self._set_buttons_state('normal')

    def _end_combat(self, player_won):
        self._set_buttons_state('disabled')

        # Determine if player fled (new logic: player_won can be True, False, or 'fled')
        fled = player_won == 'fled'

        # Award XP/gold/loot for victories only if not fled
        if player_won is True and not fled:
            try:
                from player_helpers import add_experience, add_gold, add_loot
                xp = getattr(self.enemy, 'xp_reward', 0)
                gold = getattr(self.enemy, 'gold_reward', 0)
                loot = getattr(self.enemy, 'loot', []) or []

                if xp:
                    add_experience(xp)
                    self.append_message(f"Earned {xp} XP.")
                if gold:
                    add_gold(gold)
                    self.append_message(f"Found {gold} gold.")
                if loot:
                    add_loot(loot)
                    for it in loot:
                        self.append_message(f"Found loot: {it.name}", rarity=getattr(it, 'rarity', 'common'))
            except Exception:
                # non-fatal if player_helpers fails
                pass

        if self._on_end:
            try:
                self._on_end(player_won)
            except Exception:
                pass

        # Autosave on victory (best-effort, non-fatal), but not on flee
        if player_won is True and not fled:
            try:
                from functions import save_game
                saved = save_game()
                if saved:
                    try:
                        # Use append_message so both GUI and CLI notify the user
                        self.append_message("Game autosaved.")
                    except Exception:
                        pass
            except Exception:
                pass

        # Build a summary text for logging/presentation
        summary_lines = []
        if player_won is True and not fled:
            xp = getattr(self.enemy, 'xp_reward', 0)
            gold = getattr(self.enemy, 'gold_reward', 0)
            loot = getattr(self.enemy, 'loot', []) or []
            summary_lines.append(f"Victory vs {self.enemy.name}")
            if xp:
                summary_lines.append(f"XP: {xp}")
            if gold:
                summary_lines.append(f"Gold: {gold}")
            if loot:
                # include rarity markers + emoji in the summary log
                def _format_loot_entry(it):
                    r = getattr(it, 'rarity', 'common')
                    icon = RARITY_EMOJIS.get(r, '')
                    return f"{icon} {it.name} ({r})" if icon else f"{it.name} ({r})"
                summary_lines.append("Loot: " + ", ".join(_format_loot_entry(it) for it in loot))
        elif fled:
            summary_lines.append(f"Fled from {self.enemy.name}")
        else:
            summary_lines.append(f"Defeat vs {self.enemy.name}")

        summary_text = " | ".join(summary_lines)

        # Persist to combat log file in the user data directory (non-fatal)
        try:
            from functions import get_data_dir
            import datetime
            log_path = os.path.join(get_data_dir(), 'combat_log.txt')
            with open(log_path, 'a', encoding='utf-8') as fh:
                ts = datetime.datetime.utcnow().isoformat()
                fh.write(f"{ts} - {summary_text}\n")
        except Exception:
            pass

        # If this is running as a GUI, show a persistent summary panel and let the player close it
        try:
            if hasattr(self, 'win') and getattr(self.win, 'winfo_exists', lambda: False)():
                # Clear message area and show summary
                self.append_message('--- Combat Summary ---')
                for ln in summary_lines:
                    self.append_message(ln)

                # Add a Close button that the user must click; disable other buttons
                self._set_buttons_state('disabled')
                if 'summary_frame' not in self._gui_widgets:
                    frm = tk.Frame(self.win)
                    frm.pack(pady=6)
                    lbl = tk.Label(frm, text='Combat Summary:')
                    lbl.pack()

                    # Summary text
                    txt = tk.Text(frm, height=4, width=60, state='normal')
                    txt.insert('end', summary_text)
                    txt.config(state='disabled')
                    txt.pack(padx=6, pady=4)

                    # If there is loot, show clickable buttons that open item tooltips (only if not fled)
                    loot = getattr(self.enemy, 'loot', []) or []
                    if player_won is True and not fled and loot:
                        loot_frame = tk.Frame(frm)
                        loot_frame.pack(pady=4)
                        tk.Label(loot_frame, text='Loot:').grid(row=0, column=0, padx=4)
                        col = 1
                        for it in loot:
                            btn = tk.Button(loot_frame, text=it.name, command=lambda itm=it: self._show_item_tooltip(itm))
                            btn.grid(row=0, column=col, padx=4)
                            col += 1

                    close_btn = tk.Button(frm, text='Close', command=lambda: self.win.destroy())
                    close_btn.pack(pady=4)
                    self._gui_widgets['summary_frame'] = frm
                # Do NOT auto-destroy here; user will close summary
                return
        except Exception:
            # if GUI paths fail, fallback to auto-close
            pass

        # fallback: try to close window if GUI is present
        try:
            if hasattr(self, 'win') and getattr(self.win, 'after', None):
                self.win.after(1000, lambda: self.win.destroy())
            else:
                try:
                    self.win.destroy()
                except Exception:
                    pass
        except Exception:
            pass

    def _show_item_tooltip(self, item):
        """Open a small window showing an item's description and rarity-colored title and actions."""
        try:
            top = tk.Toplevel(self.win)
            top.title(item.name)
            color = RARITY_COLORS.get(getattr(item, 'rarity', 'common'), 'black')
            title = tk.Label(top, text=f"{item.name} ({getattr(item, 'rarity', 'common')})", fg=color, font=(None, 12, 'bold'))
            title.pack(pady=6)
            desc = tk.Text(top, height=8, width=50, state='normal')
            desc.insert('end', item.description())
            desc.config(state='disabled')
            desc.pack(padx=8, pady=6)

            btn_frame = tk.Frame(top)
            btn_frame.pack(pady=6)

            # Equip button - show comparison to current equipment for this slot
            if getattr(item, 'item_type', None) == 'equipment':
                try:
                    from player_helpers import get_item_slot, is_better
                    slot = get_item_slot(item)
                    current = player['equipment'].get(slot)
                    # show current equipped in this slot (if any)
                    cur_text = f"Current: {current.name} ({getattr(current, 'rarity', 'common')})" if current else "Current: (None)"
                    tk.Label(top, text=cur_text).pack()
                    # if the new item is better, highlight a recommendation
                    recommended = is_better(item, current)
                    if recommended:
                        note = tk.Label(top, text="This item appears to be better than your current equipment.", fg='green')
                        note.pack(pady=4)
                        eq_text = 'Equip (Recommended)'
                    else:
                        eq_text = 'Equip'
                    eq_btn = tk.Button(btn_frame, text=eq_text, command=lambda itm=item: self._equip_and_refresh(itm, top))
                    eq_btn.grid(row=0, column=0, padx=4)
                except Exception:
                    # fallback to the simple Equip button
                    eq_btn = tk.Button(btn_frame, text='Equip', command=lambda itm=item: self._equip_and_refresh(itm, top))
                    eq_btn.grid(row=0, column=0, padx=4)

            sell_btn = tk.Button(btn_frame, text='Sell', command=lambda itm=item: self._sell_and_refresh(itm, top))
            sell_btn.grid(row=0, column=1, padx=4)

            close = tk.Button(top, text='Close', command=top.destroy)
            close.pack(pady=6)
        except Exception:
            # fallback to printing
            TextFuncs.var_speed_print(item.description(), 0.02, 0.04)

    def _equip_and_refresh(self, item, window_ref):
        """Equip an item and refresh UI; safe for use from tooltips."""
        try:
            from player_helpers import equip_item
            ok = equip_item(item)
        except Exception:
            ok = False

        if not ok:
            try:
                TextFuncs.var_speed_print("Could not equip item (no space to unequip or invalid).", 0.02, 0.04)
            except Exception:
                pass
            return

        # success path
        try:
            TextFuncs.var_speed_print(f"{item.name} equipped.", 0.02, 0.04)
        except Exception:
            pass

        try:
            window_ref.destroy()
        except Exception:
            pass

        # call refresh callback if available
        try:
            if getattr(self, '_on_refresh', None):
                try:
                    self._on_refresh()
                except Exception:
                    pass
        except Exception:
            pass

        # refresh inventory window if present (close + reopen)
        try:
            parent = getattr(window_ref, 'master', None)
            if parent and getattr(parent, 'winfo_exists', lambda: False)() and getattr(parent, 'title', lambda: '')() == 'Inventory':
                try:
                    parent.destroy()
                except Exception:
                    pass
                try:
                    from main import view_inventory_gui
                    view_inventory_gui()
                except Exception:
                    pass
        except Exception:
            pass

    def _sell_and_refresh(self, item, window_ref):
        try:
            from player_helpers import sell_item
            gold = sell_item(item)
            if gold > 0:
                TextFuncs.var_speed_print(f"Sold {item.name} for {gold} gold.", 0.02, 0.04)
                try:
                    window_ref.destroy()
                except Exception:
                    pass
                # call refresh callback if available
                try:
                    if getattr(self, '_on_refresh', None):
                        self._on_refresh()
                except Exception:
                    pass
            else:
                TextFuncs.var_speed_print("Could not sell item (not in inventory).", 0.02, 0.04)
        except Exception:
            pass