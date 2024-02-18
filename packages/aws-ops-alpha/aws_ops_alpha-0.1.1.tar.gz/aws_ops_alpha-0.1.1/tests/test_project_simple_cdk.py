# -*- coding: utf-8 -*-

import aws_ops_alpha.project.simple_cdk.api as simple_cdk


def test():
    _ = simple_cdk.StepEnum
    _ = simple_cdk.SemanticBranchNameEnum
    _ = simple_cdk.RuntimeNameEnum
    _ = simple_cdk.EnvNameEnum
    _ = simple_cdk.truth_table
    _ = simple_cdk.semantic_branch_rule
    _ = simple_cdk.google_sheet_url
    _ = simple_cdk.cdk_deploy
    _ = simple_cdk.cdk_destroy


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.project.simple_cdk", preview=False)
