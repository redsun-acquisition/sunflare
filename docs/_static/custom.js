var observer = new MutationObserver(function(mutations) {   
    // check if the theme is dark
    const dark = document.documentElement.dataset.theme == 'dark';

    // loop through all elements with the class 'img-theme-switch'
    for (const element of document.getElementsByClassName('img-theme-switch')) {
        // get the filename from the src attribute
        path = element.src.split('/').pop();

        // set the new src attribute based on the theme
        element.src = dark ? `_static/dark/${path}` : `_static/light/${path}`;
    }
})
observer.observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});
