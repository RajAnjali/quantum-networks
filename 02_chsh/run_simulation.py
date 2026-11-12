import logging
import os
import numpy

from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run

from application import AliceProgram, BobProgram


def game_won(x, y, a, b):
    if x == 1 and y == 1:
        if a != b:
            return "Alice and Bob won the game, since x * y = 1 and a ^ b = 1"
        else:
            return "Alice and Bob lost the game, since x * y = 1 and a ^ b = 0"
    else:
        if a == b:
            return "Alice and Bob won the game, since x * y = 0 and a ^ b = 0"
        else:
            return "Alice and Bob lost the game, since x * y = 0 and a ^ b = 1"



if __name__ == "__main__":
    # import network configuration from config file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cfg_file_path = os.path.join(current_dir, "config.yaml")
    cfg = StackNetworkConfig.from_file(cfg_file_path)

    # generate x & y randomly
    x = numpy.random.randint(0, 2)
    y = numpy.random.randint(0, 2)

    # Step 1
    # Create instances of programs to run
    alice_program = AliceProgram(x)
    bob_program = BobProgram(y)

    # toggle logging. Set to logging.INFO for logging of events.
    alice_program.logger.setLevel(logging.ERROR)
    bob_program.logger.setLevel(logging.ERROR)

    # Run the simulation. Programs argument is a mapping of network node labels to programs to run on that node
    alice_result, bob_result = run(config=cfg, programs={"Alice": alice_program, "Bob": bob_program}, num_times=1)

    # Step 4
    a = alice_result[0]["a"]
    b = bob_result[0]["b"]

    # Step 5
    print(game_won(x, y, a, b))
