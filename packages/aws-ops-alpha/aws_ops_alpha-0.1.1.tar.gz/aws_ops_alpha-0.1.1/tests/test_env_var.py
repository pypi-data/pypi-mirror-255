# -*- coding: utf-8 -*-


from aws_ops_alpha.env_var import (
    _get_key,
)


def test_get_key():
    assert _get_key("sbx", "AWS_ACCOUNT_ID") == "SBX_AWS_ACCOUNT_ID"
    assert _get_key("sbx", "AWS_ACCOUNT_ID", "DESCRIPTION") == "SBX_AWS_ACCOUNT_ID_DESCRIPTION"


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.env_var", preview=False)
