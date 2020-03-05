// https://gist.github.com/Xaekai/e1f711cb0ad865deafc11185641c632a
const net = require('net');
const unixSocketServer = net.createServer();

unixSocketServer.listen('/tmp/unixSocket', () => {
  console.log('now listening');
});

unixSocketServer.on('connection', (s) => {
  console.log('got connection!');
  s.on('data', (d) => {
	  o = JSON.parse(d.toString())
	  console.log(o)
	  console.log(`Current position is: ${o.current_position}`)
  });
  s.end();
});
