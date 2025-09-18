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

    # assign each lingkungan to max 2 slots, no consecutive weeks
    for nama, jumlah, slot, date in sorted(slot_candidates, key=lambda x: x[2]):
        # already has 2 assignments?
        if len(lingkungan_assigned[nama]) >= 2:
            continue

        # check for week break (must not be in the same week or the next week)
        assigned_dates = [d for _, d in lingkungan_assigned[nama]]
        if assigned_dates:
            date_week = date.isocalendar()[1]
            if any(abs(date_week - ad.isocalendar()[1]) < 2 for ad in assigned_dates):
                continue

        # check slot capacity
        if slot_usage[slot] == 0 or slot_usage[slot] + jumlah <= available_slots.get(slot, 20):
            assignments[slot].append(nama)
            slot_usage[slot] += jumlah
            lingkungan_assigned[nama].append((slot, date))
    
    # fill remaining slots with other lingkungan if < 20
    for slot, assigned in assignments.items():
        total_people = sum([next(l['jumlah_tatib'] for l in lingkungan_list if l['nama'] == n) for n in assigned])
        if total_people < available_slots.get(slot, 20):
            # find lingkungan not assigned to this slot and not exceeding 2 assignments
            for l in lingkungan_list:
                if l['nama'] not in assigned and len(lingkungan_assigned[l['nama']]) < 2:
                    # check for week break (must not be in the same week or the next week)
                    assigned_dates = [d for _, d in lingkungan_assigned[l['nama']]]
                    slot_date = datetime.strptime(slot.split('T')[0], '%Y-%m-%d').date()
                    slot_week = slot_date.isocalendar()[1]
                    if assigned_dates and any(abs(slot_week - ad.isocalendar()[1]) < 2 for ad in assigned_dates):
                        continue
                    if total_people == 0 or total_people + l['jumlah_tatib'] <= available_slots.get(slot, 20):
                        assignments[slot].append(l['nama'])
                        lingkungan_assigned[l['nama']].append((slot, slot_date))
                        total_people += l['jumlah_tatib']
                    if total_people >= available_slots.get(slot, 20):
                        break
    
    return dict(assignments)