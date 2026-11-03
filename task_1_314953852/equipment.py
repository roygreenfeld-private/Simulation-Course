from datetime import timedelta
from trek import Trek


class Equipment:
    # Creates a valid equipment item with no loans; the class only reports an invalid value, the calling code decides how to handle it
    def __init__(self, equipment_id, name, total_quantity):
        if type(equipment_id) is not int or equipment_id<=0:
            raise ValueError(f"Invalid equipment id: {equipment_id}")
        if type(name) is not str or not name.strip():
            raise ValueError(f"Invalid name: {name}")
        if type(total_quantity) is not int or total_quantity<1:
            raise ValueError(f"Invalid total quantity: {total_quantity}")

        # Unique identifier of the item
        self.equipment_id=equipment_id
        # Display name of the item, such as a tent
        self.name=name
        # How many units the agency owns
        self.total_quantity=total_quantity
        # Loans as dictionaries of trek and quantity, changed only through loan_to_trek and return_from_trek
        self.loans=[]

    # Returns the quantity out on one day; reads the live trek, because a trek cannot notify this class when it is cancelled or moved
    def get_quantity_on_loan(self, day, ignore_trek_id=None):
        quantity=0
        for loan in self.loans:
            trek=loan["trek"]
            if trek.is_active() and trek.trek_id!=ignore_trek_id and trek.overlaps(day, 1):
                quantity+=loan["quantity"]
        return quantity

    # Returns the units free for the whole range, by its busiest day; ignore_trek_id lets the calling code check a move before set_dates
    def get_available_quantity(self, start_date, duration_days, ignore_trek_id=None):
        Trek.check_dates(start_date, duration_days)
        busiest=0
        for offset in range(duration_days):
            day=start_date+timedelta(days=offset)
            busiest=max(busiest, self.get_quantity_on_loan(day, ignore_trek_id))
        # A move with set_dates can leave more on loan than the stock, which find_conflicts reports
        return max(self.total_quantity-busiest, 0)

    # Lends a quantity to a trek, only after every check has passed
    def loan_to_trek(self, trek, quantity):
        if not isinstance(trek, Trek):
            raise ValueError(f"Invalid trek: {trek}")
        if not trek.is_active():
            raise ValueError(f"Cannot lend to a {trek.status} trek")
        if type(quantity) is not int or quantity<1:
            raise ValueError(f"Invalid quantity: {quantity}")
        for loan in self.loans:
            if loan["trek"] is trek:
                raise ValueError(f"Trek {trek.trek_id} already has a loan of {self.name}")
        if quantity>self.get_available_quantity(trek.start_date, trek.duration_days):
            raise ValueError(f"Not enough {self.name} on the dates of trek {trek.trek_id}")

        self.loans.append({"trek": trek, "quantity": quantity})

    # Removes the loan of a trek and returns the quantity that came back
    def return_from_trek(self, trek_id):
        for loan in self.loans:
            if loan["trek"].trek_id==trek_id:
                self.loans.remove(loan)
                return loan["quantity"]
        raise ValueError(f"Trek {trek_id} has no loan of {self.name}")

    # Returns True if the item is on loan to the trek
    def is_loaned_to(self, trek_id):
        for loan in self.loans:
            if loan["trek"].trek_id==trek_id:
                return True
        return False

    # Returns True if the trek's loan still fits on the given dates, not counting the loan itself; set_dates uses it before moving a trek
    def can_supply(self, trek_id, start_date, duration_days):
        for loan in self.loans:
            if loan["trek"].trek_id==trek_id:
                return loan["quantity"]<=self.get_available_quantity(start_date, duration_days, trek_id)
        raise ValueError(f"Trek {trek_id} has no loan of {self.name}")

    # Returns the ids of active treks with a day over the stock, which can only happen after set_dates without this item in its list
    def find_conflicts(self):
        conflicts=[]
        for loan in self.loans:
            trek=loan["trek"]
            if trek.is_active():
                for offset in range(trek.duration_days):
                    day=trek.start_date+timedelta(days=offset)
                    if self.get_quantity_on_loan(day)>self.total_quantity:
                        conflicts.append(trek.trek_id)
                        break
        return conflicts
