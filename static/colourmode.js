// set default colour mode on initial page load

function setColourMode(newMode) {
    $.get("/getmethod/"+newMode);
}

function toggleMode(){
    if (window.colourSet){
        // set this line to change default
        var colourMode = window.colourMode ? window.colourMode : "light-mode";
        var newMode = colourMode == "dark-mode" ? "light-mode" : "dark-mode";
    } else {
        // set this line also to change default
        var newMode = window.colourMode ? window.colourMode : "light-mode";
        var colourMode = newMode == "dark-mode" ? "light-mode" : "dark-mode";
    }

    var modes = [
        {'selector': 'nav', 'light-mode': 'bg-light', 'dark-mode': 'bg-black'},
        {'selector': 'input', 'light-mode': 'bg-light', 'dark-mode': 'bg-secondary'},
        {'selector': '*', 'light-mode': 'border-default', 'dark-mode': 'border-black'},
        {'selector': '.card', 'light-mode': 'bg-white', 'dark-mode': 'bg-dark'},
        {'selector': '*', 'light-mode': 'bg-white', 'dark-mode': 'bg-dark'},
        {'selector': '*', 'light-mode': 'text-dark', 'dark-mode': 'text-white'},
        {'selector': '*', 'light-mode': 'text-black', 'dark-mode': 'text-light'},
        {'selector': '*', 'light-mode': 'navbar-light', 'dark-mode': 'navbar-dark'},
        {'selector': 'a[type*="button"]', 'light-mode': 'btn-dark', 'dark-mode': 'btn-light'},
        {'selector': 'table', 'light-mode': 'table-white', 'dark-mode': 'table-dark'},
        {'selector': 'a', 'light-mode': 'link-secondary', 'dark-mode': 'link-info'},
        {'selector': 'i', 'light-mode': 'bi-sun-fill', 'dark-mode': 'bi-moon-fill'},
        {'selector': '*', 'light-mode': 'light-mode', 'dark-mode': 'dark-mode'}
    ];



    for (var i = 0; i < modes.length; i++) {
        var currSelector = modes[i]["selector"];
        var elsToChange = document.querySelectorAll(currSelector+"."+colourMode);
        for (var j = elsToChange.length - 1; j >= 0; j--) {
            var currEl = elsToChange[j];
            var oldClass = modes[i][colourMode];
            var newClass = modes[i][newMode];

            if (currEl.classList.contains(oldClass)) {
                currEl.classList.remove(oldClass);
                currEl.classList.add(newClass);
            }
        }
    }

    window.colourMode = newMode;
    window.colourSet = true;
    setColourMode(newMode);
}

