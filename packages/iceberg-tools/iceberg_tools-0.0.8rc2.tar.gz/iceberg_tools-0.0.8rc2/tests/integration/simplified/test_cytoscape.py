from iceberg_tools.schema.simplified_validator import ensure_schema


def test_cytoscape(distribution_schema_path):
    """Ensure specimen and document_reference have _identifier denormalized fields."""
    schema = ensure_schema(schema_path=distribution_schema_path)
    assert schema, f"should have loaded {distribution_schema_path}"
    ignore = ['root', 'data_release', 'core_metadata_collection']
    sources = [_ for _ in schema.keys() if _ not in ignore]

    edge_table_path = "/tmp/simplified_network_table.tsv"
    with open(edge_table_path, "w") as fp:
        print("source\ttarget\tname", file=fp)
        for source in sources:
            for _ in schema[source]['links']:
                assert 'target_type' in _, f"should have target in {source} {_}"
                assert 'name' in _, f"should have name in {source} {_}"

            targets = [(_['target_type'], _['name']) for _ in schema[source]['links']]
            for target, name in targets:
                print(f"{source}\t{target}\t{name}", file=fp)
