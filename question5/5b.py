import threading
import queue
import time
import tkinter as tk
from tkinter import ttk
import requests
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"  # Replace with your key
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

CITIES = [
    {"name": "Kathmandu", "lat": 27.7172, "lon": 85.3240},
    {"name": "Pokhara", "lat": 28.2096, "lon": 83.9856},
    {"name": "Biratnagar", "lat": 26.4525, "lon": 87.2718},
    {"name": "Nepalgunj", "lat": 28.0500, "lon": 81.6167},
    {"name": "Dhangadhi", "lat": 28.7000, "lon": 80.5833},
]

def fetch_city(city, result_queue, lock):
    """Fetch weather for one city in a separate thread."""
    try:
        params = {
            "lat": city["lat"],
            "lon": city["lon"],
            "appid": API_KEY,
            "units": "metric"
        }
        resp = requests.get(BASE_URL, params=params, timeout=10)
        data = resp.json()
        result = {
            "city": city["name"],
            "temp": data["main"]["temp"],
            "hum": data["main"]["humidity"],
            "press": data["main"]["pressure"],
            "desc": data["weather"][0]["description"].title(),
            "ok": True,
        }
    except Exception as e:
        result = {"city": city["name"], "ok": False, "err": str(e)}

    with lock:
        result_queue.put(result)


class WeatherApp:
    def __init__(self, master):
        self.master = master
        master.title("Nepal Weather Dashboard")
        master.geometry("820x600")
        self.rq = queue.Queue()
        self.lock = threading.Lock()
        self.seq_t = None
        self.con_t = None
        self._build_ui()

    def _build_ui(self):
        tk.Label(self.master, text="Nepal Multi-City Weather Dashboard",
                 font=("Times New Roman", 14, "bold"), pady=6).pack(fill=tk.X)

        # Buttons
        btn_frame = tk.Frame(self.master, pady=4)
        btn_frame.pack()
        tk.Button(btn_frame, text="Fetch (Concurrent)",
                  font=("Times New Roman", 11), padx=10, pady=3,
                  command=self.fetch_concurrent).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="Fetch (Sequential)",
                  font=("Times New Roman", 11), padx=10, pady=3,
                  command=self.fetch_sequential).pack(side=tk.LEFT, padx=8)

        self.status = tk.StringVar(value="Ready.")
        tk.Label(self.master, textvariable=self.status,
                 font=("Times New Roman", 10)).pack()

        # Results table
        cols = ("City", "Temp (C)", "Humidity (%)", "Pressure (hPa)", "Description")
        self.tree = ttk.Treeview(self.master, columns=cols, show="headings", height=6)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=145, anchor="center")
        self.tree.pack(fill=tk.X, padx=10, pady=5)

        # Latency chart
        self.fig, self.ax = plt.subplots(figsize=(7, 2.8))
        cv = FigureCanvasTkAgg(self.fig, master=self.master)
        cv.get_tk_widget().pack(fill=tk.BOTH, padx=10, pady=4)
        self.canvas = cv

    def _clear(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

    def _insert(self, r):
        if r.get("ok"):
            self.tree.insert("", tk.END, values=(
                r["city"], f"{r['temp']:.1f}", r["hum"], r["press"], r["desc"]))
        else:
            self.tree.insert("", tk.END, values=(
                r["city"], "N/A", "N/A", "N/A", r.get("err", "Error")))

    def fetch_concurrent(self):
        self._clear()
        self.status.set("Fetching concurrently ...")
        start = time.perf_counter()
        threads = []

        for city in CITIES:
            t = threading.Thread(target=fetch_city, args=(city, self.rq, self.lock), daemon=True)
            threads.append(t)
            t.start()

        def poll():
            while not self.rq.empty():
                self._insert(self.rq.get_nowait())
            if any(t.is_alive() for t in threads):
                self.master.after(100, poll)
            else:
                self.con_t = time.perf_counter() - start
                self.status.set(f"Concurrent done in {self.con_t:.2f}s")
                self._chart()

        self.master.after(100, poll)

    def fetch_sequential(self):
        self._clear()
        self.status.set("Fetching sequentially ...")
        q = queue.Queue()
        start = time.perf_counter()
        for city in CITIES:
            fetch_city(city, q, self.lock)
            self._insert(q.get())
            self.master.update()  # keep GUI responsive
        self.seq_t = time.perf_counter() - start
        self.status.set(f"Sequential done in {self.seq_t:.2f}s")
        self._chart()

    def _chart(self):
        self.ax.clear()
        labels, vals = [], []
        if self.seq_t is not None:
            labels.append("Sequential")
            vals.append(self.seq_t)
        if self.con_t is not None:
            labels.append("Concurrent")
            vals.append(self.con_t)
        if vals:
            bars = self.ax.bar(labels, vals, color=["#777777", "#333333"][:len(vals)], width=0.35)
            for bar, v in zip(bars, vals):
                self.ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                             f"{v:.2f}s", ha="center", fontsize=9, fontweight="bold")
            self.ax.set_ylabel("Time (s)")
            self.ax.set_title("Sequential vs Concurrent Latency", fontweight="bold")
            self.ax.set_ylim(0, max(vals) * 1.4 + 0.5)
            self.fig.tight_layout()
            self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    WeatherApp(root)
    root.mainloop()