# Copyright 2022 Zurich Instruments AG
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Dict, Iterator, List

from attrs import define

from laboneq.compiler.common.compiler_settings import CompilerSettings
from laboneq.compiler.common.event_type import EventType
from laboneq.compiler.ir.loop_iteration_ir import LoopIterationIR
from laboneq.compiler.ir.section_ir import SectionIR


@define(kw_only=True, slots=True)
class LoopIR(SectionIR):
    compressed: bool
    iterations: int

    def generate_event_list(
        self,
        start: int,
        max_events: int,
        id_tracker: Iterator[int],
        expand_loops,
        settings: CompilerSettings,
    ) -> List[Dict]:
        assert self.children_start is not None
        assert self.length is not None

        # We'll later wrap the child events in some extra events, see below.
        max_events -= 3

        if not self.compressed:  # unrolled loop
            children_events = self.children_events(
                start,
                max_events,
                settings,
                id_tracker,
                expand_loops,
                subsection_events=False,
            )
        else:
            children_events = [
                self.children[0].generate_event_list(
                    start + self.children_start[0],
                    max_events,
                    id_tracker,
                    expand_loops,
                    settings,
                )
            ]
            iteration_event = children_events[0][-1]
            assert iteration_event["event_type"] == EventType.LOOP_ITERATION_END
            iteration_event["compressed"] = True
            if expand_loops:
                prototype = self.children[0]
                assert prototype.length is not None
                assert isinstance(prototype, LoopIterationIR)
                iteration_start = start
                for iteration in range(1, self.iterations):
                    max_events -= len(children_events[-1])
                    if max_events <= 0:
                        break
                    iteration_start += prototype.length
                    shadow_iteration = prototype.compressed_iteration(iteration)
                    children_events.append(
                        shadow_iteration.generate_event_list(
                            iteration_start,
                            max_events,
                            id_tracker,
                            expand_loops,
                            settings,
                        )
                    )

        for child_list in children_events:
            for e in child_list:
                if "nesting_level" in e:
                    # todo: pass the current level as an argument, rather than
                    #  incrementing after the fact
                    e["nesting_level"] += 1

        start_id = next(id_tracker)
        d = {
            "section_name": self.section,
            "nesting_level": 0,
            "chain_element_id": start_id,
        }
        return [
            {"event_type": EventType.SECTION_START, "time": start, "id": start_id, **d},
            {
                "event_type": EventType.LOOP_START,
                "time": start,
                "iterations": self.iterations,
                "compressed": self.compressed,
                **d,
            },
            *[e for l in children_events for e in l],
            {"event_type": EventType.LOOP_END, "time": start + self.length, **d},
            {"event_type": EventType.SECTION_END, "time": start + self.length, **d},
        ]

    def __hash__(self):
        return super().__hash__()
