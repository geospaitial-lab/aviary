const maps = [
  { path: '../../../how_to_guides/api/maps/bounding_box.html', containerId: 'bounding-box' },
  { path: '../../../how_to_guides/api/maps/bounding_box_setter.html', containerId: 'bounding-box-setter' },
  { path: '../../../how_to_guides/api/maps/bounding_box_from_gdf.html', containerId: 'bounding-box-from-gdf' },
  { path: '../../../how_to_guides/api/maps/bounding_box_from_gdf_districts.html', containerId: 'bounding-box-from-gdf-districts' },
  { path: '../../../how_to_guides/api/maps/bounding_box_buffer_positive.html', containerId: 'bounding-box-buffer-1' },
  { path: '../../../how_to_guides/api/maps/bounding_box_buffer_negative.html', containerId: 'bounding-box-buffer-2' },
  { path: '../../../how_to_guides/api/maps/bounding_box_quantize.html', containerId: 'bounding-box-quantize' },
  { path: '../../../how_to_guides/api/maps/process_area.html', containerId: 'process-area' },
  { path: '../../../how_to_guides/api/maps/process_area_setter_coordinates.html', containerId: 'process-area-setter-coordinates' },
  { path: '../../../how_to_guides/api/maps/process_area_setter_tile_size.html', containerId: 'process-area-setter-tile-size' },
  { path: '../../../how_to_guides/api/maps/process_area_from_bounding_box.html', containerId: 'process-area-from-bounding-box' },
  { path: '../../../how_to_guides/api/maps/process_area_from_bounding_box_tile_size.html', containerId: 'process-area-from-bounding-box-tile-size' },
  { path: '../../../how_to_guides/api/maps/process_area_from_bounding_box_quantize.html', containerId: 'process-area-from-bounding-box-quantize' },
  { path: '../../../how_to_guides/api/maps/process_area_from_gdf.html', containerId: 'process-area-from-gdf' },
  { path: '../../../how_to_guides/api/maps/process_area_from_gdf_districts.html', containerId: 'process-area-from-gdf-districts' },
  { path: '../../../how_to_guides/api/maps/process_area_add.html', containerId: 'process-area-add' },
  { path: '../../../how_to_guides/api/maps/process_area_sub.html', containerId: 'process-area-sub' },
  { path: '../../../how_to_guides/api/maps/process_area_and.html', containerId: 'process-area-and' },
  { path: '../../../how_to_guides/api/maps/process_area_append.html', containerId: 'process-area-append' },
  { path: '../../../how_to_guides/api/maps/process_area_filter_difference.html', containerId: 'process-area-filter-difference' },
  { path: '../../../how_to_guides/api/maps/process_area_filter_intersection.html', containerId: 'process-area-filter-intersection' },
];

const showMap = (path, containerId) => {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = '';

    const iframe = document.createElement('iframe');
    iframe.src = path;
    iframe.width = '100%';
    iframe.height = '300px';
    iframe.style.border = 'none';

    iframe.onload = () => {
      const setAttributionLinksToOpenInNewTab = () => {
        const openStreetMapAttribution = iframe.contentDocument.querySelector(".leaflet-control-attribution a[href='https://www.openstreetmap.org/copyright']");
        if (openStreetMapAttribution) {
          openStreetMapAttribution.setAttribute('target', '_blank');
          openStreetMapAttribution.setAttribute('rel', 'noopener noreferrer');
        }

        const leafletAttribution = iframe.contentDocument.querySelector(".leaflet-control-attribution a[href='https://leafletjs.com']");
        if (leafletAttribution) {
          leafletAttribution.setAttribute('href', 'https://www.leafletjs.com');
          leafletAttribution.setAttribute('target', '_blank');
          leafletAttribution.setAttribute('rel', 'noopener noreferrer');
        }
      };

      setAttributionLinksToOpenInNewTab();

      const attributionContainer = iframe.contentDocument.querySelector('.leaflet-control-attribution');

      if (attributionContainer) {
        const observer = new MutationObserver(() => {
          setAttributionLinksToOpenInNewTab();
        });

        observer.observe(attributionContainer, { childList: true, subtree: true });

        iframe.addEventListener('unload', () => {
          observer.disconnect();
        });
      }
    };

    container.appendChild(iframe);
  }
};

const showButton = (containerId) => {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = '';

    const div = document.createElement('div');
    div.style.width = '100%';
    div.style.height = '300px';
    div.style.display = 'flex';
    div.style.alignItems = 'center';
    div.style.justifyContent = 'center';

    const button = document.createElement('a');
    button.textContent = 'Show map';
    button.className = 'md-button';
    button.href = '#__consent';

    div.appendChild(button);
    container.appendChild(div);
  }
};

const showContent = () => {
  const consent = __md_get('__consent');

  maps.forEach(map => {
    if (consent) {
      if (consent.maps) {
        showMap(map.path, map.containerId);
      } else {
        showButton(map.containerId);
      }
    }
  });
};

document$.subscribe(showContent);
