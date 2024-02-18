import random

from mfire.utils.selection import Selection


class SelectionFactory(Selection):
    sel = {"id": random.randint(0, 42)}
    islice = {"valid_time": slice(random.randint(0, 42), random.randint(0, 42))}
    isel = {"latitude": random.randint(0, 42)}
    slice = {"longitude": slice(random.randint(0, 42), random.randint(0, 42))}
