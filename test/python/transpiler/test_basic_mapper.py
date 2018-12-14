# -*- coding: utf-8 -*-

# Copyright 2018, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

"""Test the Basic Mapper pass"""

import unittest
from qiskit.transpiler.passes import BasicMapper
from qiskit.mapper import Coupling
from qiskit.converters import circuit_to_dag
from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister
from ..common import QiskitTestCase


class TestBasicMapper(QiskitTestCase):
    """ Tests the BasicMapper pass."""

    def test_trivial_case(self):
        """No need to have any swap, the CX are distance 1 to each other
         q0:--(+)-[U]-(+)-
               |       |
         q1:---.-------|--
                       |
         q2:-----------.--

         Coupling map: [1]--[0]--[2]
        """
        coupling = Coupling({0: [1, 2]})

        qr = QuantumRegister(3, 'q')
        circuit = QuantumCircuit(qr)
        circuit.cx(qr[0], qr[1])
        circuit.h(qr[0])
        circuit.cx(qr[0], qr[2])

        dag = circuit_to_dag(circuit)
        pass_ = BasicMapper(coupling)
        after = pass_.run(dag)

        self.assertEqual(dag, after)

    def test_trivial_in_same_layer(self):
        """ No need to have any swap, two CXs distance 1 to each other, in the same layer
         q0:--(+)--
               |
         q1:---.---

         q2:--(+)--
               |
         q3:---.---

         Coupling map: [0]--[1]--[2]--[3]
        """
        coupling = Coupling({0: [1], 1: [2], 2: [3]})

        qr = QuantumRegister(4, 'q')
        circuit = QuantumCircuit(qr)
        circuit.cx(qr[2], qr[3])
        circuit.cx(qr[0], qr[1])

        dag = circuit_to_dag(circuit)
        pass_ = BasicMapper(coupling)
        after = pass_.run(dag)

        self.assertEqual(dag, after)

    def test_a_single_swap(self):
        """ Adding a swap
         q0:-------

         q1:--(+)--
               |
         q2:---.---

         Coupling map: [1]--[0]--[2]

         q0:--X---.---
              |   |
         q1:--X---|---
                  |
         q2:-----(+)--

        """
        coupling = Coupling({0: [1, 2]})

        qr = QuantumRegister(3, 'q')
        circuit = QuantumCircuit(qr)
        circuit.cx(qr[1], qr[2])
        dag = circuit_to_dag(circuit)

        expected = QuantumCircuit(qr)
        expected.swap(qr[1], qr[0])
        expected.cx(qr[0], qr[2])

        pass_ = BasicMapper(coupling)
        after = pass_.run(dag)

        self.assertEqual(circuit_to_dag(expected), after)

    def test_keep_layout(self):
        """After a swap, the following gates also change the wires.
         qr0:---.---[H]--
                |
         qr1:---|--------
                |
         qr2:--(+)-------

         Coupling map: [0]--[1]--[2]

         qr0:--X-----------
               |
         qr1:--X---.--[H]--
                   |
         qr2:-----(+)------
        """
        coupling = Coupling({1: [0, 2]})

        qr = QuantumRegister(3, 'q')
        circuit = QuantumCircuit(qr)
        circuit.cx(qr[0], qr[2])
        circuit.h(qr[0])
        dag = circuit_to_dag(circuit)

        expected = QuantumCircuit(qr)
        expected.swap(qr[0], qr[1])
        expected.cx(qr[1], qr[2])
        expected.h(qr[1])

        pass_ = BasicMapper(coupling)
        after = pass_.run(dag)

        self.assertEqual(circuit_to_dag(expected), after)

    def test_far_swap(self):
        """ A far swap that affects coming CXs.
         qr0:--(+)---.--
                |    |
         qr1:---|----|--
                |    |
         qr2:---|----|--
                |    |
         qr3:---.---(+)-

         Coupling map: [0]--[1]--[2]--[3]

         qr0:--X--------------
               |
         qr1:--X--X-----------
                  |
         qr2:-----X--(+)---.--
                      |    |
         qr3:---------.---(+)-

        """
        coupling = Coupling({0: [1], 1: [2], 2: [3]})

        qr = QuantumRegister(4, 'q')
        circuit = QuantumCircuit(qr)
        circuit.cx(qr[0], qr[3])
        circuit.cx(qr[3], qr[0])
        dag = circuit_to_dag(circuit)

        expected = QuantumCircuit(qr)
        expected.swap(qr[0], qr[1])
        expected.swap(qr[1], qr[2])
        expected.cx(qr[2], qr[3])
        expected.cx(qr[3], qr[2])

        pass_ = BasicMapper(coupling)
        after = pass_.run(dag)

        self.assertEqual(circuit_to_dag(expected), after)

    def test_far_swap_with_gate_the_front(self):
        """ A far swap with a gate in the front.
         qr0:------(+)--
                    |
         qr1:-------|---
                    |
         qr2:-------|---
                    |
         qr3:--[H]--.---

         Coupling map: [0]--[1]--[2]--[3]

         qr0:-----------(+)--
                         |
         qr1:---------X--.---
                      |
         qr2:------X--X------
                   |
         qr3:-[H]--X---------

        """
        coupling = Coupling({0: [1], 1: [2], 2: [3]})

        qr = QuantumRegister(4, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.h(qr[3])
        circuit.cx(qr[3], qr[0])
        dag = circuit_to_dag(circuit)

        expected = QuantumCircuit(qr)
        expected.h(qr[3])
        expected.swap(qr[3], qr[2])
        expected.swap(qr[2], qr[1])
        expected.cx(qr[1], qr[0])

        pass_ = BasicMapper(coupling)
        after = pass_.run(dag)

        self.assertEqual(circuit_to_dag(expected), after)

    def test_far_swap_with_gate_the_back(self):
        """ A far swap with a gate in the back.
         qr0:--(+)------
                |
         qr1:---|-------
                |
         qr2:---|-------
                |
         qr3:---.--[H]--

         Coupling map: [0]--[1]--[2]--[3]

         qr0:-------(+)------
                     |
         qr1:-----X--.--[H]--
                  |
         qr2:--X--X----------
               |
         qr3:--X-------------

        """
        coupling = Coupling({0: [1], 1: [2], 2: [3]})

        qr = QuantumRegister(4, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.cx(qr[3], qr[0])
        circuit.h(qr[3])
        dag = circuit_to_dag(circuit)

        expected = QuantumCircuit(qr)
        expected.swap(qr[3], qr[2])
        expected.swap(qr[2], qr[1])
        expected.cx(qr[1], qr[0])
        expected.h(qr[1])

        pass_ = BasicMapper(coupling)
        after = pass_.run(dag)

        self.assertEqual(circuit_to_dag(expected), after)

    def test_far_swap_with_gate_the_middle(self):
        """ A far swap with a gate in the middle.
         qr0:--(+)-------.--
                |        |
         qr1:---|--------|--
                |
         qr2:---|--------|--
                |        |
         qr3:---.--[H]--(+)-

         Coupling map: [0]--[1]--[2]--[3]

         qr0:-------(+)-------.---
                     |        |
         qr1:-----X--.--[H]--(+)--
                  |
         qr2:--X--X---------------
               |
         qr3:--X------------------

        """
        coupling = Coupling({0: [1], 1: [2], 2: [3]})

        qr = QuantumRegister(4, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.cx(qr[3], qr[0])
        circuit.h(qr[3])
        circuit.cx(qr[0], qr[3])
        dag = circuit_to_dag(circuit)

        expected = QuantumCircuit(qr)
        expected.swap(qr[3], qr[2])
        expected.swap(qr[2], qr[1])
        expected.cx(qr[1], qr[0])
        expected.h(qr[1])
        expected.cx(qr[0], qr[1])

        pass_ = BasicMapper(coupling)
        after = pass_.run(dag)

        self.assertEqual(circuit_to_dag(expected), after)

    def test_swap_between_qregs(self):
        """ Adding a swap affecting different qregs
        virtual  physical
         qr0_0:    [0] -------

         qr1_0:    [1] --(+)--
                          |
         qr1_1:    [2] ---.---

         Coupling map: [1]--[0]--[2]

        virtual  physical
         qr0_0:    [0] --X-(+)--
                         |  |
         qr1_0:    [1] --X--|---
                            |
         qr1_1:    [2] -----.---

        """
        coupling = Coupling({0: [1, 2]})

        qr0 = QuantumRegister(1, 'qr0')
        qr1 = QuantumRegister(2, 'qr1')

        circuit = QuantumCircuit(qr0, qr1)
        circuit.cx(qr1[0], qr1[1])
        dag = circuit_to_dag(circuit)

        expected = QuantumCircuit(qr0, qr1)
        expected.swap(qr1[0], qr0[0])
        expected.cx(qr0[0], qr1[1])

        pass_ = BasicMapper(coupling)
        after = pass_.run(dag)

        self.assertEqual(circuit_to_dag(expected), after)

    def test_swap_handle_measures(self):
        """ Adding a swap affecting different qregs
         q_0: --.-----(+)-m-------
                |      |  |
         q_1: -(+)-(+)-|--|-m-----
                    |  |  | |
         q_2: ------|--|--|-|-m---
                    |  |  | | |
         q_3: -[H]--.--.--|-|-|-m-
                          | | | |
         c_0: ------------.-|-|-|-
         c_1: --------------.-|-|-
         c_2: ----------------.-|-
         c_3: ------------------.-

         Coupling map: [0]--[1]--[2]--[3]

         q_0: --.--------(+)-m-----
                |         |  |
         q_1: -(+)--(+)-X-.--|---m-
                     |  |    |   |
         q_2: -----X-.--X----|-m-|-
                   |         | | |
         q_3: -[H]-X----m----|-|-|-
                        |    | | |
         c_0: ----------|----.-|-|-
         c_1: ----------|------.-|-
         c_2: ----------.--------|-
         c_3: -------------------.-
        """

        coupling = Coupling(couplinglist=[[0, 1], [1, 2], [2, 3]])
        qr = QuantumRegister(4, 'q')
        cr = ClassicalRegister(4, 'c')
        circuit = QuantumCircuit(qr, cr)
        circuit.h(qr[3])
        circuit.cx(qr[0], qr[1])
        circuit.cx(qr[3], qr[1])
        circuit.cx(qr[3], qr[0])
        circuit.measure(qr, cr)

        dag = circuit_to_dag(circuit)

        expected = QuantumCircuit(qr, cr)
        expected.cx(qr[0], qr[1])
        expected.h(qr[3])
        expected.swap(qr[3], qr[2])
        expected.cx(qr[2], qr[1])
        expected.measure(qr[3], cr[2])
        expected.swap(qr[2], qr[1])
        expected.cx(qr[1], qr[0])
        expected.measure(qr[0], cr[0])
        expected.measure(qr[2], cr[1])
        expected.measure(qr[1], cr[3])

        pass_ = BasicMapper(coupling)
        after = pass_.run(dag)

        self.assertEqual(circuit_to_dag(expected), after)


if __name__ == '__main__':
    unittest.main()
