# -*- coding: utf-8 -*-

import pytest

from aws_ops_alpha.paths import dir_project_root
from aws_ops_alpha.git.api import (
    InvalidSemanticNameError,
    SemanticBranchRule,
    MultiGitRepo,
    MonoGitRepo,
    extract_semantic_branch_name_for_multi_repo,
    extract_semantic_branch_name_for_mono_repo,
)

# fmt: off
def test_extract_semantic_branch_name_for_multi_repo():
    assert extract_semantic_branch_name_for_multi_repo("main") == 'main'
    assert extract_semantic_branch_name_for_multi_repo("feature/add-this-feature") == 'feature'


def test_extract_semantic_branch_name_for_mono_repo():
    assert extract_semantic_branch_name_for_mono_repo("main") == 'main'
    assert extract_semantic_branch_name_for_mono_repo("my_project/feature/add-this-feature") == 'feature'
# fmt: on


class TestGitRepo:
    def test(self):
        git_repo = MultiGitRepo(dir_project_root)

        # property
        _ = git_repo.git_branch_name
        _ = git_repo.git_commit_id
        _ = git_repo.git_commit_message

        git_repo.print_git_info(verbose=False)

        # is certain branch
        _ = git_repo.is_main_branch
        _ = git_repo.is_feature_branch
        _ = git_repo.is_fix_branch
        _ = git_repo.is_doc_branch
        _ = git_repo.is_release_branch
        _ = git_repo.is_cleanup_branch
        _ = git_repo.is_lambda_branch
        _ = git_repo.is_layer_branch
        _ = git_repo.is_ecr_branch
        _ = git_repo.is_ami_branch
        _ = git_repo.is_glue_branch
        _ = git_repo.is_sfn_branch
        _ = git_repo.is_airflow_branch

    def test_semantic_branch_name(self):
        def _test(git_branch_name, expected_part, expected_name):
            git_repo = MultiGitRepo(
                dir_project_root,
                sem_branch_rule=SemanticBranchRule(
                    rules={"main": ["main", "master"], "feature": ["feature", "feat"]},
                ),
            )
            # force override git_branch_name
            git_repo.git_branch_name = git_branch_name
            assert git_repo.semantic_branch_part == expected_part
            assert git_repo.semantic_branch_name == expected_name

        _test("main", "main", "main")
        _test("feature", "feature", "feature")
        _test("feat", "feat", "feature")
        _test("feat/description", "feat", "feature")
        _test("feat-123/description", "feat-123", "feature")
        with pytest.raises(InvalidSemanticNameError):
            _test("release", "release", None)


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.git", preview=False)
