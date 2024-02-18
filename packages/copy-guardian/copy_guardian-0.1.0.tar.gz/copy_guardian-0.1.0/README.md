# copy guardian

File system based semaphore + rsync.


## Features

`copy_guardian` implements a file system based seamaphore to limit execution of
critical operations. The default mode binds the semaphore to the script which
owns it, such that operations can be also limitted over parallel executions within
a HPC batch system.
