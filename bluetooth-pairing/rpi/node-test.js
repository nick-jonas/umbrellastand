var noble = require('noble');

var serviceUUIDs = []; // default: [] => all
var allowDuplicates = false; // default: false

noble.startScanning(serviceUUIDs, allowDuplicates); // particular UUID's

noble.on('stateChange', function(state){
	console.log(state);
});

noble.on('discover', function(peripheral){
	console.log(peripheral);
});