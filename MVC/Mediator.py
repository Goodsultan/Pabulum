from MVC.Model import Model
from MVC.View import View
from MVC.Controller import Controller


class Mediator:
    def __init__(self):
        self.model = Model()
        self.view = View(self)
        self.controller = Controller(self)
