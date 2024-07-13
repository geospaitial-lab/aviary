import aviary.pipeline.segmentation_pipeline


def test_globals() -> None:
    class_names = [
        'CompositePreprocessor',
        'NormalizePreprocessor',
        'ONNXSegmentationModel',
        'SegmentationExporter',
        'StandardizePreprocessor',
        'VRTFetcher',
    ]

    for class_name in class_names:
        assert hasattr(aviary.pipeline.segmentation_pipeline, class_name)
