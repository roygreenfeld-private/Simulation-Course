from trek import Trek


class Traveler:
    # The only membership types a traveler can have
    VALID_MEMBERSHIPS=("basic", "annual", "premium")
    # Assumption: the discount rate of each membership type; the rates are our choice
    MEMBERSHIP_DISCOUNTS={"basic": 0.0, "annual": 0.1, "premium": 0.2}
    # Assumption: a private tour costs a fixed amount per day, because request_private_tour receives no price
    PRIVATE_TOUR_DAILY_PRICE=500

    # Creates a valid traveler with no treks; the class only reports an invalid value, the calling code decides how to handle it
    def __init__(self, traveler_id, name, age, membership_type, experience_level):
        if type(traveler_id) is not int or traveler_id<=0:
            raise ValueError(f"Invalid traveler id: {traveler_id}")
        if type(name) is not str or not name.strip():
            raise ValueError(f"Invalid name: {name}")
        if type(age) is not int or age<=0:
            raise ValueError(f"Invalid age: {age}")
        if membership_type not in Traveler.VALID_MEMBERSHIPS:
            raise ValueError(f"Invalid membership type: {membership_type}")
        # Assumption: the same 1 to 10 scale as a trek's difficulty level
        if type(experience_level) is not int or not 1<=experience_level<=10:
            raise ValueError(f"Invalid experience level: {experience_level}")

        # Unique identifier of the traveler
        self.traveler_id=traveler_id
        # Full name of the traveler
        self.name=name
        # Age of the traveler in years
        self.age=age
        # Membership type, one of VALID_MEMBERSHIPS
        self.membership_type=membership_type
        # Experience on the same scale as a trek's difficulty level
        self.experience_level=experience_level
        # Treks the traveler is registered to, changed only through Trek's methods and add_completed_trek
        self.current_treks=[]
        # Treks the traveler finished, changed only through add_completed_trek
        self.completed_treks=[]

    # Asks to register to a trek; Trek makes all the checks, so there is one place that registers
    def register_to_trek(self, trek):
        if not isinstance(trek, Trek):
            raise ValueError(f"Invalid trek: {trek}")
        trek.register(self)

    # Cancels a registration and returns the refund rate, which is calculated before the trek is released
    def cancel_trek(self, trek_id):
        for trek in self.current_treks:
            if trek.trek_id==trek_id:
                refund_rate=trek.calculate_refund_rate()
                trek.cancel_registration(self.traveler_id)
                return refund_rate
        raise ValueError(f"Traveler {self.traveler_id} is not registered to trek {trek_id}")

    # Moves a trek from current to completed, only after the trek itself was closed
    def add_completed_trek(self, trek_id):
        for trek in self.current_treks:
            if trek.trek_id==trek_id:
                if trek.status!="completed":
                    raise ValueError(f"Trek {trek_id} is not completed")
                self.current_treks.remove(trek)
                self.completed_treks.append(trek)
                return
        raise ValueError(f"Trek {trek_id} is not a current trek of traveler {self.traveler_id}")

    # Creates a one person trek with this guide and returns it; the calling code adds it to the agency
    def request_private_tour(self, guide, start_date, duration_days):
        # Checks the shared name rather than the class, because the guide file imports nothing from this one
        if not hasattr(guide, "guide_id"):
            raise ValueError(f"Invalid guide: {guide}")
        if not self.is_available(start_date, duration_days):
            raise ValueError(f"Traveler {self.traveler_id} is not available on these dates")

        # Assumption: an id built from the traveler and the date needs no counter, and a traveler cannot start two treks on one day
        trek_id=self.traveler_id*1000000+start_date.toordinal()
        # Assumption: the region is the guide's first specialty and the difficulty is the traveler's own level
        trek=Trek(trek_id, f"Private tour of {self.name}", guide.specialties[0], self.experience_level,
                  1, 1, start_date, duration_days, Traveler.PRIVATE_TOUR_DAILY_PRICE*duration_days)
        # Checked here because the guide is assigned before the registration that would reject this date
        if trek.has_departed():
            raise ValueError("Cannot request a private tour that has already departed")

        trek.assign_guide(guide)
        trek.register(self)
        return trek

    # Returns True if the date range overlaps none of the current treks; ignore_trek_id lets a trek skip itself when it moves
    def is_available(self, start_date, duration_days, ignore_trek_id=None):
        Trek.check_dates(start_date, duration_days)
        for trek in self.current_treks:
            if trek.trek_id!=ignore_trek_id and trek.overlaps(start_date, duration_days):
                return False
        return True

    # Returns the trek's price after the membership discount, without changing the trek's full price
    def get_final_price(self, trek):
        if not isinstance(trek, Trek):
            raise ValueError(f"Invalid trek: {trek}")
        return round(trek.price*(1-Traveler.MEMBERSHIP_DISCOUNTS[self.membership_type]), 2)

    # Returns a payment report calculated on every call; a current trek also shows its fee if cancelled today, a past cancellation has no field to be kept in
    def generate_payment_report(self):
        treks=[]
        total=0
        for trek in self.current_treks:
            final_price=self.get_final_price(trek)
            cancellation_fee=round(final_price*(1-trek.calculate_refund_rate()), 2)
            treks.append({"trek_id": trek.trek_id, "name": trek.name, "state": "current",
                          "final_price": final_price, "cancellation_fee": cancellation_fee})
            total+=final_price
        for trek in self.completed_treks:
            final_price=self.get_final_price(trek)
            treks.append({"trek_id": trek.trek_id, "name": trek.name, "state": "completed",
                          "final_price": final_price, "cancellation_fee": 0})
            total+=final_price
        return {"traveler_id": self.traveler_id, "name": self.name, "membership_type": self.membership_type,
                "discount": Traveler.MEMBERSHIP_DISCOUNTS[self.membership_type], "treks": treks, "total": round(total, 2)}
