isNullOrEmpty = function (value)
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
        success: successCallback,
        error: errorCallback,
        dataType: "json",
        async: isAsync
    });
}
