# Python Logger:
 
This script was made for logging as fast and simple as possible. Make sure you have write permission for your log file.

It's reccommended that you use an absolute route for your log file.

Multiple instances of this logger can be used (With same or different log_name)

## Sample usage:

```
from pathlib import Path # This line is intended for using Path(), it is not required for LocalLogger
from pythonlogger.logger import LocalLogger

log = LocalLogger(str(Path(__file__).resolve().parent) + '/log.log', 'Some-logger')
log.debug('mensaje debug')
log.info('mensaje info')
log.warning('mensaje warning')
log.error('mensaje error')
log.critical('mensaje critical')
```

By default, it logs from WARNING to CRITICAL messages. If you want to change it, you can call `log.SetLevel('debug')` to log every message.

Made by Juan Ignacio De Nicola. Feel free to redistribute or modify it as you wish.
