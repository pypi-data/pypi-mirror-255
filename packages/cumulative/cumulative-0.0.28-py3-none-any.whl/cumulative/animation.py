from functools import partial

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import HTML, display
from matplotlib.animation import FuncAnimation
from tqdm.auto import tqdm

from cumulative.options import options
from cumulative.plot import Figure


class Animation:
    def __init__(self, c):
        self.c = c

    def render(self, func, n_frames=10, interval=20, show_percentage=True, html5=False):
        figure = Figure(ioff=True)

        mpl.rcParams["animation.embed_limit"] = 2**128

        pbar = tqdm(total=100, desc="animation", **options.get("tqdm"))

        def init_func():
            # We pass to FuncAnimation this empty init function to not call the expensive draw_frame.
            # (If no init_func is passed, func is called initially to clear the figure.)
            pass

        def draw_frame(figure, pct_frames, i_frame):

            pct_frame = pct_frames[i_frame]
            pct_frame_loop = pct_frame * 2

            if pct_frame_loop > 1:
                pct_frame_loop = 2 - pct_frame_loop

            figure.ax.clear()

            func(self.c, figure=figure, i_frame=i_frame, pct_frame=pct_frame, pct_frame_loop=pct_frame_loop)

            if show_percentage:
                figure.ax.text(
                    0.90,
                    0.05,
                    f"{pct_frame * 100:.0f}%".rjust(4),
                    horizontalalignment="center",
                    verticalalignment="center",
                    transform=figure.ax.transAxes,
                    color="white",
                )
            pbar.update(int(pct_frame * 100))

        self.anim = FuncAnimation(
            fig=figure.fig,
            init_func=init_func,
            func=partial(draw_frame, figure, np.linspace(0, 1, num=n_frames)),
            frames=n_frames,
            interval=interval,
        )

        # func is executed as part of .to_html5_video()

        if html5:
            video = self.anim.to_html5_video()
        else:
            video = self.anim.to_jshtml()

        pbar.close()

        html = HTML(video)
        display(html)
        plt.close()
