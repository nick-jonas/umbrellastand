var DEVICE_ADDRESS = '00:02:72:D6:A4:8C';

var App = function(){
  
  var self = this;
  var isDiscovering = false;
  var $spinner = $('.spinner');
  var $findDeviceButton = $('.find-device');
  var bl = new Bluetooth(DEVICE_ADDRESS);


  $findDeviceButton.click(function(e){
    e.preventDefault();
    
    if(isDiscovering) return;
    isDiscovering = true;
    
    $('.spinner').css('display', 'block');

    bl.startDiscovery();
  });
  
};



$(document).ready(function(){
  var myApp = new App();
});




function ab2str(buf) {
  return String.fromCharCode.apply(null, new Uint16Array(buf));
}

function str2ab(str) {
  var buf = new ArrayBuffer(str.length*2); // 2 bytes for each char
  var bufView = new Uint16Array(buf);
  for (var i=0, strLen=str.length; i<strLen; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf;
}