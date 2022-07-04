# -*- coding: utf-8 -*-
import pytest
from _pytest.config import ExitCode


def test_all_passing_scenario(pytester: pytest.Pytester):
    pytester.makepyfile(
        hello1="""
        def hello1():
            print("hello1")
        """
    )

    pytester.makepyfile(
        hello2="""
        from hello1 import hello1
        def hello2():
            hello1()
            raise Exception("!")
            print("hello2")
        """
    )

    pytester.makepyfile(
        hello3="""
        from hello1 import hello1
        def hello3():
            hello1()
            print("Hello3")
        """
    )
    called_test_hello2 = "print('called: test_hello2.py')"
    pytester.makepyfile(
        test_hello2=f"""
        from hello2 import hello2
        def test_hello2():
            {called_test_hello2}
            hello2()
        """
    )

    called_test_hello3 = "print('called: test_hello3.py')"
    pytester.makepyfile(
        test_hello3=f"""
            from hello3 import hello3
            def test_hello3():
                {called_test_hello3}
                hello3()
            """
    )

    result_with_skip1 = pytester.runpytest('--skip-unchanged-tests', '--skip-unchanged-tests-debug')
    result_with_skip1.stdout.no_fnmatch_line('collect_ignore: *test_*.py*')
    result_with_skip1.stdout.fnmatch_lines(['collected 2 items'])
    result_with_skip2 = pytester.runpytest('--skip-unchanged-tests', '--skip-unchanged-tests-debug')
    result_with_skip2.stdout.fnmatch_lines(['collected 1 item'])

    result_with_ignore_fail = pytester.runpytest('--skip-unchanged-tests', '--skip-previously-failed-tests')
    result_with_ignore_fail.stdout.fnmatch_lines(['collected 0 items'])

    pytester.makepyfile(
        hello2="""
        from hello1 import hello1
        def hello2():
            hello1()
            print("hello2")
        """
    )

    result_with_hello2_fixed = pytester.runpytest('--skip-unchanged-tests', '--skip-unchanged-tests-debug')
    result_with_hello2_fixed.stdout.fnmatch_lines(['collected 1 item'])

    result_with_hello2_fixed2 = pytester.runpytest('--skip-unchanged-tests', '--skip-unchanged-tests-debug')
    result_with_hello2_fixed2.stdout.fnmatch_lines(['collected 0 items'])

