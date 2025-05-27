var lastXDaysSlider = document.getElementById("lastXDaysRange");
var lastXDaysOutput = document.getElementById("lastXDaysValue");
lastXDaysOutput.innerHTML = lastXDaysSlider.value;

lastXDaysSlider.oninput = function () {
    lastXDaysOutput.innerHTML = this.value;
}

var maxNumOfArticlesSlider = document.getElementById("maxNumOfArticlesRange");
var maxNumOfArticlesOutput = document.getElementById("maxNumOfArticlesValue");
maxNumOfArticlesOutput.innerHTML = maxNumOfArticlesSlider.value;
var reqToLoad = document.getElementById("req-to-load");
reqToLoad.innerHTML = maxNumOfArticlesSlider.value;

maxNumOfArticlesSlider.oninput = function () {
    maxNumOfArticlesOutput.innerHTML = this.value;
}
