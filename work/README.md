# Work Directory

This directory reserved for working files by the runtime. 

In develop mode, it will be written to directly, allowing one to easily inspect the files created.

In prod mode, the work directory will be volume mounted, as the container is considered read-only.