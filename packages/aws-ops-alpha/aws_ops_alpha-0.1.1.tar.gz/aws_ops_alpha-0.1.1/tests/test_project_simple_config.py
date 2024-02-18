# -*- coding: utf-8 -*-

import aws_ops_alpha.project.simple_config.api as simple_config


def test():
    _ = simple_config.StepEnum
    _ = simple_config.SemanticBranchNameEnum
    _ = simple_config.RuntimeNameEnum
    _ = simple_config.EnvNameEnum
    _ = simple_config.truth_table
    _ = simple_config.semantic_branch_rule
    _ = simple_config.google_sheet_url
    _ = simple_config.deploy_config
    _ = simple_config.create_config_snapshot
    _ = simple_config.delete_config


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.project.simple_config", preview=False)
