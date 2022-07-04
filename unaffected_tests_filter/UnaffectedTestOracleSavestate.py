from __future__ import annotations

import json
import os
from typing import Set, Dict

from pydantic.dataclasses import dataclass
from pydantic.json import pydantic_encoder

from unaffected_tests_filter.types import TestSrcPathStr, SrcPathStr, ChecksumStr


def get_test_files_to_src_files(
    src_files_to_test_file: Dict[SrcPathStr, Set[TestSrcPathStr]]
):
    to_return: Dict[TestSrcPathStr, Set[SrcPathStr]] = {}
    for src_path, test_src_paths in src_files_to_test_file.items():
        for test_src_path in test_src_paths:
            prev_value = to_return.get(test_src_path, set())
            prev_value.add(src_path)
            to_return[test_src_path] = prev_value
    return to_return


def get_src_files_to_test_files(
    test_files_to_src_files: Dict[TestSrcPathStr, Set[SrcPathStr]]
):
    to_return: Dict[SrcPathStr, Set[TestSrcPathStr]] = {}
    for test_src_path, src_paths in test_files_to_src_files.items():
        for src_path in src_paths:
            prev_value = to_return.get(src_path, set())
            prev_value.add(test_src_path)
            to_return[src_path] = prev_value
    return to_return


@dataclass
class UnaffectedTestOracleSaveState:
    tests_to_run: Set[TestSrcPathStr]
    file_checksums: Dict[SrcPathStr, ChecksumStr]
    src_files_to_test_files: Dict[SrcPathStr, Set[TestSrcPathStr]]
    failing_tests: Set[TestSrcPathStr]

    def save(self, save_path: str):
        to_save = json.dumps(
            self, ensure_ascii=False, indent=2, default=pydantic_encoder
        )
        with open(save_path, "w") as f:
            f.write(to_save)

    @staticmethod
    def load(save_path: str) -> UnaffectedTestOracleSaveState:
        if not os.path.isfile(save_path):
            return UnaffectedTestOracleSaveState(
                tests_to_run=set(),
                file_checksums=dict(),
                src_files_to_test_files=dict(),
                failing_tests=set(),
            )
        with open(save_path, "r") as f:
            contents = f.read()
            return UnaffectedTestOracleSaveState.__pydantic_model__.parse_raw(contents)
