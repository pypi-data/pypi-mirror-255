# -*- coding: utf-8 -*-

import aws_ops_alpha.project.simple_lbd_agw_chalice.api as simple_lbd_agw_chalice


def test():
    _ = simple_lbd_agw_chalice.StepEnum
    _ = simple_lbd_agw_chalice.SemanticBranchNameEnum
    _ = simple_lbd_agw_chalice.RuntimeNameEnum
    _ = simple_lbd_agw_chalice.EnvNameEnum
    _ = simple_lbd_agw_chalice.truth_table
    _ = simple_lbd_agw_chalice.semantic_branch_rule
    _ = simple_lbd_agw_chalice.google_sheet_url
    _ = simple_lbd_agw_chalice.build_lambda_source_chalice_vendor
    _ = simple_lbd_agw_chalice.get_lock
    _ = simple_lbd_agw_chalice.download_deployed_json
    _ = simple_lbd_agw_chalice.upload_deployed_json
    _ = simple_lbd_agw_chalice.run_chalice_deploy
    _ = simple_lbd_agw_chalice.run_chalice_delete


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.project.simple_lbd_agw_chalice", preview=True)
