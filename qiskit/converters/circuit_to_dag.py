# -*- coding: utf-8 -*-

# Copyright 2018, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

"""Helper function for converting a circuit to a dag"""


from qiskit.circuit.compositegate import CompositeGate
from qiskit.dagcircuit._dagcircuit import DAGCircuit


def circuit_to_dag(circuit):
    """Build a ``DAGCircuit`` object from a ``QuantumCircuit``.

    Args:
        circuit (QuantumCircuit): the input circuit.

    Return:
        DAGCircuit: the DAG representing the input circuit.
    """
    dagcircuit = DAGCircuit()
    dagcircuit.name = circuit.name
    for register in circuit.qregs:
        dagcircuit.add_qreg(register)
    for register in circuit.cregs:
        dagcircuit.add_creg(register)

    for main_instruction in circuit.data:
        # TODO: generate nodes for CompositeGates;
        # for now simply drop their instructions into the DAG
        instruction_list = []
        is_composite = isinstance(main_instruction, CompositeGate)
        if is_composite:
            instruction_list = main_instruction.instruction_list()
        else:
            instruction_list.append(main_instruction)

        for instruction, qargs, cargs in instruction_list:
            # Get arguments for classical control (if any)
            if instruction.control is None:
                control = None
            else:
                control = (instruction.control[0], instruction.control[1])

            def duplicate_instruction(instruction):
                """Create a fresh instruction from an input instruction."""
                args = instruction.params + [instruction.circuit]
                new_instruction = instruction.__class__(*args)
                return new_instruction

            instruction = duplicate_instruction(instruction)
            dagcircuit.apply_operation_back(instruction, qargs, cargs, control)

    return dagcircuit
