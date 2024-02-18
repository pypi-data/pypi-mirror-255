# -*- coding: utf-8 -*-

"""
Runtime is the type of computational resource where you run your code.
For example, local laptop, AWS EC2, AWS Lambda, CI/CD build environment, etc.
You may need to determine the current runtime to make your code behave differently.

This module can detect the current runtime information using LAZY LOAD technique.

Requirements: Python>=3.8

Dependencies::

    cached-property>=1.5.2; python_version < '3.8'

Usage example::

    from runtime import runtime
"""

import os
import sys
import enum
from functools import cached_property


class RunTimeEnum(str, enum.Enum):
    local = "local"  # local laptop
    aws_codebuild = "aws_codebuild"
    github_action = "github_action"
    gitlab_ci = "gitlab_ci"
    bitbucket_pipeline = "bitbucket_pipeline"
    circleci = "circleci"
    jenkins = "jenkins"
    ci = "ci"
    aws_lambda = "aws_lambda"
    aws_batch = "aws_batch"
    aws_glue = "aws_glue"
    aws_cloud9 = "aws_cloud9"
    aws_ec2 = "aws_ec2"
    aws_ecs = "aws_ecs"
    unknown = "unknown"


class Runtime:
    """
    Detect the current runtime information by inspecting environment variables.

    The instance of this class is the entry point of all kinds of runtime related
    variables, methods.
    """

    @cached_property
    def is_aws_codebuild(self) -> bool:
        # ref: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html
        return "CODEBUILD_BUILD_ID" in os.environ

    @cached_property
    def is_github_action(self) -> bool:
        # ref: https://docs.github.com/en/actions/learn-github-actions/variables
        return "GITHUB_ACTION" in os.environ

    @cached_property
    def is_gitlab_ci(self) -> bool:
        # ref: https://docs.gitlab.com/ee/ci/variables/predefined_variables.html
        return "CI_PROJECT_ID" in os.environ

    @cached_property
    def is_bitbucket_pipeline(self) -> bool:
        # ref: https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/
        return "BITBUCKET_BUILD_NUMBER" in os.environ

    @cached_property
    def is_circleci(self) -> bool:
        # ref: https://circleci.com/docs/variables/
        return "CIRCLECI" in os.environ

    @cached_property
    def is_jenkins(self) -> bool:
        # ref: https://www.jenkins.io/doc/book/pipeline/jenkinsfile/#using-environment-variables
        return "BUILD_TAG" in os.environ and "EXECUTOR_NUMBER" in os.environ

    @cached_property
    def is_ci(self) -> bool:
        if (
            self.is_aws_codebuild
            or self.is_github_action
            or self.is_gitlab_ci
            or self.is_bitbucket_pipeline
            or self.is_circleci
            or self.is_jenkins
        ):
            return True
        else:
            return "CI" in os.environ

    @cached_property
    def is_aws_lambda(self) -> bool:
        # ref: https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html
        return "AWS_LAMBDA_FUNCTION_NAME" in os.environ

    @cached_property
    def is_aws_batch(self) -> bool:
        # ref: https://docs.aws.amazon.com/batch/latest/userguide/job_env_vars.html
        return "AWS_BATCH_JOB_ID" in os.environ

    @cached_property
    def is_aws_glue(self) -> bool:
        return "--JOB_RUN_ID" in sys.argv

    @cached_property
    def is_aws_cloud9(self) -> bool:
        return "C9" in os.environ

    @cached_property
    def is_aws_ec2(self) -> bool:
        # there's no official way to detect if it is ec2 instance
        # you could set a custom environment variable for all your ec2 instances
        return "IS_AWS_EC2" in os.environ

    @cached_property
    def is_aws_ecs(self) -> bool:
        # there's no official way to detect if it is ec2 instance
        # you could set a custom environment variable for all your ec2 instances
        # ref: https://docs.aws.amazon.com/AmazonECS/latest/userguide/taskdef-envfiles.html
        return "IS_AWS_ECS_TASK" in os.environ

    @cached_property
    def is_local(self) -> bool:
        if (
            self.is_aws_codebuild
            or self.is_github_action
            or self.is_gitlab_ci
            or self.is_bitbucket_pipeline
            or self.is_circleci
            or self.is_jenkins
            or self.is_ci
            or self.is_aws_lambda
            or self.is_aws_batch
            or self.is_aws_glue
            or self.is_aws_cloud9
            or self.is_aws_ec2
            or self.is_aws_ecs
        ):
            return False
        else:
            return True

    @cached_property
    def current_runtime(self):  # pragma: no cover
        """
        Return the human friendly name of the current runtime.
        """
        if self.is_aws_codebuild:
            return RunTimeEnum.aws_codebuild.value
        if self.is_github_action:
            return RunTimeEnum.github_action.value
        if self.is_gitlab_ci:
            return RunTimeEnum.gitlab_ci.value
        if self.is_bitbucket_pipeline:
            return RunTimeEnum.bitbucket_pipeline.value
        if self.is_circleci:
            return RunTimeEnum.circleci.value
        if self.is_jenkins:
            return RunTimeEnum.jenkins.value
        if self.is_ci:
            return RunTimeEnum.ci.value
        if self.is_aws_lambda:
            return RunTimeEnum.aws_lambda.value
        if self.is_aws_batch:
            return RunTimeEnum.aws_batch.value
        if self.is_aws_glue:
            return RunTimeEnum.aws_glue.value
        if self.is_aws_cloud9:
            return RunTimeEnum.aws_cloud9.value
        if self.is_aws_ec2:
            return RunTimeEnum.aws_ec2.value
        if self.is_aws_ecs:
            return RunTimeEnum.aws_ecs.value
        if self.is_local:
            return RunTimeEnum.local.value
        return RunTimeEnum.unknown.value

    @cached_property
    def local_or_ci(self) -> str:
        if self.is_ci:
            return RunTimeEnum.ci.value
        if self.is_local:
            return RunTimeEnum.local.value
        raise ValueError("Not in local or CI environment")


runtime = Runtime()
