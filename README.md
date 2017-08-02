## Software diagram

https://github.com/TheGentlemanOctopus/thegentlemanoctopus/blob/f_octopus_code/docs/software_flow.pdf

WORK IN PROCESS FOR 2017 

Welcome to the octopus show! 

Software runs three processes in parallel:

1. OPC Server. Either LEDSCAPE on the beaglebone or the openGL simulator at home.
2. Pattern Generator. Generates RGB data and sends to an opc server over TCP
3. RPC Client. Sends external input to the pattern generator. E.g. data from user, MSGEQ7 or .wav

## openGL Simulator ##

The openGL simulator is a fork from http://openpixelcontrol.org/ and lives in `/openpixelcontrol/`. Compiling it should be as easy as

```
$cd openpixelcontrol
$make
```

The simulator requires a json file at runtime to know where the pixels are, called a layout. For example this simple layout has a single pixel at the origin
```
[
  {
    "point": [0,0,0]
  }
]
```

### Octopus Layout ###

The module to generate an octopus is in `octopus/layouts/octopus.py`. Running this will create a default octopus.json layout that is intended to reflect the real one. 

You will notice the module contains an **Octopus** class to represent the obvious. This is further broken down into **Tentacle** and **LedStrip** classes. LedStrips contain a list of **Pixel** objects which are arranged from base to tip. Extra metadata is included in the json file so they can be imported back into Octopus objects

To make the octopus layout and start the openGL server
```
$cd octopus
$python layouts/octopus.py
$../openpixelcontrol/bin/gl_server -l layouts/octopus.json 
```

Which will run the OPC server at the usual **127.0.0.1:7890**

With the simulator up and running, we can go ahead and make some patterns!

## Pattern Generator ##

The `patternGenerator.py` module provides a command-line interface for trying out patterns and playing around with parameters. Running the module will connect to an OPC Server, display the default set of patterns and run the first pattern in the set. The **(w/s)** keys switch between patterns. You can adjust the parameters for the currently selected pattern with **(r/f), (t/g)**, etc.... It will also start an RPC Server which by default listens at **http://localhost:8000**

To run the pattern generator we need to provide an octopus

```python patternGenerator.py layouts/octopus.json```

### Making Patterns ###

Patterns are stored as classes in individual files in the `/octopus/patterns/` package. `pattern.py` contains the **Pattern** base class which all patterns inherit from. 

This contains the `register_param` method used to initialise the parameters that you tinker with in the pattern generator. This should be called in a subclass constructor before it is ever referenced. You can then get and set it just like you would any other class variable, except the values are rounded to its min/max if you try and set it beyond its limits. The module's script has a simple example.

Each implementation of Pattern should define the method `next_frame(self, octopus, data)`. When a pattern is selected, this method is called repeatedly until the pattern is switched. octopus is an instance of the Octopus in `Octopus.py` and data is a dictionary of data received by a RPC Client. The method should not return anything, but instead update the pixel colors on the Octopus object. PatternGenerator contains a default dictionary so patterns don't crash on the first iteration :/ Current defaults exist for level (volume) and a 7 band EQ 

To make a pattern you should:

1. Make a new .py file in `/octopus/patterns/` containing a class that inherits from Pattern
2. In its constructor, define parameters with `register_param` calls
3. Define a `next_frame` method that updates pixels on the octopus object
4. Import the pattern into `patternGenerator.py` module and append an instance of your new pattern to the default set in the script at the bottom
5. Run, watch and marvel :)

## RPC Client ##

An RPC Client sends data to the PatternGenerator and are stored in the `/octopus/rpcClients/` package. When the PatternGenerator receives data from a client, it updates the dictionary of data passed to `next_frame`. Clients should inherit from **RpcClient** base class, which contains the default endpoint **http://localhost:8000** and the `put` method; which should be called when sending data.

For example, `userInputClient.py` repeatedly sends key value pairs from the command line. Try selecting rpcTestPattern from the PatternGenerator and use the client to adjust the brightness with the key `level` using a value between 0-255

`streamWavClient.py` plays a .wav file while streaming level and eq data. With the PatternGenerator running try

`python rpcClients/streamWavClient.py ../examples/FFT/DaftPunk.wav`

### Running on Odroid ###

ssh to odroid
```bash
ssh odroid@192.168.1.42
```

run screen 
```bash
screen
```

run start script
```bash
./runOctopus.sh
```

to detatch screen session
```bash
ctrl+a   then d
```

to return to active session 
```bash
screen -r
```
