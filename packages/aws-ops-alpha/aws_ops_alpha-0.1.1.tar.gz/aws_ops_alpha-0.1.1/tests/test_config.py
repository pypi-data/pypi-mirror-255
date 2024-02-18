# -*- coding: utf-8 -*-

import pytest
import typing as T
import dataclasses
from functools import cached_property

from aws_ops_alpha.paths import dir_project_root
from aws_ops_alpha.runtime.api import runtime
from aws_ops_alpha.multi_env.api import BaseEnvNameEnum, detect_current_env
from aws_ops_alpha.boto_ses.api import AlphaBotoSesFactory
from aws_ops_alpha.config.api import BaseConfig, BaseEnv


class MyEnvNameEnum(BaseEnvNameEnum):
    devops = "devops"
    sbx = "sbx"
    prd = "prd"


@dataclasses.dataclass
class MyEnv(BaseEnv):
    username: T.Optional[str] = dataclasses.field(default=None)
    password: T.Optional[str] = dataclasses.field(default=None)


@dataclasses.dataclass
class MyConfig(BaseConfig[BaseEnv]):
    @classmethod
    def get_current_env(cls) -> str:  # pragma: no cover
        return detect_current_env(runtime, MyEnvNameEnum)

    @cached_property
    def sbx(self):  # pragma: no cover
        return self.get_env(env_name=MyEnvNameEnum.sbx)

    @cached_property
    def prd(self):  # pragma: no cover
        return self.get_env(env_name=MyEnvNameEnum.prd)


@dataclasses.dataclass
class BotoSesFactory(AlphaBotoSesFactory):
    def get_env_role_session_name(self, env_name: str) -> str:
        return ""

    def get_env_role_arn(self, env_name: str) -> str:
        return ""


boto_ses_factory = BotoSesFactory(
    runtime=runtime,
    env_to_profile_mapper={
        MyEnvNameEnum.devops.value: "bmt_app_devops_us_east_1",
        MyEnvNameEnum.sbx.value: "bmt_app_dev_us_east_1",
        MyEnvNameEnum.prd.value: "bmt_app_prod_us_east_1",
    },
    default_app_env_name=MyEnvNameEnum.sbx.value,
)

dir_tests = dir_project_root / "tests"
path_config_json = dir_tests / "test_config.json"
path_config_secret_json = dir_tests / "test_config_secret.json"


skip_test = runtime.is_local is False


@pytest.mark.skipif(skip_test, reason="we don't want to run this test in CI")
def test():
    config = MyConfig.smart_load(
        runtime=runtime,
        env_name_enum_class=MyEnvNameEnum,
        env_class=MyEnv,
        path_config_json=path_config_json,
        path_config_secret_json=path_config_secret_json,
        boto_ses_factory=boto_ses_factory,
    )

    _ = config.env

    # app.py
    _ = config.env.s3uri_data
    _ = config.env.s3uri_docs
    _ = config.env.s3dir_data
    _ = config.env.s3dir_env_data
    _ = config.env.s3dir_docs
    _ = config.env.env_vars
    _ = config.env.devops_aws_tags
    _ = config.env.workload_aws_tags

    # deploy.py
    _ = config.env.s3dir_artifacts
    _ = config.env.s3dir_env_artifacts
    _ = config.env.s3dir_tmp
    _ = config.env.s3dir_config
    _ = config.env.s3uri_artifacts

    # name.py
    _ = config.env.cloudformation_stack_name

    # from rich import print as rprint
    # rprint(config)


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.config", preview=False)
