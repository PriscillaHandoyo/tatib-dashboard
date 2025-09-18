import calendar
from collections import defaultdict
from datetime import datetime

def logic(lingkungan_list, year, month, available_slots):
    """
    lingkungan_list: list of dicts, each with 'nama', 'jumlah_tatib', 'availability'
    available_slots: dict of slot datetime string -> max people (default 20)
    returns: dict of slot -> list of lingkungan names assigned
    """

    # prepare assignment
    assignments = defaultdict(list)
    lingkungan_assigned = {l['nama']: [] for l in lingkungan_list}
    slot_usage = defaultdict(int)

    # prepare all possible slots for Saturday and Sunday
    cal = calendar.Calendar()
    saturdays = [d for d in cal.itermonthdates(year, month) if d.weekday() == 5 and d.month == month]
    sundays = [d for d in cal.itermonthdates(year, month) if d.weekday() == 6 and d.month == month]

    # get all possible slots per lingkungan
    slot_candidates = []
    for link in lingkungan_list:
        for hari, jam_list in link.get('availability', {}).items():
            if 'sabtu' in hari.lower():
                for date in saturdays:
                    for jam in jam_list:
                        slot = f"{date.strftime('%Y-%m-%d')}T{jam.replace('.', ':')}:00"
                        slot_candidates.append((link['nama'], link['jumlah_tatib'], slot, date))
            elif 'minggu' in hari.lower():
                for date in sundays:
                    for jam in jam_list:
                        slot = f"{date.strftime('%Y-%m-%d')}T{jam.replace('.', ':')}:00"
                        slot_candidates.append((link['nama'], link['jumlah_tatib'], slot, date))    

    # Track which slots have been taken
    slots_taken = set()
    # Track which lingkungan has been assigned
    lingkungan_assigned_once = set()

    for link in lingkungan_list:
        # Find all possible slots for this lingkungan
        possible_slots = []
        for hari, jam_list in link.get('availability', {}).items():
            if 'sabtu' in hari.lower():
                for date in saturdays:
                    for jam in jam_list:
                        slot = f"{date.strftime('%Y-%m-%d')}T{jam.replace('.', ':')}:00"
                        possible_slots.append((slot, date))
            elif 'minggu' in hari.lower():
                for date in sundays:
                    for jam in jam_list:
                        slot = f"{date.strftime('%Y-%m-%d')}T{jam.replace('.', ':')}:00"
                        possible_slots.append((slot, date))
        # Sort slots by date
        possible_slots.sort(key=lambda x: x[0])
        # Assign to the first slot not already taken
        for slot, date in possible_slots:
            if slot not in slots_taken:
                assignments[slot].append(link['nama'])
                slot_usage[slot] += link['jumlah_tatib']
                slots_taken.add(slot)
                lingkungan_assigned_once.add(link['nama'])
                break  # Only one assignment per lingkungan
    
    # fill remaining slots with other lingkungan if < 20
    for slot, assigned in assignments.items():
        total_people = sum([next(l['jumlah_tatib'] for l in lingkungan_list if l['nama'] == n) for n in assigned])
        if total_people < available_slots.get(slot, 20):
            # find lingkungan not assigned anywhere yet
            for l in lingkungan_list:
                if l['nama'] not in assigned and l['nama'] not in lingkungan_assigned_once:
                    assignments[slot].append(l['nama'])
                    lingkungan_assigned_once.add(l['nama'])
                    total_people += l['jumlah_tatib']
                    if total_people >= available_slots.get(slot, 20):
                        break

    return dict(assignments)