from pathlib import Path

import typer
import yaml

from aviary import __version__
from aviary.pipeline.postprocessing_pipeline import (
    PostprocessingPipeline,
    PostprocessingPipelineConfig,
)
from aviary.pipeline.segmentation_pipeline import (
    SegmentationPipeline,
    SegmentationPipelineConfig,
)

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
)


def version_callback(
    value: bool,
) -> None:
    if value:
        print(f'aviary {__version__}')
        raise typer.Exit


# noinspection PyUnusedLocal
@app.callback()
def main(
    version: bool = typer.Option(  # noqa: ARG001
        None,
        '--version',
        callback=version_callback,
        help='Show the version of the package and exit.',
    ),
) -> None:
    pass


@app.command()
def segmentation_pipeline(
    config_path: str,
) -> None:
    """Run the segmentation pipeline.

    Parameters:
        config_path: path to the configuration file
    """
    with Path(config_path).open() as file:
        config = yaml.safe_load(file)

    segmentation_pipeline_config = SegmentationPipelineConfig(**config)
    segmentation_pipeline = SegmentationPipeline.from_config(segmentation_pipeline_config)
    segmentation_pipeline()


@app.command()
def postprocessing_pipeline(
    config_path: str,
) -> None:
    """Run the postprocessing pipeline.

    Parameters:
        config_path: path to the configuration file
    """
    with Path(config_path).open() as file:
        config = yaml.safe_load(file)

    postprocessing_pipeline_config = PostprocessingPipelineConfig(**config)
    postprocessing_pipeline = PostprocessingPipeline.from_config(postprocessing_pipeline_config)
    postprocessing_pipeline()


if __name__ == '__main__':
    app()
