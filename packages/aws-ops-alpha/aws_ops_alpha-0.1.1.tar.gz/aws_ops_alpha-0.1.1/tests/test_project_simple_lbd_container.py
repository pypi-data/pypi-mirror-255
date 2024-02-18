# -*- coding: utf-8 -*-

import aws_ops_alpha.project.simple_lbd_container.api as simple_lbd_container


def test():
    _ = simple_lbd_container.StepEnum
    _ = simple_lbd_container.SemanticBranchNameEnum
    _ = simple_lbd_container.RuntimeNameEnum
    _ = simple_lbd_container.EnvNameEnum
    _ = simple_lbd_container.truth_table
    _ = simple_lbd_container.semantic_branch_rule
    _ = simple_lbd_container.google_sheet_url
    _ = simple_lbd_container.create_ecr_repository
    _ = simple_lbd_container.build_lambda_container
    _ = simple_lbd_container.push_lambda_container


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.project.simple_lbd_container", preview=True)
