let contador = 0;

function moverSlider() {
    const slider = document.getElementById("slider");
    const totalSlides = slider.children.length;
    contador = (contador + 1) % totalSlides;
    slider.style.transform = `translateX(-${contador * 100}%)`;
}

setInterval(moverSlider, 4000); // cada 3 segundos
