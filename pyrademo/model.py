"""Radioactive decay modeling.

This module contains classes to model radoactive decay chains.
"""

from __future__ import annotations

import pprint
import numpy
from dataclasses import dataclass
from dataclasses import field


@dataclass
class Decay:
    """Models a possible decay of an isotope to another.

    Attributes:
      rate: The rate constant (lambda).
      probability: The probability, that among the possible decays from one isotope,
        this one happens.
      to_isotope: Id of the decay target isotope within the DecayChain.
      energy: released energy, in MeV
    """

    rate: float
    probability: float
    to_isotope: int
    energy: float


@dataclass
class Isotope:
    """Models an isotope.

    Attributes:
      index: An integer, the index within DecayChain.isotopes.
      name: A human readable name.
      alpha_decay: A Decay, if the isotope decays via alpha decay, None otherwise.
      beta_decay: A Decay, if the isotope decays via beta decay, None otherwise.
    """

    index: int
    name: str
    alpha_decay: Decay | None = None
    beta_decay: Decay | None = None

    def pick_decay(self, rng: numpy.random.Generator) -> Decay | None:
        if self.alpha_decay is None and self.beta_decay is None:
            return None
        if self.alpha_decay == None:
            return self.beta_decay
        if self.beta_decay == None:
            return self.alpha_decay
        # TODO: verify if the two probabilities add up to 100, here or
        # in the constructor.
        if rng.uniform(0.0, 100.0) < self.alpha_decay.probability:
            return self.alpha_decay
        return self.beta_decay


@dataclass
class DecayChain:
    """Models a decay chain.

    While the traditional name of "chain" suggests that this is a linear chain,
    in reality it's a DAG, with nodes being elements, edges being alpha or beta
    decays.

    The element with index 0 is special, it is the starting element for the
    decay simulation.

    Attributes:
      isotopes: A list of all the isotopes in the decay tree.
    """

    isotopes: list[Isotope] = field(default_factory=list)


@dataclass
class DecayEvent:
    """Models a single decay event during a simulation.

    Attributes:
      particle: The index of the particle.
      from_isotope: The index of the decaying isotope within the DecayChain.
      to_isotope: The index of the decay target within the DecayChain.
      time: The absolute time in seconds, when the decay event happens.
      energy: Released energy, in MeV.
    """

    particle: int
    from_isotope: int
    to_isotope: int
    time: float
    energy: float

    def as_line(self) -> str:
        """Returns a simplistic, line oriented representation of the DecayEvent."""
        return "{} {} {} {} {}".format(self.particle, self.from_isotope, self.to_isotope, self.time, self.energy)

    @staticmethod
    def header() -> str:
        """Returns the header for the line oriented format."""
        return "particle from_isotope to_isotope time_sec energy_MeV"

    @staticmethod
    def from_line(line: str) -> DecayEvent:
        """Returns a DecayEvent from a line produced by as_line."""
        parts = line.split()
        return DecayEvent(int(parts[0]), int(parts[1]), int(parts[2]), float(parts[3]), float(parts[4]))


@dataclass
class SimulationConfig:
    """A base config for simulations."""

    decay_chain: DecayChain
    num_particles: int
    total_time: float
    file_base_name: str

    def write_file(self):
        """Writes the simulation config to file."""
        with open(self.file_base_name+".sim", "w") as f:
            f.write(pprint.pformat(self))

    @staticmethod
    def from_file(file_name: str) -> SimulationConfig:
        if not file_name.endswith(".sim"):
            file_name = file_name + ".sim"

        with open(file_name, "r") as f:
            contents = f.read()
            return eval(contents)


@dataclass
class SimulationResults:
    """A data structure representing results of a simulation."""

    cfg: SimulationConfig
    data: list[DecayEvent]

    def write_file(self) -> None:
        """Writes the simulation results to files."""
        with open(self.cfg.file_base_name+".events", "w") as f:
            f.write("# " + DecayEvent.header() + "\n")
            for event in self.data:
                f.write(event.as_line())
                f.write("\n")
        self.cfg.write_file()

    def from_file(file_name: str) -> SimulationResults:
        """Reads the simulation results from files."""
        cfg = SimulationConfig.from_file(file_name)
        events: list[DecayEvent] = []

        data_file_name = file_name.removesuffix(".sim") + ".events"
        with open(data_file_name, "r") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                line = line.strip()
                if line.startswith("#") or line == "":
                    continue
                events.append(DecayEvent.from_line(line))

        return SimulationResults(cfg, events)
