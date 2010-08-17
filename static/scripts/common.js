String.isNullOrEmpty = function (value)
{
    return (value == null || value == "");
}

function toggleButton(button, targetState)
{
    if (!button.disabled)
    {
        var targetSrc = button.getAttribute(targetState + "src");
        button.src = targetSrc;
    }
}

function toggleButtonOnEvent(targetState)
{
    var button = event.srcElement;
    toggleButton(button, targetState);
}

function disableButton(buttonId)
{
    var button = $("#" + buttonId)[0];
    toggleButton(button, "disabled");
    button.disabled = true;
}

function enableButton(buttonId)
{
    var button = $("#" + buttonId)[0];
    button.disabled = false;
    toggleButton(button, "normal");
}

function buttonOnMouseOver()
{
    toggleButtonOnEvent("onmouseover");
}

function buttonOnMouseOut()
{
    toggleButtonOnEvent("normal");
}

function buttonOnMouseDown()
{
    toggleButtonOnEvent("onmousedown");
}

function buttonOnMouseUp()
{
    toggleButtonOnEvent("normal");
}

function getJSON(url, params, isAsync, successCallback, errorCallback)
{
    if (isAsync == null)
    {
        isAsync = true;
    }

    if (params != null && params.length > 0)
    {
        for (var i = 0; i < params.length; i++)
        {
            url += "/" + params[i];
        }
    }

    return $.ajax({
        type: "GET",
        url: url,
        success: function (data) { OnComplete(data, successCallback); },
        error: errorCallback,
        dataType: "json",
        async: isAsync
    });
}

function displayStatusMessage(message, isError, leaveOnScreen)
{
    var statusPanel = $("#statusPanel");
    statusPanel.text(message);
    var body = $("body");
    var windowWidth = body.innerWidth();
    var statusWidth = statusPanel.outerWidth();

    statusPanel.css("position", "absolute");
    statusPanel.css("top", body.scrollTop());
    statusPanel.css("left", (windowWidth - statusWidth) / 2);

    if (isError)
    {
        statusPanel.addClass("statusError");
    }
    else
    {
        statusPanel.removeClass("statusError");
    }

    var callback;

    if (!leaveOnScreen)
    {
        callback = hideStatusMessage;
    }

    statusPanel.fadeIn(2000, callback);
    //window.setTimeout(function () { alert(message); }, 500);
}

function hideStatusMessage()
{
    $("#statusPanel").fadeOut(2000, function () { $("#statusPanel").text(""); });
}
function OnComplete(data, callback)
{
    try
    {
        callback(data);
    }
    catch (e)
    {
        var message;
        if (e.description)
        {
            message = e.description;
        }
        else
        {
            message = e;
        }
        
        displayStatusMessage("Error:" + message, true, true);
    }
}

function addOption(list, option)
{
    try
    {
        list.add(option, null);
    }
    catch (e)
    {
        list.add(option);
    }
}
