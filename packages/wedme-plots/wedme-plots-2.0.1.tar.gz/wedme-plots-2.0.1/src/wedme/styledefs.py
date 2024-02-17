import importlib_resources as _resources
import matplotlib.pyplot as _plt
import matplotlib as _mpl
from wedme.const import *


## Functions for applying the wedme styles
def _apply_style(stylename):
    with _resources.files("wedme") / f"{stylename}.mplstyle" as file_path:
        _plt.style.use(file_path)


def reset():
    _mpl.rcParams.update(_mpl.rcParamsDefault)


def _common():
    _apply_style("common")


def slide():
    _common()
    _apply_style("slides")


def paper():
    _common()
    _apply_style("elspaper")


def dev():
    paper()
    _mpl.rcParams["figure.dpi"] = 200


def poster():
    _common()
    _apply_style("a0")


## Some more utility functions
class _metafigure(type):
    # Catch-all for figure types. Any method call to this class will get intercepted here.
    def __getattr__(cls, name: str):
        # `name` is the name of the method that was called
        nameparts = name.upper().split("_")

        stylename = nameparts[0]
        if stylename not in ["PAPER", "SLIDE", "POSTER"]:
            raise ValueError(
                f"Unknown figure type {stylename}. Must be one of PAPER, SLIDE, or POSTER"
            )
        # If the name is not of the form `TYPE_WIDTH_HEIGHT`, then we assume it is just a type
        if len(nameparts) != 3:
            figsize = None
        # Otherwise, we assume it is of the form `TYPE_WIDTH_HEIGHT`
        else:
            # Extract the type, width, and height
            wname, hname = nameparts[1:]
            if wname.startswith("H"):
                hname, wname = nameparts[1:]

            wname = "_".join([stylename, wname])
            hname = "_".join([stylename, hname])

            # Get the width and height from the defined variables in this script
            h = globals()[hname]
            w = globals()[wname]
            figsize = (w, h)

        # Define a new function that calls the `figure` method with the appropriate arguments
        def myfig(*args, stylename=stylename, **kwargs):
            # Update the keyword arguments with the figure size
            kws = {}
            kws.update(kwargs)
            kws.update(figsize=figsize)

            # Call the appropriate figure type
            if stylename == "PAPER":
                paper()
            elif stylename == "SLIDE" or stylename == "SLIDES":
                stylename = "SLIDE"
                slide()
            elif stylename == "POSTER":
                poster()
            else:
                raise ValueError(f"Unknown figure type {stylename}")

            # Call the figure method with the updated arguments
            return _plt.figure(*args, **kws)

        # Return the new function handle. When one calls `wedme.figure.TYPE_WIDTH_HEIGHT()`,
        # `wedme.figure.TYPE_WIDTH_HEIGHT` returns the function handle `myfig`
        return myfig


class figure(metaclass=_metafigure):
    pass
