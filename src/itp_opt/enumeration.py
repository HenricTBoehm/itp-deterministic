from __future__ import annotations

from itertools import product

from .constraints import Constraint, assess
from .models import Catalog, Configuration, Status


def generate(catalog: Catalog):
    """Yield configurations in stable lexicographic catalog order."""
    for parts in product(catalog.floor_slabs, catalog.ceilings, catalog.exterior_walls,
                         catalog.interior_walls, catalog.windows, catalog.main_doors,
                         catalog.secondary_doors):
        floor, ceiling, exterior, interior, window, main, secondary = parts
        thickness = {"Concrete slab_130": 130, "Concrete slab_150": 150, "Concrete slab_200": 200,
                     "Panels_10": 11, "Panels_13": 14, "Panels_15": 16.5,
                     "Brick Wall_100": 100, "Brick Wall_150": 150,
                     "Brick Wall_200": 200, "Brick Wall_250": 250}
        window_values = {
            "S6_1015_2HDL": (1.5, 1), "S6_1215_2HDL": (1.8, 1), "S6_1415_2HDL": (2.1, 1),
            "D6_1015_2HDL": (1.5, 2), "D6_1215_2HDL": (1.8, 2), "D6_1415_2HDL": (2.1, 2),
        }
        door_values = {"1622_2HDL": 3.52, "1822_2HDL": 3.96, "2022_2HDL": 4.4,
                       "0621_1HDL": 1.26, "0821_1HDL": 1.68}
        values = {}
        if all(part in thickness for part in (floor, ceiling, exterior, interior)) and window in window_values:
            values = {"x1": thickness[floor], "x2": thickness[ceiling], "x3": thickness[exterior],
                      "x4": thickness[interior], "x5": window_values[window][0],
                      "x6": window_values[window][1], "x7": door_values[main],
                      "x8": door_values[secondary]}
        yield Configuration.create(floor_slab=floor, ceiling=ceiling, exterior_wall=exterior,
                                   interior_wall=interior, window=window, main_door=main,
                                   secondary_door=secondary, values=values)


def enumerate_with_status(catalog: Catalog, constraints: list[Constraint]):
    for configuration in generate(catalog):
        status, details = assess(configuration, constraints)
        reason = "; ".join(r.reason for r in details if r.status is not Status.ADMISSIBLE)
        yield configuration, status, reason
