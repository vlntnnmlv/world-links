from railwaynet import *
from editor import *

from threading import Thread

# region Main

def main() -> None:
    manager, _, _ = default_setup()

    editor = Editor(manager)
    editor.run()

# endregion

if __name__ == "__main__":
    main()
