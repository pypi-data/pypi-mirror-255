# -*- coding: utf-8 -*-

import os
from aws_ops_alpha.constants import (
    CommonEnvNameEnum,
    EnvVarNameEnum,
    AwsOpsSemanticBranchEnum,
)

def test():
    for enum_class in [
        CommonEnvNameEnum,
        EnvVarNameEnum,
        AwsOpsSemanticBranchEnum,
    ]:
        for enum_obj in enum_class:
            assert enum_class.is_valid_value(enum_obj.value) is True


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.constants", preview=False)
