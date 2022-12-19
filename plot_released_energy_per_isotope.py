"""Plots the cumulative released energy per isotope in the function of time."""

import pprint
import argparse
import sys
from dataclasses import dataclass
import matplotlib.pyplot as plt
import numpy

from pyrademo import model

parser = argparse.ArgumentParser(
    prog="plot_released_energy_per_isotope.py",
    description="Plots the cumulative released energy per isotope, in MeV.",
)

parser.add_argument("-i", "--input", required=True,
                    help="A simulation, produced by write_raw_events.py. Either the filename of a .sim file, or its base name.")
parser.add_argument("--ymax", required=False, type=int,
                    help="The maximum of the y scale. Auto-scales if not provided.")

args = parser.parse_args(sys.argv[1:])

sr = model.SimulationResults.from_file(args.input)


@dataclass
class Point:
    """A point on a single graph."""
    time: float
    num: float


@dataclass
class Graph:
    """A single graph (representing number of particles of a single isotope."""
    name: str
    points: list[Point]


# We create a graph for each isotope in the decay chain. We add a point to time 0.0
# with value 0.
graphs: list[Graph] = list(map(lambda isotope: Graph(isotope.name, [Point(0.0, 0.0)]),
                               sr.cfg.decay_chain.isotopes))

for e in sr.data:
    # We fill out the graphs with the change initially. We will compute cumulative
    # value later, just after we sorted by time.
    graphs[e.from_isotope].points.append(Point(e.time, e.energy))
    graphs[e.to_isotope].points.append(Point(e.time, e.energy))

for graph in graphs:
    # For each isotope, we sort the decay events by time.
    graph.points.sort(
        key=lambda p: p.time
    )
    # We convert the values in the num field of the points to cumulative:
    cumulative_num = graph.points[0].num
    for i in range(1, len(graph.points)):
        graph.points[i].num += cumulative_num
        cumulative_num = graph.points[i].num


fig, ax = plt.subplots()

for graph in graphs:
    x = numpy.array(list(map(lambda p: p.time, graph.points)), dtype=float)
    y = numpy.array(list(map(lambda p: p.num, graph.points)), dtype=int)
    ax.plot(x, y, linewidth=1.0, label=graph.name)


ax.legend()

if args.ymax is not None:
    ax.set(ylim=(0, args.ymax))

ax.set_ylabel("MeV")
ax.set_xlabel("sec")

ax.set_title("num_particles={}".format(sr.cfg.num_particles))
fig.suptitle("Cumulative released energy per isotope in time")

plt.savefig(sr.cfg.file_base_name+"-released_energy_per_isotope.png")
plt.show()
