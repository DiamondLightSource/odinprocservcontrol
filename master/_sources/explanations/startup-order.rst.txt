Why the processes are restarted in a certain order
==================================================

Most of the Odin processes in a deployment either don't care about each other or are
able to coordinate with each other regardless of the order they come up in. This means
that most of the processes can be started together simulataneously. The exceptions to
this are the Odin server and the ADOdin IOC. There is a delay in starting the server to
allow the underlying processes time to initialise so that the server does not get errors
trying to connect to them. The IOC then has a delay to allow the server to initialise.
The IOC and server could come up in any order, except that the IOC generally has dbpf
calls that will configure the server in a certain way, so this delay is just to ensure
those don't happen until the server is ready.
