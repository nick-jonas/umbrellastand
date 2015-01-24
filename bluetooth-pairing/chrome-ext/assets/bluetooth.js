/*------------------------------------------------------
  
Written by: Nick Jonas

Bluetooth takes care of setup for bluetooth socket
using the SPP (Serial Port Profile) with a RPi and
a Chrome App, based on the API found here:

https://developer.chrome.com/apps/bluetoothSocket

To find your device address, plug in an adaptor & run the following on your Pi:

$ hciconfig | grep "BD Address"

------------------------------------------------------*/

var Bluetooth = function(deviceAddress){

    this.uuid = '1101'; // SPP Profile
    this.addr = deviceAddress;
    this.isDiscovering = false;
    this.deviceNames = {};
    this.socketId = null;
    this.init();
};

Bluetooth.prototype.init = function() {
  chrome.bluetooth.getAdapterState( function( result ) {
    if (result) {
      console.log(result);
    } else {
      console.log(chrome.runtime.lastError);
    }
  });
  
  // Add listeners to receive newly found devices and updates
  // to the previously known devices.
  chrome.bluetooth.onDeviceAdded.addListener($.proxy(this.updateDeviceName, this));
  chrome.bluetooth.onDeviceChanged.addListener($.proxy(this.updateDeviceName, this));
  chrome.bluetooth.onDeviceRemoved.addListener($.proxy(this.removeDeviceName, this));

  // show current devices
  this.getDevices();
  this.startDiscovery();
};

Bluetooth.prototype.startDiscovery = function() {
  chrome.bluetooth.startDiscovery(function() {
    // Stop discovery after 30 seconds.
    setTimeout(function() {
      chrome.bluetooth.stopDiscovery(function() {});
    }, 30000);
  });
};

Bluetooth.prototype.updateDeviceName = function(device) {
  if(typeof this.deviceNames[device.address] === 'undefined'){
    this.getDevices();
    if(device.address === this.addr){
      this.connectSocket(device);
    }
  }
  this.deviceNames[device.address] = device.name;
};

Bluetooth.prototype.removeDeviceName = function(device) {
  delete this.deviceNames[device.address];
};

// With the listeners in place, get the list of devices found in
// previous discovery sessions, or any currently active ones,
// along with paired devices.
Bluetooth.prototype.getDevices = function() {
  var self = this;
  chrome.bluetooth.getDevices(function(devices) {
    console.dir(devices);
    for (var i = 0; i < devices.length; i++) {
      self.updateDeviceName(devices[i]);
      console.log(devices[i].address + ' = ' +
                  devices[i].vendorIdSource + ':' +
                  devices[i].vendorId.toString(16) + ':' +
                  devices[i].productId.toString(16) + ':' +
                  devices[i].deviceId.toString(16));
    }
  });
}

Bluetooth.prototype.connectSocket = function(device) {
  var self = this;
  console.log('create bluetooth socket...');
  chrome.bluetoothSocket.create(function(createInfo) {
    // console.log(createInfo.socketId, device.address, uui);
    console.log('attempting socket connection to ' + device.address + '...');
    self.socketId = createInfo.socketId;
    chrome.bluetoothSocket.connect(createInfo.socketId, device.address, self.uuid, onConnectedCallback);
  
    chrome.bluetoothSocket.onAccept.addListener(function(acceptInfo) {
      if (info.socketId != createInfo.socketId)
        return;

      console.log('accepted socket connection!');
      console.log('sending message to RPi...');
      // Say hello...
      chrome.bluetoothSocket.send(acceptInfo.clientSocketId, 'hi', onSendCallback);

      // Accepted sockets are initially paused,
      // set the onReceive listener first.
      chrome.bluetoothSocket.onReceive.addListener(function(receiveInfo) {
        console.log("Received " + receiveInfo.data.byteLength + " bytes");
        var bytes = new Uint8Array(receiveInfo.data);
        console.log("buffer = " + JSON.stringify(bytes));
      })
      chrome.bluetoothSocket.setPaused(acceptInfo.clientSocketId, false);
    });

    chrome.bluetoothSocket.listenUsingRfcomm(createInfo.socketId, self.uuid, function() {
      if (chrome.runtime.lastError) {
        console.log("Connection failed: " + chrome.runtime.lastError.message);
      }
    });

    chrome.bluetoothSocket.onReceiveError.addListener(function(info){
      console.dir(info);
    });

  });

  var onConnectedCallback = function() {
    if (chrome.runtime.lastError) {
      console.log("Connection failed: " + chrome.runtime.lastError.message);
    } else {
      chrome.bluetoothSocket.send(self.socketId, str2ab('ssid:peterpounders'), function(bytesSent){
        console.log('sent ssid: ' + bytesSent + ' bytes (max = 128)');
      });
      chrome.bluetoothSocket.send(self.socketId, str2ab('pass:0123456789'), function(bytesSent){
        console.log('sent pass: ' + bytesSent + ' bytes (max = 128)');
      });
      // Profile implementation here.
    }
  };
}

