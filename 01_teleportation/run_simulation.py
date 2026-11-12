import logging
import os

from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run

from application import TeleportParams, AliceProgram, BobProgram

if __name__ == "__main__":
    
    # import network configuration from config file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cfg_file_path = os.path.join(current_dir, "config.yaml")
    cfg = StackNetworkConfig.from_file(cfg_file_path)

    # generate parameters randomly
    params = TeleportParams.generate_random_params()

    # Create instances of programs to run
    alice_program = AliceProgram(params)
    bob_program = BobProgram()

    # toggle logging. Set to logging.INFO for logging of events.
    alice_program.logger.setLevel(logging.ERROR)
    bob_program.logger.setLevel(logging.ERROR)

    # Run the simulation. Programs argument is a mapping of network node labels to programs to run on that node
    alice_result, bob_result = run(config=cfg,
        programs={"Alice": alice_program, "Bob": bob_program, }, num_times=1)

    print(params)
    print(f"State to teleport:\n{alice_result[0]['original_dm']}")
    print(f"State received:\n{bob_result[0]['final_dm']}")