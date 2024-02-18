def test_package():
    import databricks_genai
    del databricks_genai

    from databricks_genai import finetuning
    assert finetuning
    del finetuning

    from databricks_genai import errors
    assert errors
    del errors

    from databricks_genai import types
    assert types
    assert types.finetuning
    del types
