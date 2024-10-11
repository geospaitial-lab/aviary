const setLinksToOpenInNewTab = () => {
  const links = document.querySelectorAll('a');

  links.forEach(link => {
    if (link.hostname !== window.location.hostname) {
      link.setAttribute('target', '_blank');
      link.setAttribute('rel', 'noopener noreferrer');
    }
  });
};

document$.subscribe(setLinksToOpenInNewTab);
