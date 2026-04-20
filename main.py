from MVC.Mediator import Mediator
import os

if __name__ == '__main__':
    # Auto-create if non-existent
    if not os.path.exists(fr'{os.getcwd()}\sets'):
        # Stop the editor from modifying it after I move the folders
        os.mkdir('se' + 'ts')

    if not os.path.exists(fr'{os.getcwd()}\images'):
        os.mkdir('im' + 'ages')

    mediator = Mediator()

    mediator.view.root.mainloop()

