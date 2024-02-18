def test_has_table(data_storage):
    db = data_storage.ddb
    table = data_storage.nodes_table("s3://bucket", 1).table
    assert not db.has_table(table.name)
    table.create(db.engine)
    assert db.has_table(table.name)


def test_has_table_in_transaction(data_storage):
    db = data_storage.mdb
    table = data_storage.partials_table("s3://bucket")
    assert not db.has_table(table.name)
    with db.transaction():
        table.create(db.engine)
        assert db.has_table(table.name)
