import deci_platform_client.schemas


def hack_schemas():
    """
    The generated schema classes for deci_platform_client.schemas raise errors when validating some of the data that
    the API returns (after passing pydantic validation). This is hack makes sure that the generated classes all allow
    None (and NoneClass, the generated equivalent) as inputs, bypassing this issue.
    """
    for schema in deci_platform_client.schemas.__dict__:
        schema_class = getattr(deci_platform_client.schemas, schema)
        if "_types" not in dir(schema_class):
            continue
        schema_class._types.update({type(None), deci_platform_client.schemas.NoneClass})
