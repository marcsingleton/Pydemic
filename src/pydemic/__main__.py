from sys import exit

import pydemic.exceptions as exceptions
from pydemic.main import main

try:
    main()
except exceptions.GameOver as error:
    print('Game over:', error)
except KeyboardInterrupt as error:
    print()  # Start new line in case shell doesn't
    exit()
