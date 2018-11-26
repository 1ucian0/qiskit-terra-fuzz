# -*- coding: utf-8 -*-

# Copyright 2018, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

"""
TODO
"""

from copy import copy

from qiskit.transpiler._basepasses import TransformationPass
from qiskit.dagcircuit import DAGCircuit
from qiskit.mapper import Layout

class SwapMapper(TransformationPass):
    """
    Maps a DAGCircuit onto a `coupling_map` using swap gates.
    """

    def __init__(self,
                 coupling_map,
                 swap_basis_element='swap',
                 swap_data=None,
                 initial_layout=None):
        """
        Maps a DAGCircuit onto a `coupling_map` using swap gates.
        Args:
            coupling_map (Coupling): Directed graph represented a coupling map.
            swap_basis_element (string):  Default: 'swap' the name of the gate
               that will be used for swaping.
            swap_data (dict): The swap "gate data". Default: the swap gate is opaque.
        """
        super().__init__()
        self.coupling_map = coupling_map
        self.initial_layout = initial_layout
        self.swap_basis_element = swap_basis_element
        self.swap_data = swap_data if swap_data is not None else {"opaque": True,
                                                                  "n_args": 0,
                                                                  "n_bits": 2,
                                                                  "args": [],
                                                                  "bits": ["a", "b"]}

    def run(self, dag):
        """
        Runs the SwapMapper pass on `dag`.
        Args:
            dag (DAGCircuit): DAG to map.

        Returns:
            DAGCircuit: A mapped DAG.
        """
        new_dag = DAGCircuit()

        if self.initial_layout is None:
            # create a one-to-one layout
            self.initial_layout = Layout()
            wire_no = 0
            for qreg in dag.qregs.values():
                for index in range(qreg.size):
                    self.initial_layout[(qreg.name, index)] = wire_no
                    wire_no += 1
        current_layout = copy(self.initial_layout)

        for layer in dag.serial_layers():
            subdag = layer['graph']

            cxs = subdag.get_cnot_nodes()
            if not cxs:
                # Trivial layer, there is no entanglement in this layer, just leave it like this.
                new_dag.add_dag_at_the_end(subdag, current_layout)
                continue
            for a_cx in subdag.get_cnot_nodes():
                physical_q0 = ('q', current_layout[a_cx['qargs'][0]])
                physical_q1 = ('q', current_layout[a_cx['qargs'][1]])
                if self.coupling_map.distance(physical_q0, physical_q1) != 1:
                    # Insert the SWAP when the CXs are not already together.
                    path = self.coupling_map.shortest_path(physical_q0, physical_q1)
                    closest_physical = path[1]['name'][1]
                    farthest_physical = path[-1]['name'][1]

                    new_dag.add_basis_element(self.swap_basis_element, 2)
                    new_dag.add_gate_data(self.swap_basis_element, self.swap_data)
                    new_dag.apply_operation_back(self.swap_basis_element,
                                                 [closest_physical,
                                                  farthest_physical])

                    current_layout.swap(closest_physical, farthest_physical)
                wire_map = current_layout.wire_map_from_layouts(self.initial_layout)
                new_dag.extends_at_the_end(subdag, wire_map)
        return new_dag
