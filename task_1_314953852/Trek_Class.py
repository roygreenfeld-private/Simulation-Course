class Trek:
    # Assumption: the agency operates only in Israel, in these regions. To add a region, add it here
    VALID_REGIONS=("Golan Heights", "Upper Galilee", "Lower Galilee", "Carmel",
                   "Judean Mountains", "Judean Desert", "Dead Sea", "Negev",
                   "Arava", "Eilat Mountains")
    VALID_STATUSES=("planned", "confirmed", "cancelled", "completed")

    def __init__(self, trek_id, name, region, difficulty_level, min_participants,
                 max_participants, start_date, duration_days, price):
        # The class only reports an invalid value, the calling code decides how to handle it
        # Assumption: trek_id and difficulty_level are whole numbers
        if type(trek_id) is not int or trek_id<=0:
            raise ValueError(f"Invalid trek id: {trek_id}")
        if type(name) is not str:
            raise ValueError(f"Invalid name: {name}")
        if region not in Trek.VALID_REGIONS:
            raise ValueError(f"Invalid region: {region}")
        if type(difficulty_level) is not int or not 1<=difficulty_level<=10:
            raise ValueError(f"Invalid difficulty level: {difficulty_level}")
        if type(min_participants) is not int or type(max_participants) is not int:
            raise ValueError("Participant limits must be whole numbers")
        if min_participants<=0 or min_participants>max_participants:
            raise ValueError(f"Invalid participant limits: {min_participants}, {max_participants}")
        if type(duration_days) is not int or duration_days<1:
            raise ValueError(f"Invalid duration: {duration_days}")
        if type(price) not in (int, float) or price<=0:
            raise ValueError(f"Invalid price: {price}")

        self.trek_id=trek_id
        self.name=name
        self.region=region
        self.difficulty_level=difficulty_level
        self.min_participants=min_participants
        self.max_participants=max_participants
        # Known at creation, can be changed later through set_dates
        self.start_date=start_date
        self.duration_days=duration_days
        # Full price before discounts
        self.price=price
        # No guide at creation: assigned only through assign_guide, which checks availability
        self.guide=None
        # Both lists start empty, so travelers are added only through
        # register (capacity, suitability and schedule checks) or add_to_waiting_list
        self.participants=[]
        self.waiting_list=[]
        # A new trek starts as "planned", updated later by update_status, cancel_trek and complete_trek
        self.status="planned"
