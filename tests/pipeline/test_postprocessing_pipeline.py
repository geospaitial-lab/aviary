import aviary.pipeline.postprocessing_pipeline


def test_globals() -> None:
    class_names = [
        'ClipPostprocessor',
        'ClipPostprocessorConfig',
        'CompositePostprocessor',
        'CompositePostprocessorConfig',
        'FieldNamePostprocessor',
        'FieldNamePostprocessorConfig',
        'FillPostprocessor',
        'FillPostprocessorConfig',
        'SievePostprocessor',
        'SievePostprocessorConfig',
        'SimplifyPostprocessor',
        'SimplifyPostprocessorConfig',
        'ValuePostprocessor',
        'ValuePostprocessorConfig',
    ]

    for class_name in class_names:
        assert hasattr(aviary.pipeline.postprocessing_pipeline, class_name)
