import typer
import yaml

from aviary import __version__
from aviary.pipeline.segmentation_pipeline import (
    SegmentationPipeline,
    SegmentationPipelineConfig,
)

app = typer.Typer()


@app.command()
def segmentation_pipeline(
    config_path: str,
) -> None:
    """Run the segmentation pipeline.

    Parameters:
        config_path: path to the configuration file
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    segmentation_pipeline_config = SegmentationPipelineConfig(**config)
    segmentation_pipeline = SegmentationPipeline.from_config(segmentation_pipeline_config)
    segmentation_pipeline()


@app.command()
def version() -> None:
    """Show the version of the package."""
    typer.echo(__version__)


if __name__ == "__main__":
    app()
