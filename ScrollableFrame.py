from tkinter import ttk, Canvas

class ScrollableFrame(ttk.Frame):
    '''Frame with scrollbars. Can can be vertical, horizontal or or both.
    Use self.scrollable_frame to acces content of frame'''
    def __init__(self, container, orientation ="vertical", *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = Canvas(self)
        self.canvas.configure(width=250,height = 250)
        if orientation == "vertical":
            scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
            self.scrollable_frame = ttk.Frame(self.canvas)
            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")))
            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.canvas.configure(yscrollcommand=scrollbar.set)
            self.canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        elif orientation == "horizontal":
            scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
            self.scrollable_frame = ttk.Frame(self.canvas)
            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")))
            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.canvas.configure(xscrollcommand=scrollbar.set)
            self.canvas.pack(side="top",fill="both",expand=True)
            scrollbar.pack(side="bottom", fill="x")
        elif orientation == "both":
            vertbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
            horbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
            self.scrollable_frame = ttk.Frame(self.canvas)
            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")))
            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.canvas.configure(xscrollcommand=horbar.set)
            self.canvas.configure(yscrollcommand=vertbar.set)
            vertbar.pack(side="right", fill="y")
            self.canvas.pack(side="top",fill="both",expand=True)
            horbar.pack(side="bottom", fill="x")
        else:
            raise("orientation required. Use vertical,horizontal,both")

    def frame(self):
        '''Shortcut for easier use'''
        return self.scrollable_frame
