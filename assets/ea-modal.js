/* Full-screen toggle for modals: any element with .ea-modal-full sends its
 * enclosing Mantine modal content into browser fullscreen; Escape leaves it.
 * A delegated listener, so it works for content Dash mounts at any time. */
(function () {
  document.addEventListener('click', function (ev) {
    const btn = ev.target.closest ? ev.target.closest('.ea-modal-full') : null;
    if (!btn) { return; }
    const content = btn.closest('.mantine-Modal-content');
    if (!content) { return; }
    if (document.fullscreenElement) { document.exitFullscreen(); }
    else { content.requestFullscreen(); }
  });
})();
