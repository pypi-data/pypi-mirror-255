# -*- coding: utf-8 -*-

import aws_ops_alpha.project.simple_lambda.api as simple_lambda


def test():
    _ = simple_lambda.StepEnum
    _ = simple_lambda.SemanticBranchNameEnum
    _ = simple_lambda.RuntimeNameEnum
    _ = simple_lambda.EnvNameEnum
    _ = simple_lambda.truth_table
    _ = simple_lambda.semantic_branch_rule
    _ = simple_lambda.google_sheet_url
    _ = simple_lambda.build_lambda_source
    _ = simple_lambda.publish_lambda_layer
    _ = simple_lambda.publish_lambda_version
    _ = simple_lambda.deploy_app
    _ = simple_lambda.delete_app
    _ = simple_lambda.run_int_test


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.project.simple_lambda", preview=False)
