import numpy

from netqasm.sdk import Qubit
from squidasm.sim.stack.common import LogManager
from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta


class AliceProgram(Program):
    PEER_NAME = "Bob"

    def __init__(self, x: int):
        self.logger = LogManager.get_stack_logger(self.__class__.__name__)
        self.x = x

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="alice_program",
            csockets=[self.PEER_NAME],
            epr_sockets=[self.PEER_NAME],
            max_qubits=2,
        )

    @staticmethod
    def measure_basis_0(q: Qubit):
        return q.measure()

    @staticmethod
    def measure_basis_1(q: Qubit):
        q.H()
        return q.measure()

    def run(self, context: ProgramContext):
        epr_socket = context.epr_sockets[self.PEER_NAME]
        connection = context.connection

        # Step 2
        epr = epr_socket.create_keep()[0]
        yield from connection.flush()
        self.logger.info("Finished EPR pair creation")

        # Step 3
        # CHSH strategy: measure in one of 2 bases depending on x.
        self.logger.info(f"Measuring in basis x = {self.x}")
        if self.x == 0:
            a = self.measure_basis_0(epr)
        else:
            a = self.measure_basis_1(epr)

        yield from connection.flush()
        self.logger.info(f"Measured a: {a}")

        # Step 4
        return {"x": self.x, "a": a}


class BobProgram(Program):
    PEER_NAME = "Alice"

    def __init__(self, y: int):
        self.logger = LogManager.get_stack_logger(self.__class__.__name__)
        self.y = y

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="bob_program",
            csockets=[self.PEER_NAME],
            epr_sockets=[self.PEER_NAME],
            max_qubits=2,
        )

    @staticmethod
    def measure_basis_0(q: Qubit):
        q.rot_Y(angle=-numpy.pi / 4)
        return q.measure()

    @staticmethod
    def measure_basis_1(q: Qubit):
        q.rot_Y(angle=numpy.pi / 4)
        return q.measure()

    def run(self, context: ProgramContext):
        epr_socket = context.epr_sockets[self.PEER_NAME]
        connection = context.connection

        # Step 2
        epr = epr_socket.recv_keep()[0]
        yield from connection.flush()
        self.logger.info("Finished EPR pair creation")

        # Step 3
        # CHSH strategy: measure in one of 2 bases depending on y.
        self.logger.info(f"Measuring in basis y = {self.y}")
        if self.y == 0:
            b = self.measure_basis_0(epr)
        else:
            b = self.measure_basis_1(epr)

        yield from connection.flush()
        self.logger.info(f"Measured b: {b}")

        # Step 4
        return {"y": self.y, "b": int(b)}

