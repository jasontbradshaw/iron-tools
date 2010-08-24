var sortedResult;
var newSelection = false;

function createElement(tag, id, className, text, value)
{
	//var ui = new UI();
	
	var element = $("<" + tag + "/>");

	if (!String.isNullOrEmpty(id))
	{
		element.attr("id", id);
	}

	element.addClass(className);

	if (!String.isNullOrEmpty(text))
	{
		element.text(text);
	}

	if(!String.isNullOrEmpty(value))
	{
		element.val(value);
	}
	return element;
}

function getStartTimeMessage(startTime)
{
	var startTimeMessage = startTime ? startTime : "Not Received";
	return "Start Time: " + startTimeMessage;
}

function getFileSizeMessage(fileSize)
{
	return "File Size: " + getFileSize(fileSize) + " MB";
}

function createListItem(filename)
{
	var element = createElement("div", getNormalizedFilename(filename), "videoItem");
	element.hover(function () { element.addClass("highlight"); }, function () { element.removeClass("highlight"); });
	element.mousedown(function ()
	{
		clearSelectedOptions();
		clearLoadedOptions();
		element.addClass("selected");
	});
	element.click(function () { loadVideo(element); });
	return element;
}

function createOrUpdateListItem(item)
{
	var element = $("#" + getNormalizedFilename(item.filename));

	if (element.length == 0)
	{
		element = createListItem(item.filename);
	}
	else
	{
		$("*", element).remove();
	}

	element.append(createElement("div", null, "filename", item.filename, item.filename));
	var startTimeStyle = item.start_time ? "" : "startTimeMissing ";
	startTimeStyle = startTimeStyle + "startTime";

  if(item.start_time == null) {
  }
	element.append(createElement("div", null, startTimeStyle, getStartTimeMessage(item.start_time), ""));
	element.append(createElement("div", null, "fileSize", getFileSizeMessage(item.file_size), item.file_size));
	return element;
}

function getSelectedItem()
{
	return $(".selected");
}

function getSelectedItemStartTime()
{
	var selectedItem = getSelectedItem();
	var startTime = $(".startTime", selectedItem).val();
	return startTime == "true";
}

function getSelectedItemFileName()
{
	var selectedItem = getSelectedItem();
	var filename = $(".fileName", selectedItem).val();
	return filename;
}


function populateFileList(data)
{
	data.sort(fileSorter);
	var list = $("#videoListContainer");

	//addOption(list, createOption("", ""));
	list.text = "";

	if (data.length == 0 && list.children().length == 0)
	{
		list.append(createElement("div", "filename", "filename", "No videos are available for playback"));
	}
	else
	{
		var i;
		var selectedItemStart = getSelectedItemStartTime();

		for (i = 0; i < data.length; i++)
		{
			list.prepend(createOrUpdateListItem(data[i]));
			
//			var option = addOrUpdateListItem(data[i].filename, data[i].start_time_received, fileSize);
//			list.append(option);

			//var option = createOption(data[i].filename, data[i].filename + " - " + startTime + " - " + getFileSize(data[i].file_size) + " MB");
			// addOption(list, option);
		}

		var index = i - 1;
		$(".videoItem:gt(" + index + ")", list).remove();

		if (selectedItemStart != getSelectedItemStartTime())
		{
			loadVideo($(".selected"));
		}
//		for (var j = list.children()..length - 1; j >= i; j--)
//		{
//			list.children().re
//		}
	}



	//var junk = list.children().sort(listItemSorter);

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
}

function fileSorter(fileA, fileB)
{
	if (fileA.filename > fileB.filename)
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

//function listItemSorter(item1, item2)
//{
//	var itemName1 = $(".filename",$(item1)).text();
//	var itemName2 = $(".filename", $(item2)).text();

//	if (itemName1 < itemName2)
//	{
//		return 1;
//	}
//	else if (itemName1 == itemName2)
//	{
//		return 0;
//	}
//	else
//	{
//		return -1;
//	}
//}

function getFileList(callback)
{
	getJSON("../../get_file_list", null, true, function (data) { getFileListOnComplete(data, callback); }, getFileListOnError);
}


function getFileListOnComplete(data, callback)
{
	if (String.isNullOrEmpty(data.error))
	{
		populateFileList(data.file_list);

		if ($(".selected|.loaded").length == 0)
		{
			videoListOnChange();
		}

		if (callback != null && typeof (callback) == "function")
		{
			callback();
		}
	}
	else
	{
		displayStatusMessage("Unable to retrieve file list: " + data.error, true);
	}
}

function videoListOnChange()
{
	//   enableButton("load");
	disableButton("play");
	disableButton("stop");
}

function getFileListOnError(xmlHttpRequesget, status, errorThrown)
{
	displayStatusMessage("Unable to retrieve file list: " + errorThrown, true);
}

function loadVideo(option)
{
	var selectedOption = $(".filename", option).text();
	var startTime = getSelectedItemStartTime();
	newSelection = true;

	if (startTime)
	{
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
		//disableButton("load");
		disableButton("play");
		disableButton("stop");
		displayStatusMessage("Video is loading", false);
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
		//disableButton("load");
		disableButton("play");
		enableButton("stop");
		//$("#videoList")[0].disabled = true;
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
		// enableButton("load");
		disableButton("play");
		disableButton("stop");
		//$("#videoList")[0].disabled = false;
		clearLoadedOptions();
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

var g_statusId;

function stopCheckingStatus()
{
	if (g_statusId)
	{
		window.clearInterval(g_statusId);
	}
}

function beginCheckingStatus()
{
	stopCheckingStatus();
	g_statusId = window.setInterval(getStatus, 1000);
}

var g_FileListId;

function stopCheckingFileList()
{
	if (g_FileListId)
	{
		window.clearInterval(g_FileListId);
	}
}

function beginCheckingFileList()
{
	stopCheckingStatus();
	g_FileListId = window.setInterval(getFileList, 10000);
}

function getStatus(callback)
{
	getJSON("../../get_status", null, true, function (data) { getStatusOnComplete(data, callback); }, getStatusOnError);
}

function getStatusOnComplete(status, callback)
{
	if (String.isNullOrEmpty(status.error))
	{
		if (!String.isNullOrEmpty(status.file))
		{
			//disableButton("load");
			if (newSelection && (status.file == getSelectedItemFileName()))
			{
				newSelection = false;
				if (selectLoadedOption(status.file))
				{
					if (status.is_playing)
					{
						disableButton("play");
						enableButton("stop");
					}
					else
					{
						disableButton("stop");
						enableButton("play");
					}
				}
				else
				{
					videoListOnChange();
				}
			}
		}

		if (callback != null && typeof (callback) == "function")
		{
			callback();
		}
	}
}

function getStatusOnError(xmlHttpRequest, status, errorThrown)
{
	var junk = status;
}

function getNormalizedFilename(filename)
{
	//var regex = new RegExp("\[.]*");
	var replaced = filename.replace(/[.:]/g, "");
	return replaced;
}

function selectLoadedOption(filename)
{
	var option = $("#" + getNormalizedFilename(filename));
	clearSelectedOptions();
	//option.removeClass("selected");
	option.addClass("loaded");
	return option.length > 0;
}

function clearSelectedOptions()
{
	$(".selected").each(function (index, item) { $(this).removeClass("selected"); });
}

function clearLoadedOptions()
{
	$(".loaded").each(function (index, item) { $(this).removeClass("loaded"); });

}

function initialize()
{
	var checkStatusCallback = function ()
	{
		$("#bodyPanel").fadeIn(1000);
		beginCheckingStatus();
	}

	var getFileListCallback = function ()
	{
		getStatus(checkStatusCallback);
		beginCheckingFileList();
	}
	getFileList(getFileListCallback);
}
