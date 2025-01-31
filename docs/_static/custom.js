var observer = new MutationObserver(function(mutations) {   
    // check if the theme is dark
    const dark = document.documentElement.dataset.theme == 'dark';

    // loop through all elements with the class 'img-theme-switch'
    for (const element of document.getElementsByClassName('img-theme-switch')) {
        // get the current filename from the src attribute
        const currentPath = element.src;
        const filename = currentPath.split('/').pop();
        console.log("current path:", currentPath)
        console.log("current filename:", filename)

        // Check if we're dealing with the initial _images path or the modified _static path
        let filepath;
        if (currentPath.includes('_images/')) {
            // First run - convert from _images to _static
            filepath = currentPath.split('_images/')[0] + '_static/';
        } else {
            // Subsequent runs - already using _static
            filepath = currentPath.split(/dark\/|light\//)[0];
        }
        
        // get the new filename based on the theme
        const newFilename = dark ? 'dark/' + filename : 'light/' + filename;
        const newSrc = filepath + newFilename;
        
        console.log("new filename:", newFilename)
        console.log("new path:", newSrc)
        
        // set the new src
        element.src = newSrc;
    }
});

observer.observe(document.documentElement, {
    attributes: true, 
    attributeFilter: ['data-theme']
});
