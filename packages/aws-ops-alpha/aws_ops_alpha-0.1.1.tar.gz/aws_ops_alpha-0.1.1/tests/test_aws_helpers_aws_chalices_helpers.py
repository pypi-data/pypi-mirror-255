# -*- coding: utf-8 -*-

import sys
from pyproject_ops.api import PyProjectOps
from aws_ops_alpha.paths import dir_project_root, PACKAGE_NAME
from aws_ops_alpha.aws_helpers.aws_chalice_helpers import (
    build_lambda_source_chalice_vendor,
    get_source_sha256,
)


def test():
    pyproject_ops = PyProjectOps(
        dir_project_root=dir_project_root,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
        package_name=PACKAGE_NAME,
    )
    build_lambda_source_chalice_vendor(pyproject_ops)
    get_source_sha256(pyproject_ops)


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(
        __file__, "aws_ops_alpha.aws_helpers.aws_chalice_helpers", preview=False
    )
