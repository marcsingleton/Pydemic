from sys import exit

import pydemic.exceptions as exceptions
from pydemic.display import indent
from pydemic.main import main

try:
    main()
except exceptions.GameOverWin:
    print('Congratulations, you won!')
except exceptions.GameOverLose as error:
    print('GAME OVER')
    print(f'{indent}{error}')
    print(f'{indent}Better luck next time!')
except KeyboardInterrupt as error:
    print()  # Start new line in case shell doesn't
    exit()
