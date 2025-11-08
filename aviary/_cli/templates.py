pipeline_config = '''tile_pipeline_config:
  ...

vector_pipeline_config:
  ...
'''

tile_pipeline_base_config = '''plugins_dir_path: null
show_progress: true

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

vector_pipeline_base_config = '''plugins_dir_path: null

vector_loader_config:
  ...

vector_processor_config:
  ...
'''

registry = {
    ('pipeline', 'base'): pipeline_config,
    ('tile_pipeline', 'base'): tile_pipeline_base_config,
    ('vector_pipeline', 'base'): vector_pipeline_base_config,
}
