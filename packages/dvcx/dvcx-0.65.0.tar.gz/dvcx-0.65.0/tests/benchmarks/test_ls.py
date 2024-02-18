def test_ls(bench_dql, tmp_dir, bucket):
    bench_dql("ls", bucket, "--aws-anon")
