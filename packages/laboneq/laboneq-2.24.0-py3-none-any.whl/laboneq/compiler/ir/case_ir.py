# Copyright 2022 Zurich Instruments AG
# SPDX-License-Identifier: Apache-2.0

from typing import Dict, Iterator, List

from attrs import asdict, define

from laboneq.compiler import CompilerSettings
from laboneq.compiler.common.event_type import EventType
from laboneq.compiler.common.play_wave_type import PlayWaveType
from laboneq.compiler.ir.section_ir import SectionIR


@define(kw_only=True, slots=True)
class CaseIR(SectionIR):
    state: int

    def generate_event_list(
        self,
        start: int,
        max_events: int,
        id_tracker: Iterator[int],
        expand_loops,
        settings: CompilerSettings,
    ) -> List[Dict]:
        assert self.length is not None

        events = super().generate_event_list(
            start, max_events, id_tracker, expand_loops, settings
        )
        for e in events:
            e["state"] = self.state
        return events

    @classmethod
    def from_section_ir(cls, schedule: SectionIR, state: int):
        """Down-cast from SectionIR."""
        return cls(**asdict(schedule, recurse=False), state=state)


class EmptyBranchIR(CaseIR):
    def generate_event_list(
        self,
        start: int,
        max_events: int,
        id_tracker: Iterator[int],
        expand_loops,
        settings: CompilerSettings,
    ) -> List[Dict]:
        section_start, *rest, section_end = super().generate_event_list(
            start, max_events, id_tracker, expand_loops, settings
        )
        assert self.length is not None
        assert len(rest) == 0
        assert section_start["event_type"] == EventType.SECTION_START
        assert section_end["event_type"] == EventType.SECTION_END
        if max_events <= 2:
            return [section_start, section_end]

        d = {
            "section_name": self.section,
            "play_wave_id": "EMPTY_MATCH_CASE_DELAY",
            "play_wave_type": PlayWaveType.EMPTY_CASE.name,
        }

        delay_events = []
        for signal in self.signals:
            if max_events <= 2:
                break
            max_events -= 2
            start_id = next(id_tracker)
            delay_events.extend(
                [
                    {
                        "event_type": EventType.DELAY_START,
                        "time": start,
                        "id": start_id,
                        "signal": signal,
                        "chain_element_id": start_id,
                        **d,
                    },
                    {
                        "event_type": EventType.DELAY_END,
                        "time": start + self.length,
                        "id": next(id_tracker),
                        "signal": signal,
                        "chain_element_id": start_id,
                        **d,
                    },
                ]
            )

        return [section_start, *delay_events, section_end]
