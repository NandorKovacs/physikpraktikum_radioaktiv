"""Runs a simulations, and dumps raw events to a file."""

import argparse
import sys
import pprint

from pyrademo.decaychain import read_decay_chain
from pyrademo import model
from pyrademo import simulation
from pyrademo import timeparser

parser = argparse.ArgumentParser(
    prog="write_raw_events.py",
    description="Runs a simulation, and writes the raw events to a file.",
)

parser.add_argument("-o", "--output_base", required=True,
                    help="Basename of the output. Do not provide an extension. There will be two files written, a .cfg and a .data.")
parser.add_argument("-n", "--num-particles", required=True, type=int)
parser.add_argument("--decay-chain", required=True,
                    help="File name of a decay chain file.")
parser.add_argument("--total-time", required=True,
                    help="The total time for the simulation. A string in the form of `<number> <unit>`. Available units: {}".format(
                        timeparser.UNITS)
                    )

args = parser.parse_args(sys.argv[1:])

decay_chain = read_decay_chain(args.decay_chain)

cfg = model.SimulationConfig(
    decay_chain=decay_chain,
    num_particles=args.num_particles,
    total_time=timeparser.parse_time_str(args.total_time),
    file_base_name=args.output_base,
)

simulator = simulation.RawSimulator(cfg)

events = simulator.simulate()

model.SimulationResults(cfg, events).write_file()
