import importlib.metadata

__version__ = importlib.metadata.version("fourier_grx")

from fourier_grx.main.main import (
    main as run,
)
