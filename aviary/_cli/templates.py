#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and/or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

composite_pipeline_config = '''package: 'aviary'
name: 'CompositePipeline'
config:
  pipeline_configs:
    - ...
    ...
'''

tile_pipeline_base_config = '''package: 'aviary'
name: 'TilePipeline'
config:
  plugins_dir_path: null
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

vector_pipeline_base_config = '''package: 'aviary'
name: 'VectorPipeline'
config:
  plugins_dir_path: null

  vector_loader_config:
    ...

  vector_processor_config:
    ...
'''

registry = {
    ('composite_pipeline', 'base'): composite_pipeline_config,
    ('tile_pipeline', 'base'): tile_pipeline_base_config,
    ('vector_pipeline', 'base'): vector_pipeline_base_config,
}
