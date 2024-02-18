
from cioseq.sequence import Sequence
import os
import logging
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import mplcursors
import subprocess
import platform
import pyperclip


LOG_FORMATTER = logging.Formatter(
    "%(asctime)s  %(name)s%(levelname)9s %(filename)s-%(lineno)d %(threadName)s:  %(message)s"
)

logger = logging.getLogger("conductor.check_sequence")


BYTES_TO_MB = 1.0 / (1024 * 1024)
MAJOR_STEPS = 20

EXIST_COLOR = "dodgerblue"
MISSING_COLOR = "red"
EMPTY_COLOR = "whitesmoke"
GRID_COLOR = "black"
CORRUPT_COLOR = "darkmagenta"
BLACK = "black"
OUTER_MARGIN_COLOR = "#bbb"
INNER_COLOR = "#ccc"
ARROW_COLOR = "#777"
ANNOTATION_BG_COLOR = "#aaf"

class BarChart(object):

    ICON_CLIP = plt.imread(os.path.join(os.path.dirname(__file__), "icons", "clip.png"))
    ICON_TICK = plt.imread(os.path.join(os.path.dirname(__file__), "icons", "tick.png"))

    def __init__(self):
        plt.style.use("ggplot")

        fig, ax = plt.subplots()
        self.fig = fig
        self.ax = ax

        self.ax.set_ylabel("File Size (Mb)", weight="bold")
        self.ax.set_title("", fontsize=20)
        self.fig.set_figwidth(12)
        self.fig.set_figheight(6)

        self.fig.patch.set_facecolor(OUTER_MARGIN_COLOR)
        self.ax.set_facecolor(INNER_COLOR)
        
        self.fig.subplots_adjust(left=0.08, right=0.96, top=0.9, bottom=0.1)

        self.descriptor = None
        self.files = None
        self.max_size = None
        self.min_size = None
        self.padding = None
        self.prefix = None
        self.extension = None
        self.sequence = None
        self.bad_frame_sequence = None

        self.frame_numbers = None
        self.indices = None
        self.heights = None

        self.bars = None

        self.hover_cursor = None

    def update(self, data):
        self.descriptor = data["descriptor"]
        self.files = data["files"]
        self.max_size = data["max_size"]
        self.min_size = data["min_size"]
        self.padding = data["padding"]
        self.prefix = data["prefix"]
        self.extension = data["extension"]
        self.sequence = data["sequence"]
        self.frame_numbers = [file["frame"] for file in self.files]
        self.indices = range(len(self.files))
        self.heights = [
            file["size"] * BYTES_TO_MB
            if file["size"] > 0
            else self.max_size * BYTES_TO_MB
            for file in self.files
        ]
        bad_frames = [file["frame"] for file in self.files if file["size"] == 0]
        if bad_frames:
            self.bad_frame_sequence = Sequence.create(bad_frames)

        self.set_window_title()
        self.update_bad_frames()
        self.draw_bars()
        self.set_ticks()
        self.set_tooltips()
        self.set_bar_events()
        self.set_clipboard_button()

    def set_window_title(self):
        self.fig.canvas.manager.set_window_title(self.descriptor)
        
    def draw_bars(self):
        self.bars = self.ax.bar(
            self.indices, self.heights, width=0.9, alpha=0.8, color=EXIST_COLOR
        )
        for i in range(len(self.files)):
            self.style_bar(i)
 
    def style_bar(self, index):
        file = self.files[index]
        bar = self.bars[index]
        bad = file["size"] == 0 or file["corrupt"]
        bar.set_color(EMPTY_COLOR if file["size"] == 0 else EXIST_COLOR)
        bar.set_hatch("///" if bad else "")
        bar.set_edgecolor(CORRUPT_COLOR if file["corrupt"] else EXIST_COLOR if file["exists"] else MISSING_COLOR)
        self.fig.canvas.draw_idle()

    def set_ticks(self):
        num_files = len(self.files)
        majorstep = int(num_files / MAJOR_STEPS) 
        major_ticks = range(0, num_files, majorstep)
        major_tick_labels = [self.frame_numbers[i] for i in major_ticks]
        self.ax.set_xticks(major_ticks)
        self.ax.set_xticklabels(major_tick_labels)
        self.ax.grid(which="major", alpha=0.2, color=GRID_COLOR)

    def update_bad_frames(self, index=None, add=True):
        if index is not None:
            file = self.files[index]
            if file["size"] > 0:
                # we dont modify zero-size or missing files
                frame = [self.frame_numbers[index]]
                # we are adding or removing a frame
                if self.bad_frame_sequence:
                    if add:
                        self.bad_frame_sequence = self.bad_frame_sequence.union(frame)
                    else:
                        self.bad_frame_sequence = self.bad_frame_sequence.difference(frame)
                else:
                    if add:
                        self.bad_frame_sequence =  Sequence.create(frame)

                if add:
                    self.files[index]["corrupt"] = True
                else:
                    self.files[index]["corrupt"] = False
                
                self.style_bar(index)
                

        # update the title
        if self.bad_frame_sequence:
            num = len(self.bad_frame_sequence)
            self.ax.set_title(f"{num} bad frames: {self.bad_frame_sequence}", weight="bold", fontsize=8)
        else:
            self.ax.set_title(f"No bad frames", weight="bold", fontsize=10)
        self.fig.canvas.draw_idle()

    def set_tooltips(self):
        self.hover_cursor = mplcursors.cursor(self.bars, hover=True)
        self.hover_cursor.connect("add", self.on_bar_hover)

    def set_bar_events(self):
        plt.connect("button_press_event", self.on_bar_click)


    def set_clipboard_button(self):
        self.clip_button_ax = plt.axes([0.96, 0.94, 0.04, 0.04])
        self.clip_button = Button(self.clip_button_ax, "", image=BarChart.ICON_CLIP)
        self.clip_button.on_clicked(self.copy_to_clipboard)
        self.clip_button.hovercolor =  EMPTY_COLOR
        
        self.clip_button_ax.spines['top'].set_visible(False)
        self.clip_button_ax.spines['right'].set_visible(False)
        self.clip_button_ax.spines['bottom'].set_visible(False)
        self.clip_button_ax.spines['left'].set_visible(False)


    def copy_to_clipboard(self, event):
        text = str(self.bad_frame_sequence)
        pyperclip.copy(text)
        self.clip_button_ax.images[0].set_data(BarChart.ICON_TICK)
        # self.fig.canvas.draw_idle()
        event.canvas.draw()

    def copy_to_clipboard_hover(self, event):
        event.button.color = 'red'  # Change button color on hover
        event.canvas.draw()

    def on_bar_click(self, event):
        self.clip_button_ax.images[0].set_data(BarChart.ICON_CLIP)
        if not (event.dblclick and event.button == 1):
            return
        index = int(event.xdata + 0.5)

        if index < 0 or index >= len(self.files):
            return

        file = self.files[index]

        if event.key:
            # print("KEY PRESSED IS:", event.key)
            # frame = [file["frame"]]
            if event.key  in ["=", "+"]:
                # add to bad frames
                self.update_bad_frames(index=index, add=True)
                return
            elif event.key in ["-", "_"]:
                # remove from bad frames
                self.update_bad_frames(index=index, add=False)
                return
            
            
        file_path = file["filepath"]
        # Just a regular double click - open the file.
        operating_system = platform.system()

        try:
            if operating_system == "Darwin":
                subprocess.run(["open", file_path])
            elif operating_system == "Windows":
                subprocess.run(["start", file_path], shell=True)
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
        except FileNotFoundError:
            print(f"Failed to open the file '{file_path}'.")

    def on_bar_hover(self, sel):
        file_index = sel.index

        file = self.files[file_index]

        human_size = file["human_size"]
        exists = file["exists"]
        path = file["filepath"]
        basename = os.path.basename(path)
        text = f"{basename}\nSize: {human_size}\nExists: {exists}"
        fontcolor = (
            BLACK
            if exists and file["size"] > 0
            else EXIST_COLOR
            if exists
            else MISSING_COLOR
        )
        sel.annotation.set(
            text=text,
            weight="bold",
            fontsize=8,
            color=fontcolor,
            backgroundcolor=ANNOTATION_BG_COLOR,
            bbox=dict(boxstyle="round", fc="w", ec="k", pad=0.2, alpha=0.8),
        )
        sel.annotation.arrow_patch.set(
            arrowstyle="->", linewidth=2, color=ARROW_COLOR, alpha=0.8
        )

    def show(self):
        plt.show()
