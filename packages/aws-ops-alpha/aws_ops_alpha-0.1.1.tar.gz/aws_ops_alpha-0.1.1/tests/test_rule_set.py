# -*- coding: utf-8 -*-

import tt4human.api as tt4human
from aws_ops_alpha.logger import logger
from aws_ops_alpha.rule_set import ConditionEnum, SHOULD_WE_DO_IT, should_we_do_it


def test_should_we_do_it():
    tt = tt4human.TruthTable(
        headers=[
            ConditionEnum.step.value,
            ConditionEnum.semantic_branch_name.value,
            ConditionEnum.runtime_name.value,
            ConditionEnum.env_name.value,
            SHOULD_WE_DO_IT,
        ],
        rows=[
            ["run unit test", "main", "local", "sbx", True],
            ["run unit test", "main", "local", "prd", True],
            ["run unit test", "release", "local", "sbx", True],
            ["run unit test", "release", "local", "prd", True],
            ["deploy", "main", "local", "sbx", True],
            ["deploy", "main", "local", "prd", False],
            ["deploy", "release", "local", "sbx", True],
            ["deploy", "release", "local", "prd", True],
        ],
    )
    assert (
        should_we_do_it(
            step="run unit test",
            semantic_branch_name="main",
            runtime_name="local",
            env_name="sbx",
            truth_table=tt,
        )
        is True
    )

    with logger.disabled(
        disable=True, # no log
        # disable=False,  # show log
    ):
        logger.info("")
        should_we_do_it(
            step="deploy",
            semantic_branch_name="main",
            runtime_name="local",
            env_name="prd",
            truth_table=tt,
            google_sheet_url="https://www.example.com",
        )


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.rule_set", preview=False)
