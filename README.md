# pysesame2

Python API for Sesame Smartlock made by CANDY HOUSE, Inc.

### API KEY

You have to generate apikey using candyhouse dashboard: https://my.candyhouse.co/

### Installation

Install from pypi

```shell
# pip install pysesame2
```

Install from source

```shell
# python setup.py install
```

### Example

#### python

```python
from pysesame2 import get_sesames

sesames = get_sesames(YOUR_APIKEY)

sesame = sesames[0]
print(sesame)
print(sesame.get_status())
sesame.lock()
```

```python
from uuid import UUID
from time import sleep
from pyseame2 import Sesame

device_id = UUID('YOUR DEVICE UUID')
sesame = Sesame(device_id, YOUR_APIKEY)
print(sesame.get_status())

task = sesame.async_lock()
while task.pooling() is False:
    print('Processing...')
    sleep(1)
print('Result: %s' % task.is_successful)
```

#### Command Line Interface

```shell
# sesame2 --apikey YOUR_APIKEY list
                           Device ID        Serial Nickame
======================================================================
00000000-0000-0000-0000-000000000001  000000000001 MY-SESAME-LOCK-1
00000000-0000-0000-0000-000000000002  000000000002 MY-SESAME-LOCK-2

# sesame2 --apikey YOUR_APIKEY lock 00000000-0000-0000-0000-000000000001

# sesame2 --apikey YOUR_APIKEY status 00000000-0000-0000-0000-000000000001
Locked: True
Battery: 100
Responsive: True
```

Use `sesame2 --help` get more options
