

/*
Result : function()
{}

Result.prototype.seconds_elapsed:0;

seconds_elapsed: 0,
is_recording: false,
committed_time: 0
}*/

function copyFromElapsedTime() {
  committedTime = $("#committedTime");

  committedTime.val(formatSeconds(getElapsedTime()));
  committedTime.attr("uncommitted", true);

  committedTime.removeClass("committedTime");
  committedTime.addClass("uncommittedTime");
}

function createResult(seconds_elapsed, is_recording, committed_time)
{
    var obj = new Object();
    obj.seconds_elapsed = seconds_elapsed;
    obj.is_recording = is_recording;
    obj.committed_time = committed_time;
    return obj;
}

function startRecording(recordButton)
{
    if (!recordButton.disabled)
    {
        getJSON("../../start_record", null, false, startRecordingOnComplete, startRecordingOnError);
    }
}

function startRecordingOnComplete(status)
{
    var result = createResult(0, String.isNullOrEmpty(status.error), getCommittedTime());

    if (result.is_recording)
    {
        handleResult(result);
        displayStatusMessage("Recording successfully started", false);
    }
    else
    {
        displayStatusMessage("Unable to start recording: " + status.error, true);
    }
}

function startRecordingOnError(xmlHttpRequest, status, errorThrown)
{
    displayStatusMessage("Unable to start recording: " + errorThrown, true);
}

function stopRecording(stopButton)
{
    if (!stopButton.disabled)
    {
        getJSON("../../stop_record", null, false, stopRecordingOnComplete, stopRecordingOnError);
    }
}

function stopRecordingOnComplete(result)
{
    if (!result.is_recording)
    {
        handleResult(result);
        displayStatusMessage("Recording successfully stopped", false);
    }
}

function stopRecordingOnError(xmlHttpRequest, status, errorThrown)
{
    displayStatusMessage("Unable to stop recording: " + errorThrown, true);    
}

function getElapsedTime()
{
    return Number($("#elapsedTime").val());
}

function setElapsedTime(seconds)
{
    var elapsed = $("#elapsedTime")
    elapsed.text(formatSeconds(seconds));
    elapsed.val(seconds);
}

var g_elapsedTimeInterval;
function beginIncrementingElapsedTime()
{

    stopIncrementingElapsedTime();
    //setElapsedTime(getElapsedTime++);
    g_elapsedTimeInterval = window.setInterval(function () { setElapsedTime(getElapsedTime() + 1); }, 1000);
}

function stopIncrementingElapsedTime()
{
    if (g_elapsedTimeInterval)
    {
        window.clearInterval(g_elapsedTimeInterval);
    }

    g_elapsedTimeInterval = null;
}

function getCommittedTime()
{
    return unformatSeconds($("#committedTime").val());
}

function setCommittedTime(seconds)
{
    var committedTime = $("#committedTime");
    if (!committedTime.attr("uncommitted") && !committedTime.attr("locked"))
    {
        committedTime.val(formatSeconds(seconds));
    }
}

function getDuration()
{
    return $("#duration").val();
}

var g_statusInterval;
function beginCheckingStatus()
{
    stopCheckingStatus();
    g_statusInterval = window.setInterval(checkStatus, 5000);
}

function stopCheckingStatus()
{
    if (g_statusInterval)
    {
        window.clearInterval(g_statusInterval);
    }

    g_statusInterval = null;
}

function checkStatus(onCompleteCallback)
{
    getJSON("../../get_record_status", null, true, function (data) { checkStatusOnComplete(data, onCompleteCallback); }, checkStatusOnError);
}

function checkStatusOnComplete(data, callback)
{
    if (String.isNullOrEmpty(data.error))
    {
        handleResult(data);
        if (callback != null && typeof (callback) == "function")
        {
            callback();
        }
    }
    else
    {
        displayStatusMessage("Unable to retrieve record status from server: " + errorThrown, true);
    }
}

var savedResult = null;
function handleResult(result)
{
    setElapsedTime(result.seconds_elapsed);
    setCommittedTime(result.committed_time);
    var isRecording = savedResult == null ? null : savedResult.is_recording;

    if (result.is_recording != isRecording)
    {
        if (result.is_recording)
        {
            disableButton("record");
            enableButton("stop");
            enableButton("preview");
            enableButton("save");
            beginCheckingStatus();
            beginIncrementingElapsedTime();
        }
        else
        {
            enableButton("record");
            disableButton("stop");

            if (result.seconds_elapsed > 0)
            {
                enableButton("preview");
                enableButton("save");
            }
            else
            {
                disableButton("preview");
                disableButton("save");
            }
            stopCheckingStatus();
            stopIncrementingElapsedTime();
        }
    }

    savedResult = result;
}

function checkStatusOnError(xmlHttpRequest, status, errorThrown)
{
    displayStatusMessage("Unable to retrieve record status from server: " + errorThrown, true);
}

var maxTimes = new Array();
maxTimes.push(60, 60, 24);
function validateParts(parts)
{
    var isValid = true;

    for (var i = 0; i < parts.length; i++)
    {
        if (parts[parts.length - i] >= maxTimes[i])
        {
            isValid = false;
            break;
        }
    }

    return isValid;
}

function joinParts(parts)
{
    return formatSeconds(unformatSeconds(parts.join(":")));
}

function validateSeconds(seconds)
{
    var parts = seconds.split(":");
    var newParts = parts;

    if (parts.length == 1)
    {
        var enteredValue = parts[0];

        if (enteredValue >= 60 && enteredValue < 100)
        {
            newParts = formatSeconds(enteredValue).split(":");
        }
        else
        {
            newParts = new Array();

            for (var i = 0; i < enteredValue.length / 2; i++)
            {
                var length = 2;
                var totalLength = (i + 1) * 2;
                if (totalLength > enteredValue.length)
                {
                    length = 1;
                }

                var startPos = Math.max(0, enteredValue.length - totalLength);

                newParts.push(enteredValue.substring(startPos, startPos + length));
            }

            newParts.reverse();
        }
    }

    return { "isValid": validateParts(newParts), "value": joinParts(newParts) };
}

function formatSeconds(seconds)
{
    var remainingSeconds = seconds % 60;
    var minutes = Math.floor(seconds / 60);
    var remainingMinutes = minutes % 60;
    var hours = Math.floor(minutes / 60);

    var textMinutes = remainingMinutes < 10 ? "0" + remainingMinutes : remainingMinutes;
    var textSeconds = remainingSeconds < 10 ? "0" + remainingSeconds : remainingSeconds;
    return hours + ":" + textMinutes + ":" + textSeconds;
}

function unformatSeconds(formattedTime)
{
    var parts = formattedTime.split(":");
    var factors = new Array();
    factors.push(1, 60, 3600);

    var seconds = 0;

    for (var i = 0; i < parts.length; i++)
    {
        seconds += parts[parts.length - 1 - i] * factors[i];
    }

    return seconds;
}

function previewPlayback(playButton)
{
    if (!playButton.disabled)
    {
        var params = new Array();
        params.push(getCommittedTime());

        var duration = getDuration();
        if (duration > 0)
        {
            params.push(duration);
        }

        getJSON("../../play_preview", params, true, previewPlaybackOnComplete, previewPlaybackOnError);
    }
}

function previewPlaybackOnComplete(status)
{
    if (String.isNullOrEmpty(status.error))
    {
        displayStatusMessage("Preview started successfully", false);
    }
    else
    {
        displayStatusMessage("Error starting preview: " + status.error, true);
    }
}

function previewPlaybackOnError(xmlHttpRequest, status, errorThrown)
{
    displayStatusMessage("Error starting preview: " + errorThrown, true);
}

function saveStartTime(saveButton)
{
    if (!saveButton.disabled)
    {
        var params = new Array();
        params.push(getCommittedTime());

        getJSON("../../commit_time", params, true, saveStartTimeOnComplete, saveStartTimeOnError);
    }
}

function saveStartTimeOnComplete(status)
{
    if (String.isNullOrEmpty(status.error))
    {
        commitTime("committedTime");
        displayStatusMessage("Start time saved successfully", false);
    }
    else
    {
        displayStatusMessage("Error saving start time: " + status.error, true);
    }
}

function saveStartTimeOnError(xmlHttpRequest, status, errorThrown)
{
    displayStatusMessage("Error saving start time: " + errorThrown, true);
}

function onFocus(inputControl)
{
    var thisJQuery = $("#" + inputControl.id);
    thisJQuery.removeClass("committedTime");
    thisJQuery.addClass("uncommittedTime");
    thisJQuery.attr("storedValue", thisJQuery.val());
    thisJQuery.attr("locked", true);
    thisJQuery.val("");
}

function commitTime(id)
{
    var thisJQuery = $("#" + id);
    thisJQuery.removeAttr("uncommitted");
    thisJQuery.removeClass("uncommittedTime");
    thisJQuery.addClass("committedTime");
}

function onBlur(inputControl)
{
    var thisJQuery = $("#" + inputControl.id);
    var currentValue = thisJQuery.val();
    var formatted = validateSeconds(currentValue);
    var storedValue = thisJQuery.attr("storedValue");
    thisJQuery.removeAttr("storedValue");
    thisJQuery.removeAttr("locked");

    if (!formatted.isValid)
    {
        handleInvalid(inputControl);
        currentValue = "";
    }
    if (String.isNullOrEmpty(currentValue) || formatted.value == storedValue)
    {
        thisJQuery.val(storedValue);
        if (!thisJQuery.attr("uncommitted"))
        {
            commitTime(inputControl.id);
        }
    }
    else
    {
        thisJQuery.val(formatted.value);
        thisJQuery.attr("uncommitted", true);
    }
}


function handleInvalid(inputControl)
{
    alert("Invalid time");
}
