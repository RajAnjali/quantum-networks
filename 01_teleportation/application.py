from dataclasses import dataclass
import numpy

from netqasm.sdk import Qubit
from netqasm.sdk.classical_communication.message import StructuredMessage
from netqasm.sdk.toolbox.state_prep import set_qubit_state

from squidasm.sim.stack.common import LogManager
from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta
from squidasm.util import get_qubit_state, get_reference_state


@dataclass
class TeleportParams:
    phi: float = 0.0
    theta: float = 0.0

    @classmethod
    def generate_random_params(cls):
        """Create random parameters for a distributed CNOT program"""
        params = cls()
        params.theta = numpy.random.random() * numpy.pi
        params.phi = numpy.random.random() * numpy.pi
        return params


class AliceProgram(Program):
    PEER_NAME = "Bob"

    def __init__(self, params: TeleportParams):
        self.logger = LogManager.get_stack_logger(self.__class__.__name__)
        self.phi = params.phi
        self.theta = params.theta

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="controller_program",
            csockets=[self.PEER_NAME],
            epr_sockets=[self.PEER_NAME],
            max_qubits=2,
        )

    def run(self, context: ProgramContext):
        csocket = context.csockets[self.PEER_NAME]
        epr_socket = context.epr_sockets[self.PEER_NAME]
        connection = context.connection

        q = Qubit(connection)
        set_qubit_state(q, self.phi, self.theta)

        # Create EPR pairs
        epr = epr_socket.create_keep()[0]

        # Teleport
        q.cnot(epr)
        q.H()
        m1 = q.measure()
        m2 = epr.measure()
        yield from connection.flush()

        # Send the correction information
        m1, m2 = int(m1), int(m2)

        self.logger.info(f"Performed teleportation protocol with measured corrections: m1 = {m1}, m2 = {m2}")

        csocket.send_structured(StructuredMessage("Corrections", f"{m1},{m2}"))

        original_dm = get_reference_state(self.phi, self.theta)

        return {"m1": m1, "m2": m2, "original_dm": original_dm}


class BobProgram(Program):
    PEER_NAME = "Alice"

    def __init__(self):
        self.logger = LogManager.get_stack_logger(self.__class__.__name__)

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="controller_program",
            csockets=[self.PEER_NAME],
            epr_sockets=[self.PEER_NAME],
            max_qubits=2,
        )

    def run(self, context: ProgramContext):
        csocket = context.csockets[self.PEER_NAME]
        epr_socket = context.epr_sockets[self.PEER_NAME]
        connection = context.connection

        epr = epr_socket.recv_keep()[0]
        yield from connection.flush()
        self.logger.info("Created EPR pair")

        # Get the corrections
        msg = yield from csocket.recv_structured()
        assert isinstance(msg, StructuredMessage)
        m1, m2 = msg.payload.split(",")
        self.logger.info(f"Received corrections: {m1}, {m2}")
        if int(m2) == 1:
            self.logger.info("performing X correction")
            epr.X()
        if int(m1) == 1:
            self.logger.info("performing Z correction")
            epr.Z()

        yield from connection.flush()

        final_dm = get_qubit_state(epr, "Bob")

        return {"final_dm": final_dm}

