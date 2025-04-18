tile_pipeline_base_config = '''plugins_dir_path: null

grid_config:
  ...

tile_fetcher_config:
  ...

tile_loader_config:
  batch_size: 1
  max_num_threads: null
  num_prefetched_tiles: 0

tiles_processor_config:
  ...
'''

registry = {
    ('tile_pipeline', 'base'): tile_pipeline_base_config,
}
