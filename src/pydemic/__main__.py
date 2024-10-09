import pydemic.exceptions as exceptions
from pydemic.main import main

try:
    main()
except exceptions.GameOver as error:
    print('Game over:', error)
