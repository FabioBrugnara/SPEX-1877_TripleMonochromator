import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tkinter as tk
from tkinter import ttk

# app that plots random data

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Random Data Plotter")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.create_widgets()
        self.root.mainloop()

    def create_widgets(self):
        self.frame1 = ttk.Frame(self.root, padding=10)
        self.frame1.pack()

        self.button = ttk.Button(self.frame1, text="Plot Data", command=self.plot_data)
        self.button.grid(row=0, column=0, padx=10, pady=10)

        self.frame2 = ttk.Frame(self.root, padding=10)
        self.frame2.pack()

        self.label = ttk.Label(self.frame2, text="Data Points: ")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.entry = ttk.Entry(self.frame2, width=5)
        self.entry.grid(row=0, column=1, padx=10, pady=10)
        self.entry.insert(0, 100)

        self.frame3 = ttk.Frame(self.root, padding=10)
        self.frame3.pack()

        self.label2 = ttk.Label(self.frame3, text="Interval: ")
        self.label2.grid(row=0, column=0, padx=10, pady=10)

        self.entry2 = ttk.Entry(self.frame3, width=5)
        self.entry2.grid(row=0, column=1, padx=10, pady=10)
        self.entry2.insert(0, 100)

    def plot_data(self):
        self.data_points = int(self.entry.get())
        self.interval = int(self.entry2.get())
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ani = animation.FuncAnimation(self.fig, self.animate, interval=self.interval)
        plt.show()

    def animate(self, i):
        self.ax.clear()
        self.ax.set_title("Random Data")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.plot(np.random.rand(self.data_points))

    def on_closing(self):
        self.root.destroy()

if __name__ == "__main__":
    app = App()

