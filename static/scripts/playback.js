var $PlaybackUI = new PlaybackUI(new Playback());

$("body").ready($PlaybackUI.onReady);

function PlaybackUI(playback)
{
  var _playback = playback;
  var SELECTED = "selected";
  var LOADED = "loaded";
  var HIGHLIGHT = "highlight";

  var _files;
  var _newSelection = false;

  this.onReady = function ()
  {
    _playback.video_onAdd.add(addVideoItem);
    _playback.video_onRemove.add(deleteVideoItem);
    _playback.selectedVideo.onChange.add(selectVideoItem);

    $("#play").click(
      function ()
      {
        if (!this.disabled) { _playback.playVideo(); }
      });

    $("#stop").click(
      function ()
      {
        if (!this.disabled) { _playback.stopVideo(); }
      });

      disableButton("stop");
      disableButton("play");

      _playback.beginCheckingFileList(function ()
      {
        _playback.beginCheckingStatus(function ()
        {
          $("#bodyPanel").fadeIn(1000);
        });
      });
  }

  var createElement = function (tag, id, className)
  {
    var element = $("<" + tag + "/>");

    if (!String.isNullOrEmpty(id))
    {
      element.attr("id", id);
    }

    element.addClass(className);

    return element;
  }

  var getElementFileName = function (element)
  {
    return $(".filename", element).text();
  }

  var getVideoItem = function (filename)
  {
    return $("#" + getNormalizedFilename(filename));
  }

  var getVideoList = function ()
  {
    return $("#videoListContainer");
  }

  var addVideoItem = function (video)
  {
    var item = createVideoItem(video);
    var list = getVideoList();
    var children = list.children();
    var inserted = false;

    for (var i = 0; i < children.length; i++)
    {
      if (video.fileName() > getElementFileName(children[i]))
      {
        item.insertBefore(children[i]);
        inserted = true;
        break;
      }
    }

    if (!inserted)
    {
      list.append(item);
    }
  }

  var createVideoItem = function (video)
  {
    var videoItem = createElement("div", getNormalizedFilename(video.fileName()), "videoItem");
    videoItem.hover(function () { videoItem.addClass("highlight"); }, function () { videoItem.removeClass("highlight"); });
    videoItem.click(function () { _playback.selectedVideo.set(video); });
    video.isLoaded.onChange.add(
      function (args)
      {
        if (args.value)
        {
          enableButton("play");
          videoItem.addClass("loaded");
        }
        else
        {
          disableButton("play");
          videoItem.removeClass("loaded");
        }
      });

    video.isPlaying.onChange.add(
      function (args)
      {
        if (args.value)
        {
          disableButton("play");
          enableButton("stop");
        }
        else
        {
          disableButton("stop");
        }
      }
    );

    var fileName = createElement("div", null, "filename");
    fileName.text(video.fileName());

    videoItem.append(fileName);

    var startTimeElement = createElement("div", null, "startTime");
    startTimeElement.text(getStartTimeMessage(video.startTime.get()));
    if (video.startTime.get() == null)
    {
      startTimeElement.addClass("startTimeMissing");
    }

    video.startTime.onChange.add(
      function (args)
      {
        startTimeElement.text(getStartTimeMessage(args.value));

        if (args.value != null)
        {
          startTimeElement.removeClass("startTimeMissing");
        }
        else
        {
          startTimeElement.addClass("startTimeMissing");
        }
      });

    videoItem.append(startTimeElement);

    var fileSizeElement = createElement("div", null, "fileSize");
    fileSizeElement.text(getFileSizeMessage(video.size.get()));

    video.size.onChange.add(
      function (args)
      {
        fileSizeElement.text(getFileSizeMessage(args.value));
      });

    videoItem.append(fileSizeElement);

    return videoItem;
  }

  var deleteVideoItem = function (video)
  {
    var list = getVideoList();
    list.remove(getVideoItem(video.fileName()));
  }

  var selectVideoItem = function (args)
  {
    var video = args.value
    var previousVideo = args.previousValue;

    if (previousVideo != null)
    {
      var currentlySelected = getVideoItem(previousVideo.fileName());
      currentlySelected.removeClass("selected");
      currentlySelected.removeClass("loaded");
    }

    disableButton("stop");
    disableButton("play");

    if (video != null)
    {
      getVideoItem(video.fileName()).addClass("selected");
      if (video.isPlaying.get())
      {
        enableButton("stop");
      }
      else if (video.isLoaded.get())
      {
        enableButton("play");
      }
    }
  }
}

//END UI

//BEGIN CONTROLLER

function Playback()
{
  var STATUS_INTERVAL = 1000;
  var FILELIST_INTERVAL = 5000;
  var _statusId;
  var _fileListId;

  var _selectedVideo = new Property(null);
  var _previousVideo = new Property(null);

  var _videoList = new Array();
  var _fileNameLookup = new Array();

  var _video_onAdd = new Event();
  var _video_onRemove = new Event();

  this.selectedVideo = _selectedVideo;

  var selectedVideoOnChange = function (args)
  {
    _previousVideo.set(args.previousValue);

    var video = args.value;

    if (video != null)
    {
      if (video.startTime.get() != null && !video.isLoaded.get())
      {
        loadVideo(video);
      }

      video.startTime.onChange.add(loadSelectedVideo);
    }
  }

  _selectedVideo.onChange.add(selectedVideoOnChange);

  var previousVideoOnChange = function (args)
  {
    var oldPreviousVideo = args.previousValue;
    if (oldPreviousVideo != null)
    {
      oldPreviousVideo.isLoaded.set(false);
    }

    var previousVideo = args.value;
    if (oldPreviousVideo != null)
    {
      oldPreviousVideo.startTime.onChange.remove(loadSelectedVideo);
    }
  }

  _previousVideo.onChange.add(previousVideoOnChange);

  var updateVideoList = function (videoArray)
  {
    var processedFiles = new Array();

    for (var i = 0; i < videoArray.length; i++)
    {
      var currentVideo = videoArray[i];

      processedFiles[currentVideo.filename] = currentVideo;

      var video = _videoList[currentVideo.filename];

      if (video != null)
      {
        video.startTime.set(currentVideo.start_time);
        video.size.set(currentVideo.file_size);
      }
      else
      {
        video = new Video(currentVideo.filename, currentVideo.start_time, currentVideo.file_size);
        _videoList[currentVideo.filename] = video;
        _video_onAdd.fire(video);
      }
    }

    for (var key in _videoList)
    {
      var currVideo = _videoList[key];
      if (currVideo instanceof Video)
      {
        if (processedFiles[currVideo.fileName()] == null)
        {
          delete _videoList[currVideo.fileName()];
          _video_onRemove.fire(currVideo);
        }
      }
    }
  }

  this.video_onAdd = _video_onAdd;
  this.video_onRemove = _video_onRemove;


  var getFileList = function (callback)
  {
    getJSON("../../get_file_list", null, true, function (data) { getFileListOnComplete(data, callback); }, getFileListOnError);
  }

  var getFileListOnComplete = function (data, callback)
  {
    if (String.isNullOrEmpty(data.error))
    {
      updateVideoList(data.file_list);

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

  var getFileListOnError = function (xmlHttpRequesget, status, errorThrown)
  {
    displayStatusMessage("Unable to retrieve file list: " + errorThrown, true);
  }

  var getStatus = function (callback)
  {
    getJSON("../../get_status", null, true, function (data) { getStatusOnComplete(data, callback); }, getStatusOnError);
  }

  var selectVideo = function (video, isPlaying)
  {
    _previousVideo.set(null);
    if (video)
    {
      video.isLoaded.set(true);
      video.isPlaying.set(isPlaying);
    }
    _selectedVideo.set(video);
  }

  var getStatusOnComplete = function (status, callback)
  {
    if (String.isNullOrEmpty(status.error))
    {
      var video;

      video = _videoList[status.file];
      var selected = _selectedVideo.get();

      if (selected != null)
      {
        if (video != null)
        {
          if (video == selected)
          {
            selectVideo(video, status.is_playing);
          }
          else if (video != selected && video != _previousVideo.get())
          {
            selectVideo(video, status.is_playing);
          }
        }
      }
      else
      {
        selectVideo(video, status.is_playing);
      }

      if (callback != null && typeof (callback) == "function")
      {
        callback();
      }
      else
      {
        displayStatusMessage("Unable to get playback status: " + status.error, true);
      }
    }
  }

  var getStatusOnError = function (xmlHttpRequest, status, errorThrown)
  {
  }

  var loadSelectedVideo = function (args)
  {
    var video = _selectedVideo.get();

    if (!video.isPlaying.get())
    {
      video.isLoaded.set(false);
      loadVideo(video);
    }
  }

  var loadVideo = function (video)
  {
    var params = new Array();
    params.push(video.fileName());
    getJSON("../../arm", params, true, loadVideoOnComplete, loadVideoOnError);
  }

  var loadVideoOnComplete = function (status)
  {
    if (String.isNullOrEmpty(status.error))
    {
      displayStatusMessage("Video is loading", false);
    }
    else
    {
      displayStatusMessage("Unable to load video: " + status.error, true);
    }
  }

  var loadVideoOnError = function (xmlHttpRequest, status, errorThrown)
  {
    displayStatusMessage("Unable to load video: " + errorThrown, true);
  }

  this.beginCheckingStatus = function (callback)
  {
    if (_statusId)
    {
      window.clearInterval(_statusId);
    }

    getStatus(callback);

    _statusId = window.setInterval(getStatus, STATUS_INTERVAL);
  }

  this.beginCheckingFileList = function (callback)
  {
    if (_fileListId)
    {
      window.clearInterval(_fileListId);
    }

    getFileList(callback);

    _fileListId = window.setInterval(getFileList, FILELIST_INTERVAL);
  }


  this.playVideo = function ()
  {
    getJSON("../../play", null, true, playVideoOnComplete, playVideoOnError);
  }

  var playVideoOnComplete = function (status)
  {
    if (String.isNullOrEmpty(status.error))
    {
      displayStatusMessage("Video playback started successfully", false);
    }
    else
    {
      displayStatusMessage("Unable to start video playback: " + status.error, true);
    }
  }

  var playVideoOnError = function (xmlHttpRequest, status, errorThrown)
  {
    displayStatusMessage("Unable to start video playback: " + errorThrown, true);
  }

  this.stopVideo = function ()
  {
    getJSON("../../stop", null, true, stopVideoOnComplete, stopVideoOnError);
  }

  function stopVideoOnComplete(status)
  {
    if (String.isNullOrEmpty(status.error))
    {
      _selectedVideo.set(null);
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

}

//END CONTROLLER

//BEGIN MODEL

function Video(fileName, startTime, size)
{
  var _fileName = fileName;

  this.size = new Property(size);
  this.isLoaded = new Property(false);
  this.isPlaying = new Property(false);
  this.startTime = new Property(startTime);

  this.fileName = function ()
  {
    return _fileName;
  }
}

function Event()
{
  var _handlers = new Array();

  this.add = function (func)
  {
    if (typeof (func) == "function" && _handlers.indexOf(func) == -1)
    {
      _handlers.push(func);
    }
  }

  this.remove = function (func)
  {
    var index = _handlers.indexOf(func)
    if (index != -1)
    {
      _handlers.splice(index, 1);
    }
  }

  this.fire = function (args)
  {
    for (var i = 0; i < _handlers.length; i++)
    {
      _handlers[i](args);
    }
  }
}


function Property(value)
{
  var _value = value;

  this.onChange = new Event();

  this.get = function()
  {
    return _value;
  }

  this.set = function(value)
  {
    var currValue = _value;
    _value = value;

    if (currValue != value)
    {
      this.onChange.fire({ "value": value, "previousValue": currValue });
    }
  }
}

//END MODEL

function getStartTimeMessage(startTime)
{ 
  var startTimeMessage = startTime != null ? formatSeconds(startTime) : "Not Received";
  return "Start Time: " + startTimeMessage;
}

function getFileSizeMessage(fileSize)
{
  return "File Size: " + getFileSize(fileSize) + " MB";
}

function getFileSize(bytes)
{
  return Math.roundTo(bytes / 1024 / 1024, 2);
}

function getNormalizedFilename(filename)
{
  var replaced = filename.replace(/[.:]/g, "");
  return replaced;
}




