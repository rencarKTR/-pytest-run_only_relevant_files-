# -*- coding: utf-8 -*-

from __future__ import annotations

import json
from os import path
from typing import Optional, Set, cast

import pytest
from _pytest.config import Config
from _pytest.nodes import Item
from _pytest.runner import CallInfo
from coverage import Coverage, CoverageData

from unaffected_tests_filter.UnaffectedTestOracle import UnaffectedTestOracle
from unaffected_tests_filter.types import TestSrcPathStr, SrcPathStr

save_path_file_name = "__unaffected_tests_oracle.tmp.json"
test_oracle_save_path: Optional[str] = None
unaffected_tests_oracle: Optional[UnaffectedTestOracle] = None

collect_ignore = []
collect_ignore_set: Set[str] = set()

OPTION_SKIP_UNCHANGED_TESTS = "skipunchangedtests"
OPTION_SKIP_UNCHANGED_TESTS_DEBUG = "skipunchangedtests_debug"


def pytest_addoption(parser):
    group = parser.getgroup(OPTION_SKIP_UNCHANGED_TESTS)
    group.addoption(
        "--skip-unchanged-tests",
        action="store_true",
        dest=OPTION_SKIP_UNCHANGED_TESTS,
        default=False,
        help="skip unchanged tests",
    )

    group = parser.getgroup(OPTION_SKIP_UNCHANGED_TESTS_DEBUG)
    group.addoption(
        "--skip-unchanged-tests-debug",
        action="store_true",
        dest=OPTION_SKIP_UNCHANGED_TESTS_DEBUG,
        default=False,
        help="DEBUG FLAG for --skip-unchanged-tests (shows which tests are skipped, etc)",
    )


def pytest_ignore_collect(collection_path, path, config):
    if not config.getoption(OPTION_SKIP_UNCHANGED_TESTS):
        return False
    global collect_ignore_set
    return str(path) in collect_ignore_set


def pytest_cmdline_main(config):
    if not config.getoption(OPTION_SKIP_UNCHANGED_TESTS):
        return
    global unaffected_tests_oracle
    global collect_ignore
    global collect_ignore_set
    global test_oracle_save_path
    test_oracle_save_path = path.join(config._rootpath, '__unaffected_tests_oracle.tmp.json')

    unaffected_tests_oracle = UnaffectedTestOracle.load(test_oracle_save_path)
    collect_ignore_set = unaffected_tests_oracle.get_list_of_testfiles_to_ignore()
    if config.getoption(OPTION_SKIP_UNCHANGED_TESTS_DEBUG):
        print("collect_ignore: ", collect_ignore_set)
        print(
            "prev_state.file_checksums: ",
            json.dumps(unaffected_tests_oracle.prev_state.file_checksums),
        )


def pytest_unconfigure(config: Config):
    global unaffected_tests_oracle
    global test_oracle_save_path
    if unaffected_tests_oracle is None:
        return
    unaffected_tests_oracle.save(test_oracle_save_path)


def pytest_runtest_setup(item: Item):
    global unaffected_tests_oracle
    if unaffected_tests_oracle is None:
        return
    unaffected_tests_oracle.current_cov = Coverage()
    unaffected_tests_oracle.current_cov.start()


def pytest_runtest_teardown(item: Item, nextitem: Optional[Item]):
    global unaffected_tests_oracle
    if unaffected_tests_oracle is None or unaffected_tests_oracle.current_cov is None:
        return
    unaffected_tests_oracle.current_cov.stop()
    data: CoverageData = unaffected_tests_oracle.current_cov.get_data()
    measured_files = cast(Set[SrcPathStr], data.measured_files())
    test_src_path = TestSrcPathStr(str(item.fspath))

    unaffected_tests_oracle.after_test_ran(
        test_src_path=test_src_path,
        related_src_paths=measured_files,
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: CallInfo[None]):
    global unaffected_tests_oracle
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed and unaffected_tests_oracle is not None:
        unaffected_tests_oracle.report_failing_test(TestSrcPathStr(str(item.fspath)))
    return rep
