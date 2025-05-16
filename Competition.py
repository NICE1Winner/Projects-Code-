import tkinter as tk
from tkinter import ttk, messagebox

teams = [
    "Hi-Bot", "Shady Monke", "Hyper-Bot", "Gigachads", "Kawaii Kittens",
    "The Kids", "CheTo", "Neo Egoists", "Lego Dummies", "Boba",
    "The Engineers of the Galaxy!", "The Engine-ears!", "Su-mo, Su-more, Su-most!"
]

# Add BYE for odd number of teams (one team rests per round)
if len(teams) % 2 != 0:
    teams.append("BYE")

NUM_ROUNDS = len(teams) - 1
leaderboard = {t: {"W": 0, "D": 0, "L": 0, "Pts": 0} for t in teams if t != "BYE"}

def generate_schedule(ts):
    n = len(ts)
    sched = []
    temp = ts[:]
    for _ in range(n-1):
        pairs = [(temp[i], temp[n-1-i]) for i in range(n//2)]
        sched.append(pairs)
        temp.insert(1, temp.pop())  # Rotate except first element
    return sched

schedule = generate_schedule(teams)
results = {r: {match: None for match in schedule[r-1] if "BYE" not in match} for r in range(1, NUM_ROUNDS+1)}

def recalc_leaderboard():
    for t in leaderboard:
        leaderboard[t] = {"W":0, "D":0, "L":0, "Pts":0}
    for r in results:
        for (t1, t2), res in results[r].items():
            if res == "1":
                leaderboard[t1]["W"] += 1
                leaderboard[t1]["Pts"] += 3
                leaderboard[t2]["L"] += 1
            elif res == "2":
                leaderboard[t2]["W"] += 1
                leaderboard[t2]["Pts"] += 3
                leaderboard[t1]["L"] += 1
            elif res == "D":
                leaderboard[t1]["D"] += 1
                leaderboard[t1]["Pts"] += 1
                leaderboard[t2]["D"] += 1
                leaderboard[t2]["Pts"] += 1

def load_round(rnd):
    match_tree.delete(*match_tree.get_children())
    round_label.config(text=f"Round {rnd} ({'Morning' if rnd <= 7 else 'Afternoon'})")
    for t1, t2 in schedule[rnd-1]:
        if "BYE" in (t1, t2):
            # Show bye team as resting
            rest_team = t1 if t2 == "BYE" else t2
            match_tree.insert("", "end", values=(rest_team, "Rest (BYE)", "-"))
        else:
            res = results[rnd].get((t1,t2)) or ""
            match_tree.insert("", "end", values=(t1, t2, res))

def update_leaderboard_view():
    for i in leaderboard_tree.get_children():
        leaderboard_tree.delete(i)
    sorted_teams = sorted(leaderboard.items(), key=lambda x: x[1]["Pts"], reverse=True)
    for rank, (team, stats) in enumerate(sorted_teams, 1):
        leaderboard_tree.insert("", "end", values=(rank, team, stats["W"], stats["D"], stats["L"], stats["Pts"]))

def on_round_change():
    try:
        rnd = int(round_spin.get())
        if 1 <= rnd <= NUM_ROUNDS:
            load_round(rnd)
        else:
            messagebox.showwarning("Invalid Round", f"Please select round 1 to {NUM_ROUNDS}")
    except:
        messagebox.showwarning("Invalid Input", "Enter a valid round number")

def enter_result():
    sel = match_tree.selection()
    if not sel:
        messagebox.showwarning("Select Match", "Please select a match to enter result")
        return
    t1, t2, _ = match_tree.item(sel[0])["values"]
    if t2 == "Rest (BYE)":
        messagebox.showinfo("Bye", f"{t1} is resting this round (BYE)")
        return

    def submit(res):
        results[int(round_spin.get())][(t1, t2)] = res
        recalc_leaderboard()
        load_round(int(round_spin.get()))
        update_leaderboard_view()
        popup.destroy()

    popup = tk.Toplevel(root)
    popup.title(f"Result: {t1} vs {t2}")
    for txt, val in [(f"{t1} wins", "1"), (f"{t2} wins", "2"), ("Draw", "D"), ("Clear", None)]:
        tk.Button(popup, text=txt, width=20, command=lambda v=val: submit(v)).pack(pady=2)

root = tk.Tk()
root.title("Sumo-Bot Competition")
root.geometry("850x600")

top_frame = tk.Frame(root)
top_frame.pack(pady=10)

tk.Label(top_frame, text="Round:", font=("Arial", 14)).pack(side="left")
round_spin = tk.Spinbox(top_frame, from_=1, to=NUM_ROUNDS, width=4, command=on_round_change)
round_spin.pack(side="left", padx=5)
tk.Button(top_frame, text="Load Round", command=on_round_change).pack(side="left", padx=5)
round_label = tk.Label(top_frame, text="", font=("Arial", 16))
round_label.pack(side="left", padx=20)
tk.Button(top_frame, text="Enter Result", command=enter_result).pack(side="right", padx=10)

mid_frame = tk.Frame(root)
mid_frame.pack(pady=10)
match_columns = ("Team 1", "Team 2", "Result")
match_tree = ttk.Treeview(mid_frame, columns=match_columns, show="headings", height=12)
for c in match_columns:
    match_tree.heading(c, text=c)
    match_tree.column(c, width=270, anchor="center")
match_tree.pack()

bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=10, fill="both", expand=True)
lb_columns = ("Rank", "Team", "W", "D", "L", "Pts")
leaderboard_tree = ttk.Treeview(bottom_frame, columns=lb_columns, show="headings", height=13)
for c in lb_columns:
    leaderboard_tree.heading(c, text=c)
    leaderboard_tree.column(c, width=100, anchor="center")
leaderboard_tree.pack()

# Initial load
load_round(1)
update_leaderboard_view()

root.mainloop()
