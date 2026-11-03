import math
from datetime import date, timedelta


class Trek:
    # Assumption: the agency operates only in Israel, in these regions. To add a region, add it here
    VALID_REGIONS=("Golan Heights", "Galilee", "Upper Galilee", "Lower Galilee", "Carmel",
                   "Judean Mountains", "Judean Desert", "Dead Sea", "Negev",
                   "Arava", "Eilat Mountains")
    # The only statuses a trek can be in
    VALID_STATUSES=("planned", "confirmed", "cancelled", "completed")

    # Creates a valid trek with no guide and no participants; the class only reports an invalid value, the calling code decides how to handle it
    def __init__(self, trek_id, name, region, difficulty_level, min_participants,
                 max_participants, start_date, duration_days, price):
        # Assumption: trek_id and difficulty_level are whole numbers
        if type(trek_id) is not int or trek_id<=0:
            raise ValueError(f"Invalid trek id: {trek_id}")
        if type(name) is not str or not name.strip():
            raise ValueError(f"Invalid name: {name}")
        if region not in Trek.VALID_REGIONS:
            raise ValueError(f"Invalid region: {region}")
        if type(difficulty_level) is not int or not 1<=difficulty_level<=10:
            raise ValueError(f"Invalid difficulty level: {difficulty_level}")
        if type(min_participants) is not int or type(max_participants) is not int:
            raise ValueError("Participant limits must be whole numbers")
        if min_participants<=0 or min_participants>max_participants:
            raise ValueError(f"Invalid participant limits: {min_participants}, {max_participants}")
        Trek.check_dates(start_date, duration_days)
        if type(price) not in (int, float) or not math.isfinite(price) or price<=0:
            raise ValueError(f"Invalid price: {price}")

        # Unique identifier of the trek
        self.trek_id=trek_id
        # Display name of the trek
        self.name=name
        # Region of the trek, one of VALID_REGIONS
        self.region=region
        # Difficulty on a scale of 1 to 10
        self.difficulty_level=difficulty_level
        # Minimum number of participants needed for the trek to depart
        self.min_participants=min_participants
        # Maximum number of participants the trek can hold
        self.max_participants=max_participants
        # Departure date, changed later only through set_dates
        self.start_date=start_date
        # Length of the trek in days, changed later only through set_dates
        self.duration_days=duration_days
        # Full price before discounts
        self.price=price
        # Assigned guide, None until assign_guide checks availability
        self.guide=None
        # Registered travelers, changed only through register, cancel_registration and cancel_trek
        self.participants=[]
        # Waiting travelers in order of arrival, changed only through add_to_waiting_list, promote_from_waiting_list and cancel_trek
        self.waiting_list=[]
        # Current status, one of VALID_STATUSES, updated by update_status, cancel_trek and complete_trek
        self.status="planned"

    # Validates a date range in one place; static so Traveler and Guide can use it with no trek object, a deliberate step beyond the tutorial
    @staticmethod
    def check_dates(start_date, duration_days):
        # type() rejects datetime, because comparing it with a date raises TypeError
        if type(start_date) is not date:
            raise ValueError(f"Invalid start date: {start_date}")
        if type(duration_days) is not int or duration_days<1:
            raise ValueError(f"Invalid duration: {duration_days}")

    # Rejects anything without a traveler id; checks the shared name rather than the class, so the trek file needs no circular import
    def check_traveler(self, traveler):
        if not hasattr(traveler, "traveler_id"):
            raise ValueError(f"Invalid traveler: {traveler}")

    # Rejects anything without a guide id, for the same reason as check_traveler
    def check_guide(self, guide):
        if not hasattr(guide, "guide_id"):
            raise ValueError(f"Invalid guide: {guide}")

    # Returns True while the trek can still change, meaning it is neither cancelled nor completed
    def is_active(self):
        return self.status in ("planned", "confirmed")

    # Returns the last day of the trek; the end day counts, so a one day trek ends on its start date
    def get_end_date(self):
        return self.start_date+timedelta(days=self.duration_days-1)

    # Returns True if the given date range shares at least one day with this trek
    def overlaps(self, start_date, duration_days):
        Trek.check_dates(start_date, duration_days)
        end_date=start_date+timedelta(days=duration_days-1)
        return start_date<=self.get_end_date() and self.start_date<=end_date

    # Returns True if the guide has no room left in the month of the given date, not counting this trek
    def is_guide_month_full(self, guide, start_date):
        count=0
        for trek in guide.assigned_treks:
            if trek is not self and trek.start_date.year==start_date.year and trek.start_date.month==start_date.month:
                count+=1
        return count>=guide.max_monthly_treks

    # Assigns a guide and updates both sides, after checking status, region, schedule and monthly limit
    def assign_guide(self, guide):
        self.check_guide(guide)
        if not self.is_active():
            raise ValueError(f"Cannot assign a guide to a {self.status} trek")
        if self.guide is not None:
            raise ValueError(f"Trek {self.trek_id} already has a guide")
        if self.region not in guide.specialties:
            raise ValueError(f"Guide {guide.guide_id} does not specialize in {self.region}")
        if not guide.is_available(self.start_date, self.duration_days):
            raise ValueError(f"Guide {guide.guide_id} is not available on these dates")
        if self.is_guide_month_full(guide, self.start_date):
            raise ValueError(f"Guide {guide.guide_id} reached the monthly trek limit")

        self.guide=guide
        guide.assigned_treks.append(self)

    # Sets new dates only if the guide and every participant can make them, otherwise the old dates stay
    def set_dates(self, start_date, duration_days):
        Trek.check_dates(start_date, duration_days)
        if not self.is_active():
            raise ValueError(f"Cannot change the dates of a {self.status} trek")
        # The trek's own id is ignored, otherwise it would conflict with itself
        if self.guide is not None:
            if not self.guide.is_available(start_date, duration_days, self.trek_id):
                raise ValueError(f"Guide {self.guide.guide_id} is not available on these dates")
            if self.is_guide_month_full(self.guide, start_date):
                raise ValueError(f"Guide {self.guide.guide_id} reached the monthly trek limit")
        for traveler in self.participants:
            if not traveler.is_available(start_date, duration_days, self.trek_id):
                raise ValueError(f"Traveler {traveler.traveler_id} is not available on these dates")

        self.start_date=start_date
        self.duration_days=duration_days

    # Returns True if at least one place is left
    def has_capacity(self):
        return len(self.participants)<self.max_participants

    # Returns True if the traveler's experience reaches the trek's difficulty (assumption: both use the same scale)
    def is_suitable(self, traveler):
        self.check_traveler(traveler)
        return traveler.experience_level>=self.difficulty_level

    # Returns True once the departure day has arrived
    def has_departed(self):
        return self.start_date<=date.today()

    # Registers a traveler and updates both sides, only after every check has passed
    def register(self, traveler):
        self.check_traveler(traveler)
        if not self.is_active():
            raise ValueError(f"Cannot register to a {self.status} trek")
        if self.has_departed():
            raise ValueError(f"Trek {self.trek_id} has already departed")
        if traveler in self.participants:
            raise ValueError(f"Traveler {traveler.traveler_id} is already registered")
        if traveler in self.waiting_list:
            raise ValueError(f"Traveler {traveler.traveler_id} is on the waiting list")
        if not self.is_suitable(traveler):
            raise ValueError(f"Traveler {traveler.traveler_id} is not suitable for this trek")
        if not self.has_capacity():
            raise ValueError(f"Trek {self.trek_id} is full")
        if not traveler.is_available(self.start_date, self.duration_days):
            raise ValueError(f"Traveler {traveler.traveler_id} has a schedule conflict")

        self.participants.append(traveler)
        traveler.current_treks.append(self)
        self.update_status()

    # Cancels a registration on both sides, then promotes a waiting traveler and refreshes the status
    def cancel_registration(self, traveler_id):
        if not self.is_active():
            raise ValueError(f"Cannot cancel a registration of a {self.status} trek")
        for traveler in self.participants:
            if traveler.traveler_id==traveler_id:
                self.participants.remove(traveler)
                traveler.current_treks.remove(self)
                self.promote_from_waiting_list()
                self.update_status()
                return
        raise ValueError(f"Traveler {traveler_id} is not registered to trek {self.trek_id}")

    # Returns the refund rate between 0 and 1 by days before departure; the tiers are our choice: 30+ full, 14-29 75%, 7-13 half, else none
    def calculate_refund_rate(self, cancel_date=None):
        # With no date the rate uses today; the optional parameter keeps results repeatable in tests
        if cancel_date is None:
            cancel_date=date.today()
        if type(cancel_date) is not date:
            raise ValueError(f"Invalid cancel date: {cancel_date}")
        days_before=(self.start_date-cancel_date).days
        if days_before>=30:
            return 1.0
        if days_before>=14:
            return 0.75
        if days_before>=7:
            return 0.5
        return 0.0

    # Adds a traveler to the end of the waiting list, only when the trek is full
    def add_to_waiting_list(self, traveler):
        self.check_traveler(traveler)
        if not self.is_active():
            raise ValueError(f"Cannot join the waiting list of a {self.status} trek")
        if self.has_departed():
            raise ValueError(f"Trek {self.trek_id} has already departed")
        if self.has_capacity():
            raise ValueError(f"Trek {self.trek_id} still has room, register instead")
        if traveler in self.participants:
            raise ValueError(f"Traveler {traveler.traveler_id} is already registered")
        if traveler in self.waiting_list:
            raise ValueError(f"Traveler {traveler.traveler_id} is already on the waiting list")
        if not self.is_suitable(traveler):
            raise ValueError(f"Traveler {traveler.traveler_id} is not suitable for this trek")

        self.waiting_list.append(traveler)

    # Promotes a waiting traveler by membership type, then by order of arrival within the type; anyone no longer available is skipped, and doing nothing is not an error
    def promote_from_waiting_list(self):
        if not self.has_capacity() or self.has_departed():
            return
        # Assumption: premium comes before annual, and annual before basic
        for membership_type in ("premium", "annual", "basic"):
            for traveler in self.waiting_list:
                if traveler.membership_type==membership_type and traveler.is_available(self.start_date, self.duration_days):
                    self.waiting_list.remove(traveler)
                    self.register(traveler)
                    return

    # Sets confirmed or planned by the number of participants; a cancelled or completed trek never changes back
    def update_status(self):
        if not self.is_active():
            return
        if len(self.participants)>=self.min_participants:
            self.status="confirmed"
        else:
            self.status="planned"

    # Cancels the trek on the agency's initiative and releases everyone (assumption: travelers owe nothing, so the trek just leaves their current treks)
    def cancel_trek(self):
        if not self.is_active():
            raise ValueError(f"Cannot cancel a {self.status} trek")
        for traveler in self.participants:
            traveler.current_treks.remove(self)
        self.participants=[]
        self.waiting_list=[]
        if self.guide is not None:
            self.guide.remove_trek(self.trek_id)
        self.status="cancelled"

    # Closes a confirmed trek that has ended and credits every participant; the optional date keeps tests repeatable
    def complete_trek(self, completion_date=None):
        if completion_date is None:
            completion_date=date.today()
        if type(completion_date) is not date:
            raise ValueError(f"Invalid completion date: {completion_date}")
        if self.status!="confirmed":
            raise ValueError(f"Cannot complete a {self.status} trek")
        if completion_date<self.get_end_date():
            raise ValueError(f"Trek {self.trek_id} has not ended yet")

        # The status changes first, because add_completed_trek accepts only a completed trek
        self.status="completed"
        for traveler in self.participants:
            traveler.add_completed_trek(self.trek_id)
