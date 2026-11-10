from trek import Trek


class Transport:
    # Creates a valid vehicle with no assignments; an invalid value raises ValueError before any field is set
    def __init__(self, transport_id, vehicle_type, seats):
        if type(transport_id) is not int or transport_id<=0:
            raise ValueError(f"Invalid transport id: {transport_id}")
        if type(vehicle_type) is not str or not vehicle_type.strip():
            raise ValueError(f"Invalid vehicle type: {vehicle_type}")
        # Assumption: the smallest useful vehicle holds a guide and one participant
        if type(seats) is not int or seats<2:
            raise ValueError(f"Invalid seats: {seats}")

        # Unique identifier of the vehicle
        self.transport_id=transport_id
        # Kind of vehicle, such as a minibus
        self.vehicle_type=vehicle_type
        # Number of seats, including the guide's
        self.seats=seats
        # Assignments as dictionaries of trek and pickup point, changed only through assign_to_trek and remove_from_trek
        self.assignments=[]

    # Returns True if the range overlaps no active trek; reads the live trek, because a trek cannot notify this class when it is cancelled or moved
    def is_available(self, start_date, duration_days, ignore_trek_id=None):
        Trek.check_dates(start_date, duration_days)
        for assignment in self.assignments:
            trek=assignment["trek"]
            if trek.is_active() and trek.trek_id!=ignore_trek_id and trek.overlaps(start_date, duration_days):
                return False
        return True

    # Assigns the vehicle to a trek with its pickup point, only after every check has passed
    def assign_to_trek(self, trek, pickup_point):
        if not isinstance(trek, Trek):
            raise ValueError(f"Invalid trek: {trek}")
        if not trek.is_active():
            raise ValueError(f"Cannot assign a vehicle to a {trek.status} trek")
        if type(pickup_point) is not str or not pickup_point.strip():
            raise ValueError(f"Invalid pickup point: {pickup_point}")
        for assignment in self.assignments:
            if assignment["trek"] is trek:
                raise ValueError(f"Vehicle {self.transport_id} is already assigned to trek {trek.trek_id}")
        if not self.is_available(trek.start_date, trek.duration_days):
            raise ValueError(f"Vehicle {self.transport_id} is not available on these dates")

        self.assignments.append({"trek": trek, "pickup_point": pickup_point})

    # Removes the assignment of a trek
    def remove_from_trek(self, trek_id):
        for assignment in self.assignments:
            if assignment["trek"].trek_id==trek_id:
                self.assignments.remove(assignment)
                return
        raise ValueError(f"Trek {trek_id} is not assigned to vehicle {self.transport_id}")

    # Returns True if the vehicle is assigned to the trek
    def is_assigned_to(self, trek_id):
        for assignment in self.assignments:
            if assignment["trek"].trek_id==trek_id:
                return True
        return False

    # Returns True if the trek's vehicles together seat everyone; static, because one vehicle does not know the others
    @staticmethod
    def has_enough_seats(trek, vehicles):
        if not isinstance(trek, Trek):
            raise ValueError(f"Invalid trek: {trek}")
        if type(vehicles) is not list:
            raise ValueError(f"Invalid vehicles: {vehicles}")
        total_seats=0
        counted=[]
        for vehicle in vehicles:
            if not isinstance(vehicle, Transport):
                raise ValueError(f"Invalid vehicle: {vehicle}")
            # A vehicle listed twice or serving another trek would inflate the total
            if vehicle in counted:
                raise ValueError(f"Vehicle {vehicle.transport_id} is listed twice")
            if not vehicle.is_assigned_to(trek.trek_id):
                raise ValueError(f"Vehicle {vehicle.transport_id} is not assigned to trek {trek.trek_id}")
            counted.append(vehicle)
            total_seats+=vehicle.seats
        # Assumption: one seat stays for the guide, and the trek can reach max_participants
        return total_seats>=trek.max_participants+1

    # Returns pairs of ids of overlapping active treks, which can only happen after set_dates without this vehicle in its list
    def find_conflicts(self):
        active=[]
        for assignment in self.assignments:
            if assignment["trek"].is_active():
                active.append(assignment["trek"])

        conflicts=[]
        for i in range(len(active)):
            for second in active[i+1:]:
                if active[i].overlaps(second.start_date, second.duration_days):
                    conflicts.append((active[i].trek_id, second.trek_id))
        return conflicts
