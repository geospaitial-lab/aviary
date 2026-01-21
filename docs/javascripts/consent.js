const maps = [
  { path: '../../../how_to_guides/api/maps/bounding_box.html', containerId: 'bounding-box' },
  { path: '../../../how_to_guides/api/maps/bounding_box_from_gdf.html', containerId: 'bounding-box-from-gdf' },
  { path: '../../../how_to_guides/api/maps/bounding_box_from_gdf_districts.html', containerId: 'bounding-box-from-gdf-districts' },
  { path: '../../../how_to_guides/api/maps/bounding_box_and.html', containerId: 'bounding-box-and' },
  { path: '../../../how_to_guides/api/maps/bounding_box_or.html', containerId: 'bounding-box-or' },
  { path: '../../../how_to_guides/api/maps/bounding_box_buffer_positive.html', containerId: 'bounding-box-buffer-1' },
  { path: '../../../how_to_guides/api/maps/bounding_box_buffer_negative.html', containerId: 'bounding-box-buffer-2' },
  { path: '../../../how_to_guides/api/maps/bounding_box_quantize.html', containerId: 'bounding-box-snap' },
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
