// run this on the RPi: 
// $: hciconfig | grep "BD Address"
var DEVICE_ADDRESS = '00:02:72:D6:A4:8C';
var socketId = null;

var App = function(){
  
  var self = this;
  var isDiscovering = false;
  var $spinner = $('.spinner');
  var $findDeviceButton = $('.find-device');

  chrome.bluetooth.getAdapterState( function( result ) {
    if (result) {
      console.log(result);
    } else {
      console.log(chrome.runtime.lastError);
    }
  });

  // $findDeviceButton.click(function(){
  //   if(isDiscovering) return;
  //   isDiscovering = true;
  //   $('.spinner').css('display', 'block');
  //   self.findDevices();
  // });

  var device_names = {};
  var updateDeviceName = function(device) {
    if(typeof device_names[device.address] === 'undefined'){
      getDevices();
      if(device.address === DEVICE_ADDRESS){
        connectSocket(device);
      }
    }
    device_names[device.address] = device.name;
  };
  var removeDeviceName = function(device) {
    delete device_names[device.address];
  }

  // Add listeners to receive newly found devices and updates
  // to the previously known devices.
  chrome.bluetooth.onDeviceAdded.addListener(updateDeviceName);
  chrome.bluetooth.onDeviceChanged.addListener(updateDeviceName);
  chrome.bluetooth.onDeviceRemoved.addListener(removeDeviceName);

  // Now begin the discovery process.
  chrome.bluetooth.startDiscovery(function() {
    // Stop discovery after 30 seconds.
    setTimeout(function() {
      chrome.bluetooth.stopDiscovery(function() {});
    }, 30000);
  });


  function getDevices(){
    // With the listeners in place, get the list of devices found in
    // previous discovery sessions, or any currently active ones,
    // along with paired devices.
    chrome.bluetooth.getDevices(function(devices) {
      console.dir(devices);
      for (var i = 0; i < devices.length; i++) {
        updateDeviceName(devices[i]);
        console.log(devices[i].address + ' = ' +
                    devices[i].vendorIdSource + ':' +
                    devices[i].vendorId.toString(16) + ':' +
                    devices[i].productId.toString(16) + ':' +
                    devices[i].deviceId.toString(16));
      }
    });
  }

  getDevices();

  uuid = '1101';
  
  function connectSocket(device){
    console.log('create bluetooth socket...');
    chrome.bluetoothSocket.create(function(createInfo) {
      // console.log(createInfo.socketId, device.address, uui);
      console.log('attempting socket connection...');
      socketId = createInfo.socketId;
      chrome.bluetoothSocket.connect(createInfo.socketId, device.address, uuid, onConnectedCallback);
    
      chrome.bluetoothSocket.onAccept.addListener(function(acceptInfo) {
        if (info.socketId != createInfo.socketId)
          return;

        console.log('accepted socket connection!');
        console.log('sending message to RPi...');
        // Say hello...
        chrome.bluetoothSocket.send(acceptInfo.clientSocketId, 'hi', onSendCallback);

        // Accepted sockets are initially paused,
        // set the onReceive listener first.
        chrome.bluetoothSocket.onReceive.addListener(onReceive);
        chrome.bluetoothSocket.setPaused(false);
      });

      chrome.bluetoothSocket.listenUsingRfcomm(createInfo.socketId, uuid, function() {
        if (chrome.runtime.lastError) {
          console.log("Connection failed: " + chrome.runtime.lastError.message);
        }
      });

      chrome.bluetoothSocket.onReceiveError.addListener(function(info){
        console.dir(info);
      });

    });
  }

  var onReceive = function(receiveInfo){
    console.log("Received " + receiveInfo.data.byteLength + " bytes");
    var bytes = new Uint8Array(receiveInfo.data);
    console.log("buffer = " + JSON.stringify(bytes));
  }

  var onConnectedCallback = function() {
    console.log('on socket connected callback...');
    if (chrome.runtime.lastError) {
      console.log("Connection failed: " + chrome.runtime.lastError.message);
    } else {
      console.log('success!');
      chrome.bluetoothSocket.send(socketId, str2ab('ssid:peterpounders'), function(bytesSent){
        console.log('sent ssid: ' + bytesSent + ' bytes (max = 128)');
      });
      chrome.bluetoothSocket.send(socketId, str2ab('pass:0123456789'), function(bytesSent){
        console.log('sent pass: ' + bytesSent + ' bytes (max = 128)');
      });
      // Profile implementation here.
    }
  };


};



$(document).ready(function(){
  var myApp = new App();
});


// Logs debug messages to app window
function log(msg) {
  var msg_str = (typeof(msg) == 'object') ? JSON.stringify(msg) : msg;
  console.log(msg_str);
  var l = document.getElementById('log');
  if (l) {
    l.innerText += msg_str + '\n';
  }
}


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