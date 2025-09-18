# import calendar
# from collections import defaultdict
# from datetime import datetime

# def logic(lingkungan_list, year, month, available_slots):
#     """
#     lingkungan_list: list of dicts, each with 'nama', 'jumlah_tatib', 'availability'
#     available_slots: dict of slot datetime string -> max people (default 20)
#     returns: dict of slot -> list of lingkungan names assigned
#     """

#     # prepare assignment
#     assignments = defaultdict(list)
#     lingkungan_assigned = {l['nama']: [] for l in lingkungan_list}
#     slot_usage = defaultdict(int)

#     # prepare all possible slots for Saturday and Sunday
#     cal = calendar.Calendar()
#     saturdays = [d for d in cal.itermonthdates(year, month) if d.weekday() == 5 and d.month == month]
#     sundays = [d for d in cal.itermonthdates(year, month) if d.weekday() == 6 and d.month == month]

#     # get all possible slots per lingkungan
#     slot_candidates = []
#     for link in lingkungan_list:
#         for hari, jam_list in link.get('availability', {}).items():
#             if 'sabtu' in hari.lower():
#                 for date in saturdays:
#                     for jam in jam_list:
#                         slot = f"{date.strftime('%Y-%m-%d')}T{jam.replace('.', ':')}:00"
#                         slot_candidates.append((link['nama'], link['jumlah_tatib'], slot, date))
#             elif 'minggu' in hari.lower():
#                 for date in sundays:
#                     for jam in jam_list:
#                         slot = f"{date.strftime('%Y-%m-%d')}T{jam.replace('.', ':')}:00"
#                         slot_candidates.append((link['nama'], link['jumlah_tatib'], slot, date))    

#     # Track which slots have been taken
#     slots_taken = set()
#     # Track which lingkungan has been assigned
#     lingkungan_assigned_once = set()

#     for link in lingkungan_list:
#         # Find all possible slots for this lingkungan
#         possible_slots = []
#         for hari, jam_list in link.get('availability', {}).items():
#             if 'sabtu' in hari.lower():
#                 for date in saturdays:
#                     for jam in jam_list:
#                         slot = f"{date.strftime('%Y-%m-%d')}T{jam.replace('.', ':')}:00"
#                         possible_slots.append((slot, date))
#             elif 'minggu' in hari.lower():
#                 for date in sundays:
#                     for jam in jam_list:
#                         slot = f"{date.strftime('%Y-%m-%d')}T{jam.replace('.', ':')}:00"
#                         possible_slots.append((slot, date))
#         # Sort slots by date
#         possible_slots.sort(key=lambda x: x[0])
#         # Assign to the first slot not already taken
#         for slot, date in possible_slots:
#             if slot not in slots_taken:
#                 assignments[slot].append(link['nama'])
#                 slot_usage[slot] += link['jumlah_tatib']
#                 slots_taken.add(slot)
#                 lingkungan_assigned_once.add(link['nama'])
#                 break  # Only one assignment per lingkungan
    
#     # fill remaining slots with other lingkungan if < 20
#     for slot, assigned in assignments.items():
#         total_people = sum([next(l['jumlah_tatib'] for l in lingkungan_list if l['nama'] == n) for n in assigned])
#         if total_people < available_slots.get(slot, 20):
#             # find lingkungan not assigned anywhere yet
#             for l in lingkungan_list:
#                 if l['nama'] not in assigned and l['nama'] not in lingkungan_assigned_once:
#                     assignments[slot].append(l['nama'])
#                     lingkungan_assigned_once.add(l['nama'])
#                     total_people += l['jumlah_tatib']
#                     if total_people >= available_slots.get(slot, 20):
#                         break

#     return dict(assignments)

def logic(lingkungan_list, year, month, available_slots, start_idx=0):
    import calendar
    from collections import defaultdict

    assignments = defaultdict(list)

    # Prepare all possible slots for Saturday and Sunday
    cal = calendar.Calendar()
    saturdays = [d for d in cal.itermonthdates(year, month) if d.weekday() == 5 and d.month == month]
    sundays = [d for d in cal.itermonthdates(year, month) if d.weekday() == 6 and d.month == month]

    # Build all slots for the month (in order)
    all_slots = []
    for date in saturdays:
        all_slots.append((f"{date.strftime('%Y-%m-%d')}T17:00:00", "yakobus_sabtu", "17.00"))
    for date in sundays:
        all_slots.extend([
            (f"{date.strftime('%Y-%m-%d')}T08:00:00", "yakobus_minggu", "08.00"),
            (f"{date.strftime('%Y-%m-%d')}T11:00:00", "yakobus_minggu", "11.00"),
            (f"{date.strftime('%Y-%m-%d')}T17:00:00", "yakobus_minggu", "17.00"),
            (f"{date.strftime('%Y-%m-%d')}T07:30:00", "p2_minggu", "07.30"),
            (f"{date.strftime('%Y-%m-%d')}T10:30:00", "p2_minggu", "10.30"),
        ])

    # Filter lingkungan that are available for each slot
    available_for_slot = []
    for slot, slot_type, slot_time in all_slots:
        available = []
        for l in lingkungan_list:
            times = l.get("availability", {}).get(slot_type, [])
            if slot_time in times:
                available.append(l)
        available_for_slot.append(available)

    # Assign lingkungan in rotation, continuing from start_idx
    n_lingkungan = len(lingkungan_list)
    idx = start_idx
    assigned_this_month = set()
    for i, available in enumerate(available_for_slot):
        count = 0
        while count < n_lingkungan:
            l = lingkungan_list[idx % n_lingkungan]
            if l['nama'] not in assigned_this_month and l in available:
                assignments[all_slots[i][0]].append(l['nama'])
                assigned_this_month.add(l['nama'])
                idx += 1
                break
            idx += 1
            count += 1

    # If you want to fill up to 20 people per slot, uncomment below:
    for i, (slot, slot_type, slot_time) in enumerate(all_slots):
        total_people = sum([next(l['jumlah_tatib'] for l in lingkungan_list if l['nama'] == n) for n in assignments[slot]])
        if total_people < available_slots.get(slot, 20):
            for l in available_for_slot[i]:
                if l['nama'] not in assignments[slot] and l['nama'] not in assigned_this_month:
                    assignments[slot].append(l['nama'])
                    assigned_this_month.add(l['nama'])
                    total_people += l['jumlah_tatib']
                    if total_people >= available_slots.get(slot, 20):
                        break

    return dict(assignments), idx % n_lingkungan