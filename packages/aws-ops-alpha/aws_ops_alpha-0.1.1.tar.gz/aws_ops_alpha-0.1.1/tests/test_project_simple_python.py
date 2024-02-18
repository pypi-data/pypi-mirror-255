# -*- coding: utf-8 -*-

import aws_ops_alpha.project.simple_python.api as simple_python


def test():
    _ = simple_python.StepEnum
    _ = simple_python.SemanticBranchNameEnum
    _ = simple_python.RuntimeNameEnum
    _ = simple_python.EnvNameEnum
    _ = simple_python.truth_table
    _ = simple_python.semantic_branch_rule
    _ = simple_python.google_sheet_url
    _ = simple_python.pip_install
    _ = simple_python.pip_install_dev
    _ = simple_python.pip_install_test
    _ = simple_python.pip_install_doc
    _ = simple_python.pip_install_automation
    _ = simple_python.pip_install_all
    _ = simple_python.pip_install_all_in_ci
    _ = simple_python.poetry_lock
    _ = simple_python.poetry_export
    _ = simple_python.run_unit_test
    _ = simple_python.run_cov_test
    _ = simple_python.view_cov
    _ = simple_python.build_doc
    _ = simple_python.view_doc
    _ = simple_python.deploy_versioned_doc
    _ = simple_python.deploy_latest_doc
    _ = simple_python.view_latest_doc


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.project.simple_python", preview=False)
