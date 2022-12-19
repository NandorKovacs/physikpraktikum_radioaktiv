# PyRademo - Demostration von Radioaktivität

## Usage

First generate a simulation. It will write two files: a `.sim` file, which contains
all the parameters of the simulation, and a `.events` file, which contains the
raw data.

To run a simulation, you need to a file that describes a decay chain. An example
for the Thorium decay chain is in `data/thorium.decaychain`.

Run a simulation the following way:

```
python3 write_raw_events.py -o foo -n 100 --decay-chain data/thorium.decaychain --total-time "20 a"
```

Parameters:

*   `-o` - Output basename. In the example above, the program will create `foo.sim` and `foo.events`.
*   `-n` - Number of particles. Values between 100 and 100k work well.
*   `--decay-chain` - A file describing a decay chain. See the header of `data/thorium.decaychain` for its format.
*   `--total-time` - The total time for the simulation to be run. You need a space between the time and
    the time unit. The numerical value can use scientific notation, like 2e3 for 2000. The available
    time units are documented at the top of `pyrademo/timeparser.py`, and they are `ns` for nanoseconds,
    `s` for seconds, `min` for minutes, `h` for hours, `d` for days, and `a` for years (following Wikipedia's notation.)

Once you have a simulation output, you can use the plot commands:

```
python3 plot_num_particles_per_isotope.py -i foo.sim
python3 plot_released_energy_per_isotope.py -i foo.sim
```
