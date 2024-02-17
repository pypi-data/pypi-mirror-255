# Copyright 2019-2024 Cambridge Quantum Computing
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from typing import (
    List,
    Iterator,
    Sequence,
    Set,
    Tuple,
    Optional,
    Dict,
    Any,
)
from collections import Counter, defaultdict

import numpy as np

from qiskit.result import Result  # type: ignore
from qiskit.result.models import ExperimentResult  # type: ignore

from pytket.circuit import Bit, Qubit, UnitID, Circuit

from pytket.backends.backendresult import BackendResult
from pytket.utils.outcomearray import OutcomeArray


def _get_registers_from_uids(uids: List[UnitID]) -> Dict[str, Set[UnitID]]:
    registers: Dict[str, Set[UnitID]] = defaultdict(set)
    for uid in uids:
        registers[uid.reg_name].add(uid)
    return registers


LabelsType = List[Tuple[str, int]]


def _get_header_info(uids: List[UnitID]) -> Tuple[LabelsType, LabelsType]:
    registers = _get_registers_from_uids(uids)
    reg_sizes = [(name, max(uids).index[0] + 1) for name, uids in registers.items()]
    reg_labels = [
        (name, uid.index[0]) for name, indices in registers.items() for uid in uids
    ]

    return reg_sizes, reg_labels


def _qiskit_ordered_uids(uids: List[UnitID]) -> List[UnitID]:
    registers = _get_registers_from_uids(uids)
    names = sorted(registers.keys())
    return [uid for name in names for uid in sorted(registers[name], reverse=True)]


def _hex_to_outar(hexes: Sequence[str], width: int) -> OutcomeArray:
    ints = [int(hexst, 16) for hexst in hexes]
    return OutcomeArray.from_ints(ints, width, big_endian=False)


# An empty ExperimentResult can be an empty dict, but it can also be a dict
# filled with empty values.
def _result_is_empty_shots(result: ExperimentResult) -> bool:
    if not result.shots > 0:
        # 0-shots results don't count as empty; they are simply ignored
        return False

    datadict = result.data.to_dict()
    if len(datadict) == 0:
        return True
    elif "memory" in datadict and len(datadict["memory"]) == 0:
        return True
    elif "counts" in datadict and len(datadict["counts"]) == 0:
        return True
    else:
        return False


def qiskit_experimentresult_to_backendresult(
    result: ExperimentResult,
    ppcirc: Optional[Circuit] = None,
) -> BackendResult:
    if not result.success:
        raise RuntimeError(result.status)

    header = result.header
    width = header.memory_slots

    c_bits, q_bits = None, None
    if hasattr(header, "creg_sizes"):
        c_bits = []
        for name, size in header.creg_sizes:
            for index in range(size):
                c_bits.append(Bit(name, index))
    if hasattr(header, "qreg_sizes"):
        q_bits = []
        for name, size in header.qreg_sizes:
            for index in range(size):
                q_bits.append(Qubit(name, index))

    shots, counts, state, unitary = (None,) * 4
    datadict = result.data.to_dict()
    if _result_is_empty_shots(result):
        n_bits = len(c_bits) if c_bits else 0
        shots = OutcomeArray.from_readouts(
            np.zeros((result.shots, n_bits), dtype=np.uint8)
        )
    else:
        if "memory" in datadict:
            memory = datadict["memory"]
            shots = _hex_to_outar(memory, width)
        elif "counts" in datadict:
            qis_counts = datadict["counts"]
            counts = Counter(
                dict(
                    (_hex_to_outar([hexst], width), count)
                    for hexst, count in qis_counts.items()
                )
            )

        if "statevector" in datadict:
            state = datadict["statevector"].reverse_qargs().data

        if "unitary" in datadict:
            unitary = datadict["unitary"].reverse_qargs().data

    return BackendResult(
        c_bits=c_bits,
        q_bits=q_bits,
        shots=shots,
        counts=counts,
        state=state,
        unitary=unitary,
        ppcirc=ppcirc,
    )


def qiskit_result_to_backendresult(res: Result) -> Iterator[BackendResult]:
    for result in res.results:
        yield qiskit_experimentresult_to_backendresult(result)


def backendresult_to_qiskit_resultdata(
    res: BackendResult,
    cbits: List[UnitID],
    qbits: List[UnitID],
    final_map: Optional[Dict[UnitID, UnitID]],
) -> Dict[str, Any]:
    data: Dict[str, Any] = dict()
    if res.contains_state_results:
        qbits = _qiskit_ordered_uids(qbits)
        qbits.sort(reverse=True)
        if final_map:
            qbits = [final_map[q] for q in qbits]
        stored_res = res.get_result(qbits)
        if stored_res.state is not None:
            data["statevector"] = stored_res.state
        if stored_res.unitary is not None:
            data["unitary"] = stored_res.unitary
    if res.contains_measured_results:
        cbits = _qiskit_ordered_uids(cbits)
        if final_map:
            cbits = [final_map[c] for c in cbits]
        stored_res = res.get_result(cbits)
        if stored_res.shots is not None:
            data["memory"] = [hex(i) for i in stored_res.shots.to_intlist()]
            data["counts"] = dict(Counter(data["memory"]))
        elif stored_res.counts is not None:
            data["counts"] = {
                hex(i.to_intlist()[0]): f for i, f in stored_res.counts.items()
            }
    return data
