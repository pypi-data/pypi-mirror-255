# -*- coding: utf-8 -*-

import os
import pytest

from aws_ops_alpha.constants import EnvVarNameEnum
from aws_ops_alpha.runtime.api import runtime
from aws_ops_alpha.multi_env.api import (
    EnvNameValidationError,
    validate_env_name,
    BaseEnvNameEnum,
    env_emoji_mapper,
    EnvNameEnum,
    detect_current_env,
)


def test_validate_env_name():
    validate_env_name("devops")
    validate_env_name("sbx1")

    with pytest.raises(EnvNameValidationError):
        validate_env_name("1")

    with pytest.raises(EnvNameValidationError):
        validate_env_name("sbx-1")


class TestEnvNameEnum:
    """
    Test the built-in ``EnvNameEnum`` class.
    """

    def test_emoji(self):
        for env_name in EnvNameEnum:
            _ = env_name.emoji
            # print(f"{env_name = } = {env_name.emoji = }")

    def test_validate(self):
        EnvNameEnum.validate()

        class Enum1(BaseEnvNameEnum):
            devops = "devops"

        with pytest.raises(ValueError):
            Enum1.validate()

        class Enum2(BaseEnvNameEnum):
            dev = "dev"

        with pytest.raises(ValueError):
            Enum2.validate()

        class Enum3(BaseEnvNameEnum):
            devops = "devops"
            sbx = "sbx"
            prd = "prd"
            first = "1"

        with pytest.raises(EnvNameValidationError):
            Enum3.validate()

    def test_get_xyz(self):
        assert EnvNameEnum._get_devops() == EnvNameEnum.devops.value
        assert EnvNameEnum._get_sbx() == EnvNameEnum.sbx.value
        assert EnvNameEnum._get_prd() == EnvNameEnum.prd.value


class MyEnvNameEnum(BaseEnvNameEnum):
    """
    A custom environment name enum.
    """

    devops = "devops"
    sbx = "sbx"
    tst = "tst"
    stg = "stg"
    prd = "prd"


class TestMyEnvEnum:
    def test(self):
        os.environ[EnvVarNameEnum.USER_ENV_NAME.value] = "sbx"
        env_name = detect_current_env(runtime, MyEnvNameEnum)
        # print(f"{env_name = }")


def test_detect_current_env():
    os.environ[EnvVarNameEnum.USER_ENV_NAME.value] = "sbx"
    env_name = detect_current_env(runtime, MyEnvNameEnum)
    # print(f"{env_name = }")


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.multi_env", preview=False)
