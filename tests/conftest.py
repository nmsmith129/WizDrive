import os

# Must be set at module level, before any import of pygame. claude_code_visualizer
# calls pygame.init() at import time, so the dummy driver must be in place first.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest


@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    import pygame
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture(scope="session", autouse=True)
def disable_map_loader_debug():
    import map_loader
    map_loader.debug = False
