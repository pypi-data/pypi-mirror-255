document.addEventListener('DOMContentLoaded', () => {
    const figures = document.querySelectorAll('figure')
    Array.from(figures).forEach((figure) => {
        const image = figure.querySelector('img')
        const src = image.getAttribute('src')
        const parts = src.split('/')
        const imageName = parts[parts.length - 1].split('.', 1)[0]

        // Turn the image into a link.
        const linkImage = document.createElement('a')
        linkImage.setAttribute('href', `#image-${imageName}`)
        figure.replaceChild(linkImage, image)
        const imageClone = image.cloneNode()
        linkImage.appendChild(imageClone)

        // Setup the lightbox image.
        const linkLightbox = document.createElement('a')
        linkLightbox.setAttribute('id', `image-${imageName}`)
        linkLightbox.setAttribute('href', '#_')
        linkLightbox.classList.add('lightbox')
        linkLightbox.appendChild(image)
        figure.prepend(linkLightbox)
    })
})
