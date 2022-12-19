"""Plots the number of particles per isotope as a function of time."""

import argparse
import sys
from math import log
from math import exp
from dataclasses import dataclass
import matplotlib.pyplot as plt
import numpy

from pyrademo import model

parser = argparse.ArgumentParser(
    prog="plot_num_isotopes.py",
    description="Plots the number of isotopes in a simulation",
)

parser.add_argument("-i", "--input", required=True,
                    help="A simulation, produced by write_raw_events.py. Either the filename of a .sim file, or its base name.")
parser.add_argument("--ymax", required=False, type=int,
                    help="The maximum of the y scale. Auto-scales if not provided.")
parser.add_argument("-e", "--example-theoretical-curve", required=False, action="store_true",
                    help="Plot a theoretical curve for the amount of Th(228). Use it only when the decay chain is thorium.decaychain.")


args = parser.parse_args(sys.argv[1:])

sr = model.SimulationResults.from_file(args.input)


@dataclass
class Point:
    """A point on a single graph."""
    time: float
    num: int


@dataclass
class Graph:
    """A single graph (representing number of particles of a single isotope."""
    name: str
    points: list[Point]


# We create a graph for each isotope in the decay chain. We add a point to time 0.0
# with value 0.
graphs: list[Graph] = list(map(lambda isotope: Graph(isotope.name, [Point(0.0, 0)]),
                               sr.cfg.decay_chain.isotopes))

# In time 0.0 the starting isotope had all the particles.
graphs[0].points[0].num = sr.cfg.num_particles

for e in sr.data:
    # We fill out the graphs with the change initially. We will compute cumulative
    # value later, just after we sorted by time.
    graphs[e.from_isotope].points.append(Point(e.time, -1))
    graphs[e.to_isotope].points.append(Point(e.time, 1))

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
    ax.plot(x, y, linewidth=2.0, label=graph.name)

if args.example_theoretical_curve:
    # Partially for demonstration, but also to verify our model, we plot a
    # theoretical graph. This is an ad-hoc demonstration, and will only work
    # when the data is based on thoriumx.decaychain.

    ra228 = sr.cfg.decay_chain.isotopes[0]
    assert(ra228.name == "Ra(228)")
    lambda_a = ra228.beta_decay.rate

    th228 = sr.cfg.decay_chain.isotopes[2]
    assert(th228.name == "Th(228)")
    lambda_b = th228.alpha_decay.rate

    xf1 = numpy.linspace(0.0, sr.cfg.total_time, num=1000, dtype=float)
    yf1 = numpy.zeros(1000, float)
    c = lambda_a / (lambda_b - lambda_a) * sr.cfg.num_particles
    for i in range(1000):
        t = xf1[i]
        yf1[i] = c * (exp(-1 * lambda_a * t) - exp(-1 * lambda_b * t))

    ax.plot(xf1 ,yf1, linewidth=1.0, label="theoretical")

ax.legend()

save_fig_file_name = sr.cfg.file_base_name+"-num_particles_per_isotope.png"

if args.ymax is not None:
    ax.set(ylim=(0, args.ymax))
    save_fig_file_name = (sr.cfg.file_base_name+"-num_particles_per_isotope-ymax{}.png").format(args.ymax)

ax.set_ylabel("# of particles")
ax.set_xlabel("seconds")

ax.set_title("num_particles={}".format(sr.cfg.num_particles))
fig.suptitle("Number of particles per isotope in time")

plt.savefig(save_fig_file_name)
plt.show()
