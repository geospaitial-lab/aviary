import aviary.pipeline.postprocessing_pipeline


def test_globals() -> None:
    class_names = [
        'ClipPostprocessor',
        'CompositePostprocessor',
        'FieldNamePostprocessor',
        'FillPostprocessor',
        'SievePostprocessor',
        'SimplifyPostprocessor',
        'ValuePostprocessor',
    ]

    for class_name in class_names:
        assert hasattr(aviary.pipeline.postprocessing_pipeline, class_name)
