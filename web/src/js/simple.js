"use strict";

window.onload = function(){

    // await pauses the async function
    // but does not block the entire program.
    // Other code (like console.log('End')) can run while waiting.
    async function loadAndParseIni() {
        try {
            const iniResponse = await fetch('/config/settings.ini');
            const iniContent = await iniResponse.text();

            console.log('INI file loaded successfully:', iniContent);

            return iniContent;

            // Assuming 'ini' library is already loaded and available
            // const parsedIni = ini.parse(iniContent);
            // console.log('INI file loaded and parsed successfully:', parsedIni);
            // return parsedIni
        } catch (error) {
            console.error('Error fetching or parsing the INI file:', error);
        }
    }

    function parseINIString(data){
        var regex = {
            section: /^\s*\[\s*([^\]]*)\s*\]\s*$/,
            param: /^\s*([^=]+?)\s*=\s*(.*?)\s*$/,
            comment: /^\s*;.*$/
        };
        var value = {};
        var lines = data.split(/[\r\n]+/);
        var section = null;
        lines.forEach(function(line){
            if(regex.comment.test(line)){
                return;
            }else if(regex.param.test(line)){
                var match = line.match(regex.param);
                if(section){
                    value[section][match[1]] = match[2];
                }else{
                    value[match[1]] = match[2];
                }
            }else if(regex.section.test(line)){
                var match = line.match(regex.section);
                value[match[1]] = {};
                section = match[1];
            }else if(line.length == 0 && section){
                section = null;
            };
        });
        return value;
    }

    // Call the function to load and parse the .ini file
    // const iniContent = loadAndParseIni();
    // const parsedIni = parseINIString(iniContent)
    // console.log("LLLDSDDSL" + parsedIni)

    // Input
    var catUrl = document.querySelector('.cat-url');

    // Buttons events
    var runCatBtn = document.querySelector('.run-cat-btn');
    var emptyCatBtn = document.querySelector('.empty-cat-btn');
    var weatherBtn = document.querySelector('.weather-btn');
    
    // Input 'Enter key' event
    catUrl.addEventListener("keydown", function(event) {
        if (event.keyCode == 13) {
            identifyCat();
        }
    });
    
    runCatBtn.addEventListener("click", function(event) {
        identifyCat();
    });

    weatherBtn.addEventListener("click", function(event) {
        getWeatherInfo();
    });
    
    emptyCatBtn.addEventListener("click", function(event) {
        catUrl.value = '';
        catUrl.focus();
    });
    
    // cat identification result from go-be-service
    async function identifyCat() {

        var urlVal = catUrl.value;


        try{
            const response1 = await axios({
                method: 'post',
                url: `${iniConfig.backend_go_url}/web/cat`,
                data: {
                    cat_url: urlVal,
                },
            });

            showCat(response1.data);
            catUrl.value = '';
            catUrl.focus();
        } catch(error) {
            const figureElement = document.querySelector('.cat-figure');
            figureElement.innerHTML = `<img src="src/images/error.png" class="figure-img img-fluid rounded" style="height: 256px; width: auto; alt="Error Image">`;

            
            console.log(error)
            const figureCaptionElement = document.querySelector('.cat-result');
            figureCaptionElement.innerHTML = "Error: " + error.response.status + ", " + error.response.data.message;
            // console.error("Error calling /work/cat:", error);
            if (error.response) {
                console.log(error.response.data);
            }
        }
    }
    function showCat(data) {
        console.log(JSON.stringify(data, null, 4));
        const figureElement = document.querySelector('.cat-figure');
        figureElement.innerHTML = `<img src="${data.cat_url}" class="figure-img img-fluid rounded" alt="A generic square placeholder image with rounded corners in a figure." style="height: 256px; width: auto;">`;

        const figureCaptionElement = document.querySelector('.cat-result');
        figureCaptionElement.innerHTML = "status: " + data.python_server + " (" + data.elapsed.toFixed(5) + " ⏳)";
    }

    // var pasteBtn = document.querySelector('.paste-cat-url-btn');
    // pasteBtn.addEventListener("click", function(event) {
    //     paste_into(catUrl);
    // });
    // async function paste_into(input) {
    //     const text = await navigator.clipboard.readText();
    //     input.value = text;
    // }

    async function getWeatherInfo() {
        try{
            // Make a POST request to the backend
            // const response = await fetch('http://k8s-default-fenginxi-ab0a71e16a-424716363.ap-northeast-2.elb.amazonaws.com/weather', {
            const response = await fetch(`${iniConfig.backend_go_url}/weather`, {
            // in LOCAL k8s ingress env
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    // Add any required payload here if needed
                    // key: value
                })
            });
             // Check if the response is OK (status 200)
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            
            // Parse the JSON response
            const data = await response.json();

            // Get the weather list from the response
            const weatherList = data.weather_list;
            const elapsed = data.elapsed;
        
            showWeather(weatherList, elapsed);
            showElapsed(elapsed);
        } catch(error) {
            // console.error("Error calling /work/cat:", error);
            if (error.response) {
                console.log(error.response.data);
            }
        }
    }

    function showElapsed(elapsed) {
        const elapsedEle =document.querySelector('.elapsed');
        elapsedEle.innerHTML = "3-worker in " + elapsed.toFixed(2) + "⏳";
    }

    function showWeather(weatherList) {
        // Iterate over the weather list using forEach and xtract the required elements
        weatherList.forEach((weather, index) => {
            const name = weather.name;
            const temp = weather.main.temp;
            const humidity = weather.main.humidity;
            const icon = weather.weather[0].icon;
            var iconUrl = "https://openweathermap.org/img/wn/" + icon + ".png";
            
            // Do something with the extracted data
            // console.log(`City: ${name}, Temperature: ${temp}, Icon: ${iconUrl}`);

            // Select the element with the corresponding class name
            const weatherElement = document.querySelector(`.weather${index + 1}`);
            if (weatherElement) {
                weatherElement.innerHTML = `${name} ${temp}°C, ${humidity}% <img src="${iconUrl}" style="width: 25px; height: 25px;">`;
            }
        });
    }
    
    
    // Get references to the elements
    var runMnistBtn = document.querySelector('.run-mnist-btn');
    var emptyMnistBtn = document.querySelector('.empty-mnist-btn');

    runMnistBtn.addEventListener("click", identifyDigit);

    emptyMnistBtn.addEventListener("click", function() {
            // svcListInput.focus();
            console.log("empty draw board");
    });

    // Function to get the service list
    async function identifyDigit() {
            var digit = "";

            try {
                const response2 = await axios.post(`${iniConfig.backend_go_url}/web/mnist`, {
                    drawn_digit: digit
                });

                    showDigit(response2.data);
            } catch (error) {
                    console.error(error);
            }
    }

    function showDigit(data) {
        console.log("draw the result,", data);
    }

    var cat_btn1 = document.querySelector('#cat_btn1');
    var cat_btn2 = document.querySelector('#cat_btn2');
    var noncat_btn1 = document.querySelector('#noncat_btn1');
    var noncat_btn2 = document.querySelector('#noncat_btn2');

    var cat_url1 = document.querySelector('#cat_url1');
    var cat_url2 = document.querySelector('#cat_url2');
    var noncat_url1 = document.querySelector('#noncat_url1');
    var noncat_url2 = document.querySelector('#noncat_url2');

    cat_btn1.addEventListener("click", function(event) {
        copyToClipboard("cat_url1");
    });
    cat_btn2.addEventListener("click", function(event) {
        copyToClipboard("cat_url2");
    });
    noncat_btn1.addEventListener("click", function(event) {
        copyToClipboard("noncat_url1");
    });
    noncat_btn2.addEventListener("click", function(event) {
        copyToClipboard("noncat_url2");
    });

    cat_url1.addEventListener("click", function(event) {
        copyToClipboard("cat_url1");
    });
    cat_url2.addEventListener("click", function(event) {
        copyToClipboard("cat_url2");
    });
    noncat_url1.addEventListener("click", function(event) {
        copyToClipboard("noncat_url1");
    });
    noncat_url2.addEventListener("click", function(event) {
        copyToClipboard("noncat_url2");
    });

    function copyToClipboard(id) {
        var textToCopy = document.getElementById(id).innerText.trim();
        
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(textToCopy).then(function() {
                console.log('Copying to clipboard was successful!');
            }, function(err) {
                console.error('Could not copy text: ', err);
            });
        } else {
            // Fallback method for browsers that do not support the Clipboard API
            var textArea = document.createElement("textarea");
            textArea.value = textToCopy;
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                 // document.execCommand('copy'); // Deprecated
                navigator.clipboard.writeText(textArea.value).then(function() {
                    console.log('Copying to clipboard was successful!');
                }, function(err) {
                    console.error('Could not copy text: ', err);
                });
            } catch (err) {
                console.error('Could not copy text: ', err);
            }
            document.body.removeChild(textArea);
        }
    }

}
