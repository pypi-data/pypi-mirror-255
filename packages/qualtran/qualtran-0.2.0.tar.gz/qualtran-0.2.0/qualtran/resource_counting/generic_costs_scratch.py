#  Copyright 2023 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import abc
import math
from collections import defaultdict
from typing import Dict, Generic, Iterable, List, Sequence, Set, Tuple, Type, TypeVar, Union

import attrs
import networkx as nx
from attrs import field, frozen

from qualtran import Bloq, DecomposeTypeError, Signature
from qualtran.resource_counting import (
    AddCostVal,
    BloqCount,
    BloqCountT,
    CLIFFORD_COST,
    CostKey,
    CostKV,
    CostVal,
    MaxCostVal,
    MaxQubits,
    MulCostVal,
    SuccessProb,
    SympySymbolAllocator,
)


@frozen
class CostingBloq(Bloq):
    name: str
    nq: int
    callees: Sequence[BloqCountT] = field(converter=tuple, factory=tuple)
    static_costs: Sequence[CostKV] = field(converter=tuple, factory=tuple)
    leaf_costs: Sequence[CostKV] | None = field(
        converter=lambda x: tuple(x) if x is not None else x, default=None
    )

    def signature(self) -> 'Signature':
        return Signature.build(register=self.nq)

    def build_call_graph(self, ssa: 'SympySymbolAllocator') -> Set['BloqCountT']:
        return set(self.callees)

    def my_static_costs(self) -> List[CostKV]:
        return [(MaxQubits(), MaxCostVal(self.nq))] + list(self.static_costs)

    def my_leaf_costs(self) -> List[CostKV]:
        if self.leaf_costs is None:
            return [(BloqCount(self), AddCostVal(1)), (MaxQubits(), MaxCostVal(self.nq))]
        return list(self.leaf_costs)

    def pretty_name(self):
        return self.name

    def __str__(self):
        return self.name


def make_example_1() -> Bloq:
    tgate = CostingBloq('TGate', nq=1)
    tof = CostingBloq(
        'Tof', nq=3, callees=[(tgate, 4)], static_costs=[(CLIFFORD_COST, AddCostVal(7))]
    )
    add = CostingBloq('Add', nq=8, callees=[(tof, 8)])
    comp = CostingBloq(
        'Compare', nq=9, callees=[(tof, 8)], static_costs=[(SuccessProb(), MulCostVal(0.9))]
    )
    modadd = CostingBloq('ModAdd', nq=8, callees=[(add, 1), (comp, 2)])
    return modadd


# def _add_cost(g, x: Bloq, val: List[CostKV]):
#     data = g.nodes[x]
#     if 'costs' in data:
#         data['costs'].extend(val)
#     else:
#         data['costs'] = val
#
#
# def is_leaf(bloq: SBloq):
#     # TODO
#     return False
#
#
# def _already_visited(g, caller: SBloq):
#     return caller in g.nodes
#
#
# def _constant_costs(g, caller: SBloq):
#     g.add_node(caller)
#     _add_cost(g, caller, val=caller.my_addtl_costs())
#
#
# def _recursive_costs(g, caller):
#     if is_leaf(caller):
#         # We can stop early and use `my_leaf_costs` instead.
#         raise DecomposeTypeError()
#
#     for callee, n in caller.my_callees():
#         _graphify(g, callee)
#         # important; do this after so we only visit each node once
#         g.add_edge(caller, callee, n=n)
#
#
# def _leaf_costs_instead(g, caller):
#     _add_cost(g, caller, val=caller.my_leaf_costs())
#
#
# def _graphify(g, caller: SBloq):
#     # "Factorized" costs. Totals need the graph structure and combination logic.
#
#     if _already_visited(g, caller):
#         return
#
#     _constant_costs(g, caller)
#
#     try:
#         _recursive_costs(g, caller)
#     except DecomposeTypeError:
#         _leaf_costs_instead(g, caller)
#
#
# def graphify(bloq: SBloq):
#     g = nx.DiGraph()
#     _graphify(g, caller=bloq)
#     return g


def annotate1(g):
    g.nodes['tof']['tofcount'] = 1
    g.nodes['t']['tcount'] = 1
    g.nodes['clifford']['clifcount'] = 1

    # e.g. add extra data
    g.nodes['mod_mul']['clifcount'] = 7
    return g


# def do_totals(g: nx.DiGraph):
#     totals: Dict[SBloq, Dict[CostKey, CostVal]] = {}
#
#     for caller in reversed(list(nx.topological_sort(g))):
#         vals: Dict[CostKey, CostVal] = {}
#         for callee in g.successors(caller):
#             n = g.edges[caller, callee]['n']
#             existing_vals = totals[callee]
#             for cost, costval in existing_vals.items():
#                 if cost not in vals:
#                     vals[cost] = cost.identity_val()
#                 vals[cost] += costval * n
#
#         # val = cost_type.identity_val()
#         for cost, costval in g.nodes[caller]['costs']:
#             if cost not in vals:
#                 vals[cost] = cost.identity_val()
#             vals[cost] += costval
#
#         totals[caller] = vals
#
#     return totals
