class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year

    def display_car(self):
        print(f"{self.make} {self.model} {self.year}")

    def drive(self):
        print("Vroom! Vroom!")


