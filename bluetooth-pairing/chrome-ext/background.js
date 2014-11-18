chrome.app.runtime.onLaunched.addListener(function() {
  chrome.app.window.create('popup.html', {
    id: "window1",
    bounds: {
      width: 640,
      height: 480
    }
  });
});