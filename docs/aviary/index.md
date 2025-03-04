<style>
  @media screen and (min-width: 76.25em) {
    .md-sidebar--primary { visibility: hidden }
  }
</style>

The aviary is a collection of task-specific models for remote sensing applications.<br />
By now, the aviary includes just a single model, but we plan to add more models in future releases.

## sparrow

sparrow is a segmentation model that is trained to detect and classify impervious surfaces
from digital orthophotos.<br />
It differentiates between non-impervious surfaces (e.g., vegetation, soil or water), buildings and
impervious surfaces (e.g., pavements, roads, sidewalks, driveways, parking lots or industrial areas).
We recommend to use the model with **leaf-off** orthophotos (i.e., without foliage on trees or shrubs),
so canopies don't cover buildings or impervious surfaces.

### Requirements

- Channels: RGB (red, green, blue) and NIR (near-infrared)
- Ground sampling distance: 0.2m
- Normalized data: [0, 1]

---

### Mapping of the values

- 0: non-impervious surfaces
- 1: buildings
- 2: impervious surfaces

---

### Create the model with the Python API

If you want to use the [Python API], you can create an [`ONNXSegmentationModel`][ONNXSegmentationModel] as follows:

``` python
from aviary.inference import ONNXSegmentationModel

model = ONNXSegmentationModel.from_aviary('sparrow')
```

  [Python API]: ../api_reference/index.md
  [ONNXSegmentationModel]: ../api_reference/inference/model/onnx_segmentation_model.md

---

### Create the model with the CLI

If you want to use the [command-line interface (CLI)], you can use the following configuration:

``` yaml title="config.yaml"
model:
  name: ONNXSegmentationModel
  config:
    name: sparrow
```

  [command-line interface (CLI)]: ../cli_reference/segmentation_pipeline.md

---

### Next steps

Have a look at the [how-to guide] on how to run the segmentation pipeline with the CLI using sparrow.

  [how-to guide]: ../how_to_guides/cli/how_to_run_the_segmentation_pipeline.md
