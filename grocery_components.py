from abc import ABC, abstractmethod

class GroceryComponent(ABC):
    @abstractmethod
    def display(self):
        pass

class GroceryItem(GroceryComponent):
    def __init__(self, name, category, cost=None, mfg_date=None, exp_date=None, barcode=None, quantity=1):
        self.name = name
        self.category = category
        self.cost = cost
        self.mfg_date = mfg_date
        self.exp_date = exp_date
        self.barcode = barcode
        self.quantity = quantity  # Add quantity attribute

    def display(self):
        item_info = f"{self.name} ({self.category})"
        if self.cost:
            item_info += f" - ${self.cost}"
        if self.quantity > 1:
            item_info += f" - Qty: {self.quantity}"
        if self.mfg_date:
            item_info += f" - Mfg: {self.mfg_date}"
        if self.exp_date:
            item_info += f" - Exp: {self.exp_date}"
        if self.barcode:
            item_info += f" - Barcode: {self.barcode}"
        return item_info

class GroceryCategory(GroceryComponent):
    def __init__(self, name):
        self.name = name
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def display(self):
        result = []
        for child in self.children:
            result.append(child.display())
        return result