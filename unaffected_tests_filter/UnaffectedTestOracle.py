from dataclasses import dataclass, field
from typing import Set, Dict, Optional

from coverage import Coverage

from unaffected_tests_filter.UnaffectedTestOracleSavestate import (
    UnaffectedTestOracleSaveState,
    get_test_files_to_src_files,
    get_src_files_to_test_files,
)
from unaffected_tests_filter.file_hash import (
    get_src_file_checksums_and_deletions,
)
from unaffected_tests_filter.types import TestSrcPathStr, SrcPathStr


@dataclass
class UnaffectedTestOracle:
    prev_state: UnaffectedTestOracleSaveState
    failing_tests: Set[TestSrcPathStr] = field(default_factory=set)
    tests_ran_to_src_files: Dict[TestSrcPathStr, Set[SrcPathStr]] = field(
        default_factory=dict
    )
    current_cov: Optional[Coverage] = None

    __list_of_testfiles_to_ignore: Set[TestSrcPathStr] = field(default_factory=set)

    @staticmethod
    def load(save_path: str):
        prev_state = UnaffectedTestOracleSaveState.load(save_path)
        return UnaffectedTestOracle(prev_state=prev_state)

    def __post_init__(self):
        src_files = list(self.prev_state.src_files_to_test_files.keys())
        self.current_checksums = get_src_file_checksums_and_deletions(src_files)
        self.changed_files = set(
            [
                key
                for key, value in self.prev_state.file_checksums.items()
                if self.current_checksums.get(key, None) != value
            ]
        )
        print("CHANGED FILES: ", self.changed_files)
        new_tests_to_run = set()
        for changed_file in self.changed_files:
            new_tests_to_run.update(
                self.prev_state.src_files_to_test_files.get(changed_file, set())
            )

        print("self.prev_state.tests_to_run: ", self.prev_state.tests_to_run)
        print("new_tests_to_run: ", new_tests_to_run)
        self.tests_to_run: Set[TestSrcPathStr] = {
            *self.prev_state.tests_to_run,
            *new_tests_to_run,
        }
        self.__list_of_testfiles_to_ignore = self.get_list_of_testfiles_to_ignore()

    def get_list_of_testfiles_to_ignore(self):
        test_files_to_src_files = get_test_files_to_src_files(
            self.prev_state.src_files_to_test_files
        )
        to_ignore = set(test_files_to_src_files.keys())
        for f in self.changed_files:
            test_files_affected_by_change = self.prev_state.src_files_to_test_files.get(
                f, set()
            )
            to_ignore.difference_update(test_files_affected_by_change)
        return to_ignore

    def after_test_ran(
        self,
        test_src_path: TestSrcPathStr,
        related_src_paths: Set[SrcPathStr],
    ):
        src_files = self.tests_ran_to_src_files.get(test_src_path, {test_src_path})
        src_files.update(related_src_paths)
        self.tests_ran_to_src_files[test_src_path] = src_files

    def report_failing_test(
        self,
        test_src_path: TestSrcPathStr,
    ):
        self.failing_tests.add(test_src_path)

    def save(self, save_path: str):
        # 1. prev_state
        prev_test_files_to_src_files = get_test_files_to_src_files(
            self.prev_state.src_files_to_test_files
        )
        test_files_to_src_files = {
            **prev_test_files_to_src_files,
            **self.tests_ran_to_src_files,
        }

        src_files_to_test_files = get_src_files_to_test_files(
            test_files_to_src_files,
        )

        tests_ran = set(self.tests_ran_to_src_files.keys())
        # TODO: update test_failed:
        #   - remove failed-before-but-passed-now
        #       (test_path in self.
        failing_tests: Set[TestSrcPathStr] = {
            *(self.prev_state.failing_tests - set(tests_ran)),
            *self.failing_tests,
        }

        new_state = UnaffectedTestOracleSaveState(
            tests_to_run=self.tests_to_run - set(self.tests_ran_to_src_files.keys()),
            file_checksums=self.current_checksums,
            src_files_to_test_files=src_files_to_test_files,
            failing_tests=failing_tests,
        )
        new_state.save(save_path)
