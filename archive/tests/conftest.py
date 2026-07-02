import os

# Must be set at module level, before any import of pygame. Several modules call
# pygame.init() / create Surfaces at import time, so the dummy driver must be in
# place first to allow headless test runs.
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
    from wiz_drive import map_loader
    map_loader.debug = False
