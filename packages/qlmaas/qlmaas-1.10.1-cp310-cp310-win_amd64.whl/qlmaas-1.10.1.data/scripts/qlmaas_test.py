#!python
# -*- coding: utf-8 -*-

"""
@authors    Cyprien Lambert <cyprien.lambert@atos.net>
@copyright  2020 Bull S.A.S. - All rights reserved
            This is not Free or Open Source software.
            Please contact Bull SAS for details about its license.
            Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois
"""

from qat.lang.AQASM import Program, H, CNOT
from qat.qlmaas.commands import build_connection


def connection_test(connection):
    """
    Checks if a connection is working by submitting a Bell pair
    circuit to a remote LinAlg QPU

    .. note::

        This function does not return any result. If the test failed,
        an exception is raised

    Args:
        connection (:class:`~qat.qlmaas.QLMaaSConnection`): connection to
            check
    """
    # create a simple job
    program = Program()
    qbits = program.qalloc(2)
    program.apply(H, qbits[0])
    program.apply(CNOT, qbits)
    job = program.to_circ().to_job()

    # create remote QPU
    QPU = connection.get_qpu("qat.qpus:LinAlg")  # pylint: disable=invalid-name
    qpu = QPU()
    print("Remote QPU successfully created")

    # submit the job
    async_result = qpu.submit(job)
    print("Bell pair circuit successfully submitted to the remote QPU")

    # get the result
    result = async_result.join()
    print("Result downloaded:")

    for sample in result:
        print(f' -> {sample.state} - {sample.probability}')

    assert result, "The result seems to be empty"
    print("Test successful")


if __name__ == "__main__":
    connection_test(
        build_connection(prog="qlmaas_test",
                         description="Checks if the connection to a QLMaaS server is working")
    )
