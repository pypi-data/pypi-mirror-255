# -*- coding: utf-8 -*-

from s3pathlib import S3Path

from aws_ops_alpha.aws_helpers.rich_helpers import (
    create_path_table,
    create_s3path_table,
    create_url_table,
)


def test():
    table = create_path_table(
        [("rich_helpers.py", __file__)],
    )

    table = create_s3path_table(
        [("s3dir_artifacts", S3Path("s3://my-bucket/artifacts/"))],
    )

    table = create_url_table(
        [("project homepage", "https://my-project.com/")],
    )


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.aws_helpers.rich_helpers", preview=False)
