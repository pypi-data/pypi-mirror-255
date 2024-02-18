# -*- coding: utf-8 -*-

from aws_ops_alpha import api


def test():
    _ = api
    _ = api.constants
    _ = api.logger
    _ = api.CommonEnvNameEnum
    _ = api.EnvVarNameEnum
    _ = api.AwsTagNameEnum
    _ = api.AwsOpsSemanticBranchEnum
    _ = api.temp_env_var
    _ = api.normalize_env_var_name
    _ = api.get_environment_aws_account_id_in_ci
    _ = api.get_environment_iam_role_arn_in_dev_server
    _ = api.temp_env_var
    _ = api.RunTimeGroupEnum
    _ = api.RunTimeEnum
    _ = api.Runtime
    _ = api.runtime
    _ = api.EnvNameValidationError
    _ = api.validate_env_name
    _ = api.BaseEnvNameEnum
    _ = api.env_emoji_mapper
    _ = api.EnvNameEnum
    _ = api.detect_current_env
    _ = api.InvalidSemanticNameError
    _ = api.SemanticBranchRule
    _ = api.GitRepo
    _ = api.extract_semantic_branch_name_for_multi_repo
    _ = api.extract_semantic_branch_name_for_mono_repo
    _ = api.MultiGitRepo
    _ = api.MonoGitRepo
    _ = api.AbstractBotoSesFactory
    _ = api.AlphaBotoSesFactory
    _ = api.BaseConfig
    _ = api.BaseEnv
    _ = api.T_BASE_CONFIG
    _ = api.T_BASE_ENV
    _ = api.aws_cdk_helpers
    _ = api.aws_lambda_helpers
    _ = api.simple_python_project
    _ = api.simple_cdk_project
    _ = api.simple_config_project
    _ = api.simple_lambda_project


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.api", preview=False)
