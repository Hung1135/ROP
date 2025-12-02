
const container = document.getElementById('container');
const overlayBtn = document.getElementById('overlayBtn');
const overlayCon = document.getElementById('overlayCon');

overlayBtn.addEventListener('click', () => {
    container.classList.toggle('right-panel-active');

    if (container.classList.contains('right-panel-active')) {
        overlayCon.style.transform = 'translateX(-150%)';
    } else {
        overlayCon.style.transform = 'translateX(0)';
    }
});

document.querySelector('.overlay-right button').addEventListener('click', () => {
    container.classList.add('right-panel-active');
    overlayCon.style.transform = 'translateX(-150%)';
});

document.querySelector('.overlay-left button').addEventListener('click', () => {
    container.classList.remove('right-panel-active');
    overlayCon.style.transform = 'translateX(0)';
});
