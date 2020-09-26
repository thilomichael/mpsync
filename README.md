# mpsync

**mpsync** is a little tool that you can run during your MicroPython development to automatically upload changes in your code to a board. Simply run it inside the folder you want to sync up and it will create, upload, and delete files from and to your board whenever something changes.

## How to Install

Install by running

```
$ python setup.py install
```

Afterwards, you can just use `mpsync` anywhere to start the script.

## How to Use

```
usage: mpsync [-h] [-f FOLDER] [-p PORT] [-v]

A tool that continously synchronizes a folder to a MicroPython board.

optional arguments:
  -h, --help            show this help message and exit
  -f FOLDER, --folder FOLDER
                        The folder that should be used to synchronize. Default is the current one
  -p PORT, --port PORT  Serial port of the MicroPython board.
  -v, --verbose         Print debug information.
```

You can specify the folder you want to sync either by starting the script from the folder or by specifying it in the `--folder` argument. You can specify the location of your MicroPython board with `--port`. Here is an example:

```
~ $ cd micropython_project
~/micropython_project $ mpsync -p /dev/tty.SLAB_USBtoUART
```

## Known Issues

mpsync is currently unable to synchronize the moving of folders. Everything else should be working. If you are having troubles, please open an issue.


## Dependencies

mpsync requires the python libraries `watchdog` and `mpfshell`.

## Ideas

I have some ideas on how to improve this tool. Let me know via an issue if you have ideas as well!

 - Performing an rsync on the complete folder when the script is started
 - Support moving of folders
 - Support specification of waiting time before stuff gets uploaded.
