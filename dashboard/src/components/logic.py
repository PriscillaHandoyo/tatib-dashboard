import calendar
from collections import defaultdict

def logic (lingkungan_list, year, month, available_slots):
    # prepare assignment
    assignments = defaultdict(list)
    lingkungan_assigned = {l['nama']: [] for l in lingkungan_list}

    # get all possible slots per lingkungan
    slot_candidates = []
    for link in lingkungan_list:
        for hari, jam_list in link.get('availability', {}).items():
            for jam in jam_list:
                # ex: assign to first and third week of the month
                for week in [1, 3]:
                    # find teh date for the week and day
                    cal = calendar.Calendar()
                    if 'sabtu' in hari.lower():
                        dates = [d for d in cal.itermonthdates(year, month) if d.weekday() == 5]
                    else:
                        dates = [d for d in cal.itermonthdates(year,month) if d.weekday() == 6]
                    if len(dates) >= week:
                        date = dates[week-1]
                        slot = f"{date.strftime('%Y-%m-%d')}T{jam.replace('.', ':')}:00"
                        slot_candidates.append((link['nama'], link['jumlah_tatib'], slot))

    # assign eah lingkungan to max 2 slots, not concesutive weeks
    slot_usage = defaultdict(int)
    for nama, jumlah, slot in sorted(slot_candidates, key=lambda x: x[2]):
        # check if lingkungan already has 2 assignments
        if len(lingkungan_assigned[nama]) >= 2:
            continue
        # check if previous assignment is in the previous week
        assigned_weeks = [int(a.split('-')[2][:2]) for a in lingkungan_assigned[nama]]
        week_num = int(slot.split('-')[2][:2])
        if assigned_weeks and abs(week_num - assigned_weeks[-1]) < 7:
            continue
        # check slot capacity
        if slot_usage[slot] + jumlah <= available_slots.get(slot, 20):
            assignments[slot].append(nama)
            slot_usage[slot] += jumlah
            lingkungan_assigned[nama].append(slot)
    
    # fill remaining slots with other lingkungan if < 20
    for slot, assigned in assignments.items():
        total_people = sum([next(l['jumlah_tatib'] for l in lingkungan_list if l['nama'] == n) for n in assigned])
        if total_people < available_slots.get(slot, 20):
            # find lingkungan not assigned to this slot and not exceeding 2 assignments
            for l in lingkungan_list:
                if l['nama'] not in assigned and len(lingkungan_assigned[l['nama']]) < 2:
                    if total_people + l['jumlah_tatib'] <= available_slots.get(slot, 20):
                        assignments[slot].append(l['nama'])
                        lingkungan_assigned[l['nama']].append(slot)
                        total_people += l['jumlah_tatib']
                    if total_people >= available_slots.get(slot, 20):
                        break
    
    return dict(assignments)