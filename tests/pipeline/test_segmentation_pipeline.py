import aviary.pipeline.segmentation_pipeline


def test_globals() -> None:
    class_names = [
        'CompositePreprocessor',
        'CompositePreprocessorConfig',
        'NormalizePreprocessor',
        'NormalizePreprocessorConfig',
        'ONNXSegmentationModel',
        'SegmentationExporter',
        'SegmentationExporterConfig',
        'SegmentationModelConfig',
        'StandardizePreprocessor',
        'StandardizePreprocessorConfig',
        'VRTFetcher',
        'VRTFetcherConfig',
        'WMSFetcher',
        'WMSFetcherConfig',
    ]

    for class_name in class_names:
        assert hasattr(aviary.pipeline.segmentation_pipeline, class_name)
