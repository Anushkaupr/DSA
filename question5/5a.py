import math
import itertools
import tkinter as tk
from tkinter import messagebox
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------- Dataset ----------------
SPOTS = [
    {"name": "Pashupatinath Temple", "lat": 27.7104, "lon": 85.3488,
     "fee": 100, "tags": ["culture", "religious"]},
    {"name": "Swayambhunath Stupa", "lat": 27.7149, "lon": 85.2906,
     "fee": 200, "tags": ["culture", "heritage"]},
    {"name": "Garden of Dreams", "lat": 27.7125, "lon": 85.3170,
     "fee": 150, "tags": ["nature", "relaxation"]},
    {"name": "Chandragiri Hills", "lat": 27.6616, "lon": 85.2458,
     "fee": 700, "tags": ["nature", "adventure"]},
    {"name": "Kathmandu Durbar Sq.", "lat": 27.7048, "lon": 85.3076,
     "fee": 100, "tags": ["culture", "heritage"]},
]

VISIT_HOURS = 1.0  # hours spent at each spot
TRAVEL_SPEED = 40.0  # km/h
EARTH_KM = 111.0  # approx km per degree latitude


def travel_time(s1, s2):
    """Euclidean travel time in hours between two spot dictionaries."""
    dx = (s1["lon"] - s2["lon"]) * EARTH_KM * math.cos(math.radians(s1["lat"]))
    dy = (s1["lat"] - s2["lat"]) * EARTH_KM
    return math.hypot(dx, dy) / TRAVEL_SPEED


def interest_score(spot, interests):
    """Count how many of the user's interest tags match this spot."""
    return sum(1 for t in interests if t in spot["tags"])


def greedy_itinerary(budget, total_hours, interests):
    """
    Greedy heuristic: pick the highest-utility unvisited feasible spot
    at each step. Utility = interest_score / ((1+fee)*(1+travel_time))
    """
    available = list(SPOTS)
    selected, cost, time_used, reasons = [], 0.0, 0.0, []
    current = None

    while available:
        feasible = [s for s in available
                    if cost + s["fee"] <= budget
                    and time_used + VISIT_HOURS +
                    (travel_time(current, s) if current else 0) <= total_hours]
        if not feasible:
            break

        best = max(feasible,
                   key=lambda s: interest_score(s, interests) /
                                 ((1 + s["fee"]) *
                                  (1 + (travel_time(current, s) if current else 0))))
        tt = travel_time(current, best) if current else 0.0
        time_used += tt + VISIT_HOURS
        cost += best["fee"]
        reasons.append(f"Selected '{best['name']}' -- interest match: "
                       f"{interest_score(best, interests)}, fee: Rs.{best['fee']}, "
                       f"travel: {tt*60:.0f} min")
        selected.append(best)
        current = best
        available.remove(best)

    return selected, cost, time_used, reasons
def brute_force_itinerary(budget, total_hours, interests):
    """
    Exhaustive permutation search on the full dataset (n=5, so n!=120).
    Finds the ordering that maximizes total interest match score.
    """
    best_path, best_score = [], -1

    for r in range(1, len(SPOTS) + 1):
        for perm in itertools.permutations(SPOTS, r):
            if sum(s["fee"] for s in perm) > budget:
                continue
            t = sum(VISIT_HOURS for _ in perm)
            t += sum(travel_time(perm[i-1], perm[i]) for i in range(1, len(perm)))
            if t > total_hours:
                continue
            score = sum(interest_score(s, interests) for s in perm)
            if score > best_score:
                best_score = score
                best_path = list(perm)
    return best_path


# GUI 
class ItineraryApp:
    def __init__(self, master):
        self.master = master
        master.title("Tourist Spot Optimiser -- Kathmandu")
        master.geometry("880x700")
        master.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        tk.Label(self.master,
                 text="Tourist Spot Optimiser -- Kathmandu",
                 font=("Times New Roman", 14, "bold"),
                 pady=8).pack(fill=tk.X)

        # Input row
        frm = tk.Frame(self.master, padx=10, pady=5)
        frm.pack(fill=tk.X)
        self.budget_var = tk.StringVar(value="800")
        self.hours_var = tk.StringVar(value="6")
        self.int_var = tk.StringVar(value="culture,nature")
        for col, (lbl, var, w) in enumerate([
            ("Budget (NPR):", self.budget_var, 8),
            ("Hours:", self.hours_var, 5),
            ("Interests:", self.int_var, 18)]):
            tk.Label(frm, text=lbl, font=("Times New Roman", 11)).grid(row=0, column=col*2, sticky="w")
            tk.Entry(frm, textvariable=var, width=w, font=("Times New Roman", 11)).grid(row=0, column=col*2+1, padx=4)

        # Buttons
        btn = tk.Frame(self.master)
        btn.pack(pady=4)
        tk.Button(btn, text="Run Greedy", font=("Times New Roman", 11), padx=10, pady=3,
                  command=self.run_greedy).pack(side=tk.LEFT, padx=6)
        tk.Button(btn, text="Compare Brute-Force", font=("Times New Roman", 11), padx=10, pady=3,
                  command=self.run_compare).pack(side=tk.LEFT, padx=6)

        # Output text
        self.out = tk.Text(self.master, height=11, font=("Courier New", 10), state=tk.DISABLED)
        self.out.pack(fill=tk.X, padx=10, pady=4)

        # Map canvas
        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, padx=10, pady=4)

    def _get_inputs(self):
        """Validate and return (budget, hours, interests) or (None,None,None)."""
        try:
            budget = float(self.budget_var.get())
            hours = float(self.hours_var.get())
            if budget <= 0 or hours <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Budget and Hours must be positive numbers.")
            return None, None, None
        interests = [t.strip() for t in self.int_var.get().split(",") if t.strip()]
        if not interests:
            messagebox.showerror("Input Error", "Please enter at least one interest tag.")
            return None, None, None
        return budget, hours, interests

    def _write(self, text):
        self.out.config(state=tk.NORMAL)
        self.out.delete("1.0", tk.END)
        self.out.insert(tk.END, text)
        self.out.config(state=tk.DISABLED)

    def _draw_map(self, spots, title=""):
        self.ax.clear()
        if spots:
            lons = [s["lon"] for s in spots]
            lats = [s["lat"] for s in spots]
            self.ax.plot(lons, lats, "k-o", markersize=7, linewidth=1.5)
            for i, s in enumerate(spots):
                self.ax.annotate(f"{i+1}. {s['name'][:15]}", (s["lon"], s["lat"]),
                                 textcoords="offset points", xytext=(5, 4), fontsize=8)
        self.ax.set_title(title, fontsize=11, fontweight="bold")
        self.ax.set_xlabel("Longitude")
        self.ax.set_ylabel("Latitude")
        self.ax.grid(True, alpha=0.3)
        self.fig.tight_layout()
        self.canvas.draw()

    def run_greedy(self):
        budget, hours, interests = self._get_inputs()
        if budget is None:
            return
        spots, cost, time_used, reasons = greedy_itinerary(budget, hours, interests)
        lines = [f"=== Greedy Itinerary Budget=Rs.{budget} Time={hours}h ===\n"]
        for i, (s, r) in enumerate(zip(spots, reasons)):
            lines.append(f" Stop {i+1}: {s['name']} (Fee: Rs.{s['fee']})\n")
            lines.append(f" {r}\n")
        lines.append(f"\nTotal cost: Rs.{cost:.0f} | Total time: {time_used:.2f}h")
        self._write("".join(lines))
        self._draw_map(spots, f"Greedy Path ({len(spots)} spots)")

    def run_compare(self):
        budget, hours, interests = self._get_inputs()
        if budget is None:
            return
        g_spots, g_cost, g_time, _ = greedy_itinerary(budget, hours, interests)
        b_spots = brute_force_itinerary(budget, hours, interests)
        b_cost = sum(s["fee"] for s in b_spots)
        b_time = sum(VISIT_HOURS for _ in b_spots) + sum(travel_time(b_spots[i-1], b_spots[i])
                                                         for i in range(1, len(b_spots)))
        lines = [
            "=== Greedy vs Brute-Force Comparison ===\n\n",
            f"{'Metric':<24} {'Greedy':>10} {'Brute-Force':>13}\n",
            "-"*49 + "\n",
            f"{'Spots visited':<24} {len(g_spots):>10} {len(b_spots):>13}\n",
            f"{'Total cost (Rs.)':<24} {g_cost:>10.0f} {b_cost:>13.0f}\n",
            f"{'Total time (hrs)':<24} {g_time:>10.2f} {b_time:>13.2f}\n\n",
            "Trade-off:\n",
            " Greedy O(n^2) -- fast, near-optimal, scales to large n.\n",
            " Brute O(n!) -- exact, but only feasible for n <= 6.\n",
        ]
        self._write("".join(lines))
        self._draw_map(g_spots, "Greedy path shown (vs brute-force)")


if __name__ == "__main__":
    root = tk.Tk()
    ItineraryApp(root)
    root.mainloop()