# -*- coding: utf-8 -*-

from aws_ops_alpha.runtime.api import RunTimeGroupEnum, RunTimeEnum, Runtime, runtime


class TestRuntime:
    def test_runtime(self):
        _ = runtime.is_local
        _ = runtime.is_aws_cloud9

        _ = runtime.is_aws_codebuild
        _ = runtime.is_github_action
        _ = runtime.is_gitlab_ci
        _ = runtime.is_bitbucket_pipeline
        _ = runtime.is_circleci
        _ = runtime.is_jenkins

        _ = runtime.is_aws_lambda
        _ = runtime.is_aws_batch
        _ = runtime.is_aws_glue
        _ = runtime.is_aws_ec2
        _ = runtime.is_aws_ecs

        assert isinstance(runtime.current_runtime, str)

        # none or only one of CI environment could be TRUE
        assert (
            sum(
                [
                    runtime.is_aws_codebuild,
                    runtime.is_github_action,
                    runtime.is_gitlab_ci,
                    runtime.is_bitbucket_pipeline,
                    runtime.is_circleci,
                    runtime.is_jenkins,
                ]
            )
            <= 1
        )

    def test_runtime_group(self):
        # either local, either ci
        assert (
            sum(
                [
                    runtime.is_local_runtime_group,
                    runtime.is_ci_runtime_group,
                ]
            )
            == 1
        )

        assert isinstance(runtime.current_runtime_group, str)

if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.runtime", preview=False)
