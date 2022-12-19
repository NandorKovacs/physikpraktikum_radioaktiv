"""Simulation code for a concrete decay process."""

import numpy
from dataclasses import dataclass

from .model import DecayEvent
from .model import DecayChain
from .model import Isotope
from .model import SimulationConfig


class SimulationBase:
    """A base class for simulations of a concrete decay process.

    Contains the core logic of computing a single decay event.

    Attributes:
      cfg: SimulationConfig, holding the main options for the simulation.
    """

    def __init__(self, cfg: SimulationConfig, rng: numpy.random.Generator = numpy.random.default_rng()) -> None:
        self.cfg = cfg
        self.rng = rng

    def _generate_decay_event(self, particle: int, isotope: Isotope, t: float) -> DecayEvent | None:
        """Given an isotope, generates a random decay event.

        In case only one decay mode is possible, it chooses that. If both alpha
        and beta decay is available from the isotope, then it takes the
        probability parameter of the decays into account to draw a decay type.

        Args:
          particle: The index of the particle. Only used to fill in to
          DecayEvent. isotope: The isotope for which to compute the decay event.
          t: The absolute time when the simulated single decay process starts.

        Returns:
          A DecayEvent, or None, if the isotope is stable.
        """
        decay = isotope.pick_decay(self.rng)
        if decay is None:
            return None

        decay_time = t + self.rng.exponential(1.0 / decay.rate)

        return DecayEvent(
            particle=particle,
            from_isotope=isotope.index,
            to_isotope=decay.to_isotope,
            time=decay_time,
            energy=decay.energy,
        )

    def simulate_one_particle(self, particle: int) -> list[DecayEvent]:
        """Simulates one particle.

        Assumes it to start from isotope 0 of the decay chain. Stops when either
        the particle reaches a stable isotope, or if the randomly chosen next
        decay time is after `total_time`.

        Returns:
          DecayEvent objects, which all have their time within [0, total_time].
        """
        events: list[DecayEvent] = []
        t = 0.0
        isotope_id = 0

        while True:
            isotope = self.cfg.decay_chain.isotopes[isotope_id]
            decay_event = self._generate_decay_event(particle, isotope, t)
            if decay_event is None:
                break
            if decay_event.time > self.cfg.total_time:
                break
            events.append(decay_event)
            t = decay_event.time
            isotope_id = decay_event.to_isotope

        return events


class RawSimulator(SimulationBase):
    """Runs the simulation, and provides the raw events.

    Given a decay chain, and a number of particles, all assumed to be the 0th
    isotope of the decay chain, the simulation will generate for each particle
    random times, when the particle experienced alpha or beta decay. The
    simulation process is started with a total_time parameter. The simulation
    ends for a particle, when first a decay time leads to after the total_time
    elapsed."""

    def simulate(self) -> list[DecayEvent]:
        events: list[DecayEvent] = []

        for p in range(self.cfg.num_particles):
            events.extend(self.simulate_one_particle(p))

        return events
