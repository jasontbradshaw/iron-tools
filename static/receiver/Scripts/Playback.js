function hideButton(buttonId)
{
//    var button = $("#" + buttonId);
//    button.addClass("hidden");
    //    button.removeClass("visible");
    disableButton(buttonId);
}

function showButton(buttonId)
{
//    var button = $("#" + buttonId);
//    button.addClass("visible");
    //    button.removeClass("hidden");
    enableButton(buttonId);
}

var sortedResult;

function populateFileList(data)
{
    data.sort(fileSorter);
    var list = $("#videoList")[0];

    list.add(createOption("", ""));

    for (var i = 0; i < data.length; i++)
    {
        var startTime = (data[i].start_time_received ? "" : "no ") + "start time";
        var option = createOption(data[i].filename, data[i].filename + " - " + startTime + " - " + getFileSize(data[i].file_size) + " MB");
        list.add(option);
    }

    sortedResult = data;
}

function createOption(value, text)
{
    var e = document.createElement("OPTION");
    e.value = value;
    e.text = text; 
    return e;
}

Math.roundTo = function (value, decimals)
{
    var factor = Math.pow(10, decimals);
    return Math.round(value * factor) / factor;
}


function getFileSize(bytes)
{
    return Math.roundTo(bytes / 1024 / 1024, 2);
    //   return Math.round(bytes / 1024 / 1024 * 100)/100;
}

function fileSorter(fileA, fileB)
{
    if (fileA.filename < fileB.filename)
    {
        return 1;
    }
    else if (fileA.filename == fileB.filename)
    {
        return 0;
    }
    else
    {
        return -1;
    }
}

function getFileList(callback)
{
    getJSON("../../get_file_list", null, true, function (data) { getFileListOnComplete(data, callback); }, getFileListOnError);
}

function getFileListOnComplete(data, callback)
{
    if (data.length > 0)
    {
        populateFileList(data);
        videoListOnChange();

        if (callback != null && typeof (callback) == "function")
        {
            callback();
        }
    }
    else
    {
        //throw error
    }
}

function videoListOnChange()
{
    showButton("load");
    hideButton("play");
    hideButton("stop");
}

function getFileListOnError(xmlHttpRequest, status, errorThrown)
{
    
}

function loadVideo(loadButton)
{
    if (!loadButton.disabled)
    {
        var list = $("#videoList")[0];
        var selectedOption = list.options[list.selectedIndex].value;
        if (String.isNullOrEmpty(selectedOption))
        {
            alert("Please select a video to load");
        }
        else
        {
            var params = new Array();
            params.push(selectedOption);
            getJSON("../../arm", params, true, loadVideoOnComplete, loadVideoOnError);
        }
    }
}

function loadVideoOnComplete(status)
{
    if (String.isNullOrEmpty(status.error))
    {
        hideButton("load");
        showButton("play");
        hideButton("stop");
        displayStatusMessage("Video loaded successfully", false);
    }
    else
    {
        displayStatusMessage("Unable to load video: " + status.error, true);
    }
}

function loadVideoOnError(xmlHttpRequest, status, errorThrown)
{
    displayStatusMessage("Unable to load video: " + errorThrown, true);
}

function playVideo(playButton)
{
    if (!playButton.disabled)
    {
        getJSON("../../play", null, true, playVideoOnComplete, playVideoOnError);
    }
}

function playVideoOnComplete(status)
{
    if (String.isNullOrEmpty(status.error))
    {
        hideButton("load");
        hideButton("play");
        showButton("stop");
        $("#videoList")[0].disabled = true;
        displayStatusMessage("Video playback started successfully", false);
    }
    else
    {
        displayStatusMessage("Unable to start video playback: " + status.error, true);
    }
}

function playVideoOnError(xmlHttpRequest, status, errorThrown)
{
    displayStatusMessage("Unable to start video playback: " + errorThrown, true);
}

function stopVideo(stopButton)
{
    if (!stopButton.disabled)
    {
        getJSON("../../stop", null, true, stopVideoOnComplete, stopVideoOnError);
    }
}

function stopVideoOnComplete(status)
{
    if (String.isNullOrEmpty(status.error))
    {
        showButton("load");
        hideButton("play");
        hideButton("stop");
        $("#videoList")[0].disabled = false;
        displayStatusMessage("Video playback stopped successfully", false);
    }
    else
    {
        displayStatusMessage("Unable to stop video playback: " + status.error, true);
    }
}

function stopVideoOnError(xmlHttpRequest, status, errorThrown)
{
    displayStatusMessage("Unable to stop video playback: " + errorThrown, true);
}