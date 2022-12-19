"""Module to read config files for pyrademo."""

from enum import Enum
from math import log
from typing import Final

from .model import Decay
from .model import DecayChain
from .model import Isotope
from .timeparser import parse_time


class _DecayType(Enum):
    """An enum representing the decay type."""
    ALPHA = 1
    BETA = 2


class _ParsedLine:
    """A class representing directly a line in the textual representation of
       a decay chain.
       
    Attributes:
      from_name: The human name of the decaying isotope.
      to_name: The human name of the decay target.
      decay_type: A _DecayType enum value, describing if it is alpha or beta decay.
      probability: In case there are multiple decay options, the probability of
        this one happening.
      half_time: The half time parameter of the decay.   
    """

    from_name: str
    to_name: str
    decay_type: _DecayType
    probability: float
    half_time: float
    energy: float

    def __init__(self, line: str):
        parts = line.split()
        self.from_name = parts[0]
        self.to_name = parts[1]
        self.decay_type = _DecayType[parts[2].upper()]
        self.probability = float(parts[3])
        self.half_time = parse_time(float(parts[4]), parts[5])
        self.energy = float(parts[6])


def _ensure_isotope(decay_chain: DecayChain, name: str) -> int:
    """Ensures, that an isotope with the given name exists, and
    returns its index."""
    for index, isotope in enumerate(decay_chain.isotopes):
        if isotope.name == name:
            return index
    new_index = len(decay_chain.isotopes)
    decay_chain.isotopes.append(Isotope(new_index, name))
    return new_index


_LN2: Final[float] = log(2)


def read_decay_chain(file_name: str) -> DecayChain:
    """Parses a text file describing a decay chain.

    Args:
      file_name: the file to parse.

    Returns:
      The DecayChain object, representing the file.
    """
    decay_chain = DecayChain()
    with open(file_name, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if line.startswith("#"):
                continue
            parsed_line = _ParsedLine(line)
            from_index = _ensure_isotope(decay_chain, parsed_line.from_name)
            to_index = _ensure_isotope(decay_chain, parsed_line.to_name)
            d = Decay(
                rate=_LN2 / parsed_line.half_time,
                probability=parsed_line.probability,
                to_isotope=to_index,
                energy=parsed_line.energy,
            )
            if parsed_line.decay_type == _DecayType.ALPHA:
                decay_chain.isotopes[from_index].alpha_decay = d
            else:
                decay_chain.isotopes[from_index].beta_decay = d
    return decay_chain
