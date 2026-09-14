document.addEventListener('DOMContentLoaded', () => {
    const playBtn = document.getElementById('playBtn');
    const modal = document.getElementById('videoModal');
    const overlay = document.getElementById('modalOverlay');
    const closeBtn = document.getElementById('modalClose');
    const video = document.getElementById('modalVideo');

    // Открыть модалку
    playBtn.addEventListener('click', () => {
        modal.classList.add('active');
        video.play();
    });

    // Закрыть по крестику
    closeBtn.addEventListener('click', closeModal);

    // Закрыть по клику на оверлей
    overlay.addEventListener('click', closeModal);

    // Закрыть по Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });

    function closeModal() {
        modal.classList.remove('active');
        video.pause();
        video.currentTime = 0;
    }
});