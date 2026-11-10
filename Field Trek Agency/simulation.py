from datetime import date, timedelta
from trek import Trek
from traveler import Traveler
from guide import Guide
from agency import Agency
from equipment import Equipment
from transport import Transport

# The simulation of the field trek agency, and the main file of the project.
# It offers three modes: a full season scenario that runs on its own, an interactive menu
# for trying any action by hand, and ready made edge case scenarios.
# "Today" is always the real date.today(). To show the past, a trek's dates are moved; today never changes.


class AgencySimulation:
    # Creates a simulation with the sample agency loaded
    def __init__(self):
        # The agency, with its travelers, guides and treks
        self.agency=None
        # Vehicles and equipment are kept here, because Agency has no field for them
        self.vehicles=[]
        self.equipment=[]
        # Counts how the scripted steps behaved, so a scenario ends with a clear summary
        self.expected=0
        self.unexpected=0
        self.load_sample_data()

    # ------------------------------------------------------------------
    # Dates and printing
    # ------------------------------------------------------------------

    # Returns the date the given number of days from today, negative for the past
    def days_from_today(self, days):
        return date.today()+timedelta(days=days)

    # Prints a section title
    def title(self, text):
        print(f"\n{'='*72}\n{text}\n{'='*72}")

    # Prints a step title inside a scenario
    def step(self, text):
        print(f"\n--- {text} ---")

    # Runs an action that should succeed, prints the result and returns it
    # The action is passed as a lambda, so the call runs only inside the try block
    def expect_ok(self, description, action):
        try:
            result=action()
            print(f"  OK        {description}")
            self.expected+=1
            return result
        except ValueError as error:
            print(f"  UNEXPECTED {description}: rejected ({error})")
            self.unexpected+=1

    # Runs an action that should be rejected and prints the reason the class gave
    def expect_rejected(self, description, action):
        try:
            action()
            print(f"  UNEXPECTED {description}: accepted, but a rejection was expected")
            self.unexpected+=1
        except ValueError as error:
            print(f"  REJECTED  {description}: {error}")
            self.expected+=1

    # Prints whether a value matches what the scenario expects
    def expect_equal(self, description, actual, expected):
        if actual==expected:
            print(f"  OK        {description}: {actual}")
            self.expected+=1
        else:
            print(f"  UNEXPECTED {description}: got {actual}, expected {expected}")
            self.unexpected+=1

    # Prints the summary of a scenario and resets the counters
    def print_summary(self, name):
        print(f"\n{name} finished: {self.expected} steps behaved as expected, {self.unexpected} did not")
        self.expected=0
        self.unexpected=0

    # ------------------------------------------------------------------
    # Sample data
    # ------------------------------------------------------------------

    # Builds a small, realistic agency: 4 guides, 12 travelers, 7 treks, 2 vehicles and 2 equipment items
    # Nothing is registered yet; the season scenario and the menu start from here
    def load_sample_data(self):
        self.agency=Agency("Desert Steps")
        guides=[
            Guide(1, "Noa Ben-David", ["Negev", "Arava", "Eilat Mountains"], 8, 12, 3),
            Guide(2, "Amir Haddad", ["Galilee", "Upper Galilee", "Golan Heights"], 6, 5.5, 2),
            Guide(3, "Maya Katz", ["Judean Desert", "Dead Sea"], 9, 15, 3),
            Guide(4, "Eitan Shalev", ["Carmel", "Judean Mountains"], 4, 2, 2),
        ]
        for guide in guides:
            self.agency.add_guide(guide)

        travelers=[
            Traveler(1, "Dana Levi", 29, "premium", 8),
            Traveler(2, "Omer Cohen", 34, "annual", 6),
            Traveler(3, "Yael Mizrahi", 41, "basic", 4),
            Traveler(4, "Itai Peretz", 23, "basic", 7),
            Traveler(5, "Shira Avraham", 37, "premium", 5),
            Traveler(6, "Lior Friedman", 52, "annual", 3),
            Traveler(7, "Noam Biton", 19, "basic", 9),
            Traveler(8, "Tamar Golan", 45, "annual", 6),
            Traveler(9, "Avi Shapiro", 63, "premium", 2),
            Traveler(10, "Roni Azulay", 31, "basic", 5),
            Traveler(11, "Michal Dahan", 27, "annual", 7),
            Traveler(12, "Yoni Klein", 38, "basic", 4),
        ]
        for traveler in travelers:
            self.agency.add_traveler(traveler)

        # trek_id, name, region, difficulty, min, max, days from today, duration, price
        treks=[
            Trek(101, "Ramon Crater Traverse", "Negev", 6, 3, 8, self.days_from_today(45), 3, 1450),
            Trek(102, "Mount Arbel Sunrise", "Galilee", 3, 2, 4, self.days_from_today(20), 1, 320),
            Trek(103, "Judean Desert Canyons", "Judean Desert", 8, 2, 6, self.days_from_today(60), 4, 2200),
            Trek(104, "Carmel Forest Trails", "Carmel", 2, 4, 12, self.days_from_today(12), 2, 480),
            Trek(105, "Eilat Mountains Ridge", "Eilat Mountains", 5, 2, 10, self.days_from_today(90), 3, 1750),
            Trek(106, "Nahal Amud Stream", "Galilee", 2, 2, 8, self.days_from_today(20), 2, 540),
            Trek(107, "Golan Volcanoes", "Golan Heights", 4, 2, 8, self.days_from_today(30), 2, 690),
        ]
        for trek in treks:
            self.agency.add_trek(trek)

        self.vehicles=[Transport(1, "Minibus", 12), Transport(2, "Jeep", 4)]
        self.equipment=[Equipment(1, "Tent", 12), Equipment(2, "Sleeping bag", 15)]

    # ------------------------------------------------------------------
    # Finding objects by id
    # ------------------------------------------------------------------

    # Each finder raises ValueError for an unknown id, like the classes do, so the menu reports it the same way
    def find_trek(self, trek_id):
        for trek in self.agency.treks:
            if trek.trek_id==trek_id:
                return trek
        raise ValueError(f"No trek with id {trek_id}")

    def find_traveler(self, traveler_id):
        for traveler in self.agency.travelers:
            if traveler.traveler_id==traveler_id:
                return traveler
        raise ValueError(f"No traveler with id {traveler_id}")

    def find_guide(self, guide_id):
        for guide in self.agency.guides:
            if guide.guide_id==guide_id:
                return guide
        raise ValueError(f"No guide with id {guide_id}")

    def find_vehicle(self, transport_id):
        for vehicle in self.vehicles:
            if vehicle.transport_id==transport_id:
                return vehicle
        raise ValueError(f"No vehicle with id {transport_id}")

    def find_equipment(self, equipment_id):
        for item in self.equipment:
            if item.equipment_id==equipment_id:
                return item
        raise ValueError(f"No equipment with id {equipment_id}")

    # Returns the vehicles assigned to a trek, which set_dates needs to check a move
    def get_trek_vehicles(self, trek):
        return [vehicle for vehicle in self.vehicles if vehicle.is_assigned_to(trek.trek_id)]

    # Returns the equipment on loan to a trek, which set_dates needs to check a move
    def get_trek_equipment(self, trek):
        return [item for item in self.equipment if item.is_loaned_to(trek.trek_id)]

    # Moves a trek so it ended the given number of days ago and completes it; the trek's dates move, today does not
    def finish_trek(self, trek, ended_days_ago=1):
        if type(ended_days_ago) is not int or ended_days_ago<1:
            raise ValueError(f"Invalid number of days: {ended_days_ago}")
        # Checked before the move, so a trek that cannot be completed keeps its dates
        if trek.status!="confirmed":
            raise ValueError(f"Cannot complete a {trek.status} trek")
        trek.set_dates(self.days_from_today(-ended_days_ago-trek.duration_days+1), trek.duration_days,
                       self.get_trek_vehicles(trek), self.get_trek_equipment(trek))
        trek.complete_trek()

    # ------------------------------------------------------------------
    # Tables and reports
    # ------------------------------------------------------------------

    def print_treks(self):
        print(f"\n{'id':>8}  {'name':<24}{'region':<16}{'diff':>4}  {'start':<11}{'days':>4}  "
              f"{'price':>7}  {'guide':<15}{'taken':>6}  {'wait':>4}  status")
        for trek in self.agency.treks:
            guide_name="-"
            if trek.guide is not None:
                guide_name=trek.guide.name
            taken=f"{len(trek.participants)}/{trek.max_participants}"
            print(f"{trek.trek_id:>8}  {trek.name[:23]:<24}{trek.region:<16}{trek.difficulty_level:>4}  "
                  f"{str(trek.start_date):<11}{trek.duration_days:>4}  {trek.price:>7}  {guide_name:<15}"
                  f"{taken:>6}  {len(trek.waiting_list):>4}  {trek.status} (min {trek.min_participants})")

    def print_travelers(self):
        print(f"\n{'id':>4}  {'name':<16}{'age':>4}  {'membership':<11}{'level':>5}  current treks / completed treks")
        for traveler in self.agency.travelers:
            current=[trek.trek_id for trek in traveler.current_treks]
            completed=[trek.trek_id for trek in traveler.completed_treks]
            print(f"{traveler.traveler_id:>4}  {traveler.name:<16}{traveler.age:>4}  {traveler.membership_type:<11}"
                  f"{traveler.experience_level:>5}  {current} / {completed}")

    def print_guides(self):
        print(f"\n{'id':>4}  {'name':<16}{'cert':>4}  {'years':>5}  {'month max':>9}  specialties / assigned treks")
        for guide in self.agency.guides:
            assigned=[trek.trek_id for trek in guide.assigned_treks]
            print(f"{guide.guide_id:>4}  {guide.name:<16}{guide.certification_level:>4}  {guide.experience_years:>5}  "
                  f"{guide.max_monthly_treks:>9}  {', '.join(guide.specialties)} / {assigned}")

    def print_trek_details(self, trek):
        guide_name="no guide"
        if trek.guide is not None:
            guide_name=f"{trek.guide.name} (id {trek.guide.guide_id})"
        print(f"\nTrek {trek.trek_id}: {trek.name}, {trek.region}, difficulty {trek.difficulty_level}")
        print(f"  dates: {trek.start_date} to {trek.get_end_date()} ({trek.duration_days} days), price {trek.price}")
        print(f"  status: {trek.status}, participants {len(trek.participants)} of {trek.max_participants}, "
              f"minimum {trek.min_participants}, guide: {guide_name}")
        print(f"  participants: {[f'{t.traveler_id} {t.name}' for t in trek.participants]}")
        print(f"  waiting list: {[f'{t.traveler_id} {t.name} ({t.membership_type})' for t in trek.waiting_list]}")
        print(f"  refund rate if cancelled today: {trek.calculate_refund_rate():.0%}")
        vehicles=[f"{v.vehicle_type} {v.transport_id}" for v in self.get_trek_vehicles(trek)]
        items=[]
        for item in self.equipment:
            for loan in item.loans:
                if loan["trek"] is trek:
                    items.append(f"{loan['quantity']} x {item.name}")
        print(f"  vehicles: {vehicles}, equipment: {items}")

    def print_season_schedule(self):
        report=self.agency.generate_season_schedule_report()
        print(f"\nSeason schedule of {report['agency']}")
        for season, rows in report["seasons"].items():
            print(f"  {season}")
            for row in rows:
                print(f"    {row['start_date']} to {row['end_date']}  {row['trek_id']:>8} {row['name'][:23]:<24}"
                      f"{row['region']:<16} guide: {row['guide'] or '-':<15} {row['participants']} travelers, {row['status']}")
        if not report["warnings"]:
            print("  no overlap warnings")
        for warning in report["warnings"]:
            print(f"  WARNING treks {warning['trek_ids'][0]} and {warning['trek_ids'][1]} overlap: {', '.join(warning['reasons'])}")

    def print_membership_report(self):
        report=self.agency.generate_membership_report()
        print(f"\nMembership report of {report['agency']}")
        print(f"  {'type':<10}{'travelers':>10}{'active':>8}{'expected income':>17}")
        for membership_type, row in report["memberships"].items():
            print(f"  {membership_type:<10}{row['travelers']:>10}{row['active_travelers']:>8}{row['expected_income']:>17}")
        print(f"  {'total':<10}{report['total_travelers']:>10}{report['active_travelers']:>8}{report['expected_income']:>17}")

    def print_guide_statistics(self, guide):
        stats=guide.analyze_guiding_statistics()
        print(f"\nGuide {stats['guide_id']} {stats['name']}: certification {stats['certification_level']}, "
              f"{stats['experience_years']} years")
        print(f"  completed treks: {stats['completed_treks']}, upcoming treks: {stats['upcoming_treks']}, "
              f"average occupancy of completed treks: {stats['average_occupancy']:.0%}")
        print(f"  treks by region: {stats['regions']}")

    def print_payment_report(self, traveler):
        report=traveler.generate_payment_report()
        print(f"\nPayment report of {report['name']} ({report['membership_type']}, {report['discount']:.0%} discount)")
        for row in report["treks"]:
            print(f"  {row['trek_id']:>8} {row['name'][:23]:<24} {row['state']:<10} final price {row['final_price']:>8}"
                  f"   fee if cancelled today {row['cancellation_fee']}")
        print(f"  total: {report['total']}")

    def print_resources(self):
        print("\nVehicles")
        for vehicle in self.vehicles:
            assigned=[f"trek {a['trek'].trek_id} from {a['pickup_point']}" for a in vehicle.assignments]
            print(f"  {vehicle.transport_id} {vehicle.vehicle_type}, {vehicle.seats} seats: {assigned}, "
                  f"conflicts: {vehicle.find_conflicts()}")
        print("Equipment")
        for item in self.equipment:
            loans=[f"{loan['quantity']} to trek {loan['trek'].trek_id}" for loan in item.loans]
            print(f"  {item.equipment_id} {item.name}, {item.total_quantity} owned: {loans}, "
                  f"conflicts: {item.find_conflicts()}")

    # ------------------------------------------------------------------
    # Mode 1: the full season scenario
    # ------------------------------------------------------------------

    # Runs one season of the agency from opening to the final reports, with no input
    def run_season_scenario(self):
        self.load_sample_data()
        agency=self.agency
        trek=self.find_trek
        person=self.find_traveler
        guide=self.find_guide

        self.title(f"Season scenario of {agency.name}, today is {date.today()}")

        self.step("1. The agency opens")
        print(f"  {len(agency.guides)} guides, {len(agency.travelers)} travelers and {len(agency.treks)} treks")
        self.print_treks()
        self.expect_rejected("a second traveler with id 1",
                             lambda: agency.add_traveler(Traveler(1, "Dana Copy", 30, "basic", 5)))

        self.step("2. Guides are assigned")
        self.expect_ok("Noa to Ramon Crater (Negev)", lambda: guide(1).assign_trek(trek(101)))
        self.expect_ok("Noa to Eilat Mountains", lambda: guide(1).assign_trek(trek(105)))
        self.expect_ok("Amir to Mount Arbel (Galilee)", lambda: guide(2).assign_trek(trek(102)))
        self.expect_ok("Amir to Golan Volcanoes", lambda: guide(2).assign_trek(trek(107)))
        self.expect_ok("Maya to Judean Desert Canyons", lambda: guide(3).assign_trek(trek(103)))
        self.expect_ok("Eitan to Carmel Forest", lambda: guide(4).assign_trek(trek(104)))
        self.expect_rejected("Amir to Nahal Amud, on the same day as Mount Arbel",
                             lambda: guide(2).assign_trek(trek(106)))
        self.expect_rejected("Eitan to Nahal Amud, not his region",
                             lambda: trek(106).assign_guide(guide(4)))
        print("  Nahal Amud stays without a guide for now")

        self.step("3. Registrations")
        for traveler_id in (1, 2, 4, 11, 8):
            self.expect_ok(f"{person(traveler_id).name} to Ramon Crater",
                           lambda: person(traveler_id).register_to_trek(trek(101)))
        self.expect_equal("Ramon Crater reached its minimum of 3", trek(101).status, "confirmed")
        self.expect_rejected("Yael (level 4) to Ramon Crater (difficulty 6)",
                             lambda: person(3).register_to_trek(trek(101)))
        for traveler_id in (3, 5, 10, 6):
            self.expect_ok(f"{person(traveler_id).name} to Mount Arbel",
                           lambda: person(traveler_id).register_to_trek(trek(102)))
        self.expect_rejected("Noam to Mount Arbel, which is full", lambda: person(7).register_to_trek(trek(102)))
        self.expect_rejected("Roni to Nahal Amud, on the day of his Mount Arbel trek",
                             lambda: person(10).register_to_trek(trek(106)))
        for traveler_id in (7, 1):
            self.expect_ok(f"{person(traveler_id).name} to Judean Desert Canyons",
                           lambda: person(traveler_id).register_to_trek(trek(103)))
        self.expect_rejected("Omer (level 6) to Judean Desert Canyons (difficulty 8)",
                             lambda: person(2).register_to_trek(trek(103)))
        for traveler_id in (9, 6):
            self.expect_ok(f"{person(traveler_id).name} to Carmel Forest",
                           lambda: person(traveler_id).register_to_trek(trek(104)))
        for traveler_id in (2, 8, 4):
            self.expect_ok(f"{person(traveler_id).name} to Eilat Mountains",
                           lambda: person(traveler_id).register_to_trek(trek(105)))
        for traveler_id in (9, 12):
            self.expect_ok(f"{person(traveler_id).name} to Nahal Amud",
                           lambda: person(traveler_id).register_to_trek(trek(106)))
        for traveler_id in (5, 11):
            self.expect_ok(f"{person(traveler_id).name} to Golan Volcanoes",
                           lambda: person(traveler_id).register_to_trek(trek(107)))
        self.print_treks()

        self.step("4. The waiting list of the full Mount Arbel trek")
        self.expect_ok("Yoni (basic) joins the waiting list first", lambda: trek(102).add_to_waiting_list(person(12)))
        self.expect_ok("Dana (premium) joins second", lambda: trek(102).add_to_waiting_list(person(1)))
        self.expect_rejected("Avi (level 2) waits for a difficulty 3 trek",
                             lambda: trek(102).add_to_waiting_list(person(9)))

        self.step("5. Equipment and vehicles")
        tents=self.find_equipment(1)
        bags=self.find_equipment(2)
        minibus=self.find_vehicle(1)
        jeep=self.find_vehicle(2)
        self.expect_ok("5 tents to Ramon Crater", lambda: tents.loan_to_trek(trek(101), 5))
        self.expect_ok("5 sleeping bags to Ramon Crater", lambda: bags.loan_to_trek(trek(101), 5))
        self.expect_ok("3 tents to Judean Desert Canyons", lambda: tents.loan_to_trek(trek(103), 3))
        self.expect_rejected("13 tents to Eilat Mountains, only 12 are owned",
                             lambda: tents.loan_to_trek(trek(105), 13))
        self.expect_ok("the minibus to Ramon Crater", lambda: minibus.assign_to_trek(trek(101), "Beer Sheva Central Station"))
        self.expect_equal("12 seats are enough for 8 travelers and a guide",
                          Transport.has_enough_seats(trek(101), [minibus]), True)
        self.expect_ok("the jeep to Judean Desert Canyons", lambda: jeep.assign_to_trek(trek(103), "Jerusalem Malha"))
        self.expect_equal("4 seats are not enough for 6 travelers and a guide",
                          Transport.has_enough_seats(trek(103), [jeep]), False)
        self.expect_ok("the minibus joins as well", lambda: minibus.assign_to_trek(trek(103), "Jerusalem Malha"))
        self.expect_equal("4 + 12 seats", Transport.has_enough_seats(trek(103), [jeep, minibus]), True)

        self.step("6. Travelers cancel; the refund depends on the days left")
        rate=self.expect_ok("Shira cancels Mount Arbel, 20 days ahead", lambda: person(5).cancel_trek(102))
        print(f"            refund rate: {rate:.0%}")
        self.expect_equal("Dana (premium) is promoted before Yoni (basic), who waited longer",
                          [t.traveler_id for t in trek(102).participants], [3, 10, 6, 1])
        rate=self.expect_ok("Omer cancels Eilat Mountains, 90 days ahead", lambda: person(2).cancel_trek(105))
        print(f"            refund rate: {rate:.0%}")
        rate=self.expect_ok("Lior cancels Carmel Forest, 12 days ahead", lambda: person(6).cancel_trek(104))
        print(f"            refund rate: {rate:.0%}")
        self.expect_rejected("Lior cancels Carmel Forest again", lambda: person(6).cancel_trek(104))

        self.step("7. A private tour")
        private=self.expect_ok("Yael asks Maya for a 2 day private tour in 75 days",
                               lambda: person(3).request_private_tour(guide(3), self.days_from_today(75), 2))
        self.expect_ok("the agency adds the private tour", lambda: agency.add_trek(private))
        print(f"            {private.name}: {private.region}, difficulty {private.difficulty_level}, price {private.price}")
        self.expect_rejected("Roni asks Maya for a tour while she leads Judean Desert Canyons",
                             lambda: person(10).request_private_tour(guide(3), self.days_from_today(61), 1))

        self.step("8. The agency cancels Carmel Forest, which is below its minimum")
        carmel=trek(104)
        print(f"  Carmel Forest has {len(carmel.participants)} of the {carmel.min_participants} travelers it needs")
        self.expect_ok("cancel Carmel Forest", lambda: carmel.cancel_trek())
        self.expect_equal("Carmel Forest left Avi's current treks", carmel not in person(9).current_treks, True)
        self.expect_equal("Carmel Forest left Eitan's assigned treks", carmel not in guide(4).assigned_treks, True)
        self.expect_rejected("register to the cancelled trek", lambda: person(12).register_to_trek(carmel))

        self.step("9. Treks end (their dates move to the past, today stays)")
        self.expect_ok("Ramon Crater ended 12 days ago and is completed", lambda: self.finish_trek(trek(101), 12))
        self.expect_ok("Golan Volcanoes ended yesterday and is completed", lambda: self.finish_trek(trek(107), 1))
        self.expect_equal("Michal completed both", [t.trek_id for t in person(11).completed_treks], [101, 107])
        self.expect_rejected("complete Judean Desert Canyons, which has not ended", lambda: trek(103).complete_trek())
        self.expect_equal("the minibus has no conflicts after the move", minibus.find_conflicts(), [])

        self.step("10. End of season reports")
        self.print_treks()
        self.print_season_schedule()
        self.print_membership_report()
        for g in agency.guides:
            self.print_guide_statistics(g)
        self.print_payment_report(person(1))
        self.print_payment_report(person(3))
        print("\nSearch")
        for term in ("galilee", "Noa", 8):
            print(f"  '{term}': {[t.name for t in agency.search_treks(term)]}")
        self.print_resources()

        self.print_summary("Season scenario")

    # ------------------------------------------------------------------
    # Mode 3: edge case scenarios, each with its own small agency
    # ------------------------------------------------------------------

    # Builds a small trek for an edge case; the dates are days from today
    def make_trek(self, trek_id, days_ahead, region="Negev", difficulty=3, min_p=2, max_p=10, duration=2):
        return Trek(trek_id, f"Edge trek {trek_id}", region, difficulty, min_p, max_p,
                    self.days_from_today(days_ahead), duration, 800)

    def make_traveler(self, traveler_id, membership="basic", experience=5):
        return Traveler(traveler_id, f"Traveler {traveler_id}", 30, membership, experience)

    def make_guide(self, guide_id, max_monthly=4):
        return Guide(guide_id, f"Guide {guide_id}", ["Negev"], 5, 5, max_monthly)

    def edge_waiting_list(self):
        self.step("Full trek: the waiting list is promoted by membership, then by arrival")
        trek=self.make_trek(1, 30, max_p=2)
        first, second=self.make_traveler(1), self.make_traveler(2)
        trek.register(first)
        trek.register(second)
        waiting=[self.make_traveler(3, "basic"), self.make_traveler(4, "annual"),
                 self.make_traveler(5, "premium"), self.make_traveler(6, "premium")]
        for traveler in waiting:
            trek.add_to_waiting_list(traveler)
        print(f"  waiting in order: {[(t.traveler_id, t.membership_type) for t in trek.waiting_list]}")
        trek.cancel_registration(1)
        self.expect_equal("first freed place goes to the first premium", trek.participants[-1].traveler_id, 5)
        trek.cancel_registration(2)
        self.expect_equal("second goes to the next premium", trek.participants[-1].traveler_id, 6)
        trek.cancel_registration(5)
        self.expect_equal("then annual comes before the basic who waited longest", trek.participants[-1].traveler_id, 4)
        busy=self.make_traveler(7, "premium")
        self.make_trek(2, 30, min_p=1).register(busy)
        full=self.make_trek(3, 30, max_p=1, min_p=1)
        full.register(self.make_traveler(8))
        full.add_to_waiting_list(busy)
        full.add_to_waiting_list(self.make_traveler(9, "basic"))
        full.cancel_registration(8)
        self.expect_equal("a premium who became busy is skipped, the basic gets the place",
                          full.participants[0].traveler_id, 9)

    def edge_schedule_conflicts(self):
        self.step("Schedule conflicts of travelers and guides")
        guide=self.make_guide(1)
        traveler=self.make_traveler(1)
        first=self.make_trek(1, 30, duration=3)
        first.assign_guide(guide)
        first.register(traveler)
        self.expect_rejected("traveler: a trek on the last day of the first",
                             lambda: self.make_trek(2, 32).register(traveler))
        self.expect_ok("traveler: a trek the day after the first ends", lambda: self.make_trek(3, 33).register(traveler))
        self.expect_rejected("guide: a trek that starts a day before and overlaps",
                             lambda: self.make_trek(4, 29).assign_guide(guide))
        self.expect_rejected("move the first trek onto the traveler's second trek",
                             lambda: first.set_dates(self.days_from_today(33), 1))

    def edge_monthly_limit(self):
        self.step("A guide's monthly limit, counted by departure month")
        month_start=(date.today().replace(day=1)+timedelta(days=62)).replace(day=1)
        guide=self.make_guide(1, max_monthly=2)
        treks=[Trek(i, f"Month trek {i}", "Negev", 3, 1, 5, month_start+timedelta(days=7*(i-1)), 2, 500) for i in (1, 2, 3)]
        self.expect_ok("first trek of the month", lambda: guide.assign_trek(treks[0]))
        self.expect_ok("second trek of the month", lambda: guide.assign_trek(treks[1]))
        self.expect_rejected("third trek of the same month", lambda: guide.assign_trek(treks[2]))
        next_month=Trek(4, "Next month", "Negev", 3, 1, 5, month_start+timedelta(days=40), 2, 500)
        self.expect_ok("a trek in the next month", lambda: guide.assign_trek(next_month))

    def edge_refund_tiers(self):
        self.step("Refund tiers by days before departure, including the edges")
        for days, rate in ((40, 1.0), (30, 1.0), (29, 0.75), (14, 0.75), (13, 0.5), (7, 0.5), (6, 0.0), (1, 0.0)):
            self.expect_equal(f"{days} days before", self.make_trek(days, days).calculate_refund_rate(), rate)

    def edge_minimum(self):
        self.step("A trek drops below its minimum and the agency cancels it")
        trek=self.make_trek(1, 30, min_p=3)
        guide=self.make_guide(1)
        trek.assign_guide(guide)
        travelers=[self.make_traveler(i) for i in (1, 2, 3)]
        for traveler in travelers:
            trek.register(traveler)
        self.expect_equal("3 of minimum 3", trek.status, "confirmed")
        travelers[0].cancel_trek(1)
        self.expect_equal("after one cancellation, 2 of 3", trek.status, "planned")
        self.expect_rejected("complete a trek that is not confirmed", lambda: trek.complete_trek())
        self.expect_ok("the agency cancels it", lambda: trek.cancel_trek())
        self.expect_equal("everyone is released", [len(t.current_treks) for t in travelers], [0, 0, 0])
        self.expect_equal("the guide is free again", guide.assigned_treks, [])

    def edge_resources(self):
        self.step("Moving a trek can leave vehicles or equipment short")
        tents=Equipment(1, "Tent", 10)
        bus=Transport(1, "Minibus", 12)
        first=self.make_trek(1, 30)
        second=self.make_trek(2, 50)
        tents.loan_to_trek(first, 7)
        tents.loan_to_trek(second, 7)
        bus.assign_to_trek(first, "Tel Aviv")
        bus.assign_to_trek(second, "Haifa")
        self.expect_rejected("move the second trek onto the first, checking its tents",
                             lambda: second.set_dates(self.days_from_today(30), 2, equipment=[tents]))
        self.expect_rejected("the same move, checking its bus", lambda: second.set_dates(self.days_from_today(30), 2, vehicles=[bus]))
        second.set_dates(self.days_from_today(30), 2)
        print("  the move without the lists is allowed, so the clash shows up in find_conflicts:")
        self.expect_equal("tent conflicts", tents.find_conflicts(), [1, 2])
        self.expect_equal("bus conflicts", bus.find_conflicts(), [(1, 2)])
        first.cancel_trek()
        self.expect_equal("cancelling the first trek frees its tents and bus", (tents.find_conflicts(), bus.find_conflicts()), ([], []))

    def edge_closed_treks(self):
        self.step("Nothing changes a cancelled or completed trek")
        cancelled=self.make_trek(1, 30)
        cancelled.cancel_trek()
        completed=self.make_trek(2, 40, min_p=1)
        traveler=self.make_traveler(1)
        completed.register(traveler)
        completed.set_dates(self.days_from_today(-5), 2)
        completed.complete_trek()
        for name, trek in (("cancelled", cancelled), ("completed", completed)):
            self.expect_rejected(f"register to a {name} trek", lambda: trek.register(self.make_traveler(9)))
            self.expect_rejected(f"assign a guide to a {name} trek", lambda: trek.assign_guide(self.make_guide(9)))
            self.expect_rejected(f"move a {name} trek", lambda: trek.set_dates(self.days_from_today(60), 2))
            self.expect_rejected(f"cancel a {name} trek", lambda: trek.cancel_trek())
            self.expect_rejected(f"lend tents to a {name} trek", lambda: Equipment(1, "Tent", 5).loan_to_trek(trek, 1))
        self.expect_rejected("register to a trek that already departed", lambda: self.make_trek(3, 0).register(traveler))

    def edge_invalid_input(self):
        self.step("Invalid input is rejected before anything is created")
        self.expect_rejected("trek with minimum above maximum",
                             lambda: Trek(1, "A", "Negev", 3, 9, 5, self.days_from_today(10), 2, 100))
        self.expect_rejected("trek in an unknown region",
                             lambda: Trek(1, "A", "Sinai", 3, 1, 5, self.days_from_today(10), 2, 100))
        self.expect_rejected("traveler aged 130", lambda: Traveler(1, "A", 130, "basic", 5))
        self.expect_rejected("guide with the same region twice", lambda: Guide(1, "A", ["Negev", "Negev"], 5, 5, 2))
        self.expect_rejected("vehicle with one seat", lambda: Transport(1, "Bike", 1))
        self.expect_rejected("search with an empty term", lambda: Agency("A").search_treks(" "))

    # Returns the edge case scenarios in menu order, as pairs of a title and a method
    def get_edge_cases(self):
        return [("Waiting list priority", self.edge_waiting_list),
                ("Schedule conflicts", self.edge_schedule_conflicts),
                ("Guide's monthly limit", self.edge_monthly_limit),
                ("Refund tiers", self.edge_refund_tiers),
                ("Trek below its minimum", self.edge_minimum),
                ("Vehicles and equipment after a move", self.edge_resources),
                ("Cancelled and completed treks", self.edge_closed_treks),
                ("Invalid input", self.edge_invalid_input)]

    # Runs every edge case scenario and prints one summary
    def run_all_edge_cases(self):
        self.title("Edge case scenarios")
        for name, scenario in self.get_edge_cases():
            scenario()
        self.print_summary("Edge case scenarios")

    # ------------------------------------------------------------------
    # Mode 2: the interactive menu
    # ------------------------------------------------------------------

    # Input helpers ask again until the value can be read, so a typing mistake never stops the simulation
    def ask_text(self, prompt):
        while True:
            text=input(f"{prompt}: ").strip()
            if text:
                return text
            print("  please type a value")

    def ask_int(self, prompt):
        while True:
            text=input(f"{prompt}: ").strip()
            try:
                return int(text)
            except ValueError:
                print("  please type a whole number")

    def ask_number(self, prompt):
        while True:
            text=input(f"{prompt}: ").strip()
            try:
                value=float(text)
            except ValueError:
                print("  please type a number")
                continue
            # A whole number stays an int, so a price of 300 is shown as 300
            if value.is_integer():
                return int(value)
            return value

    # Accepts a date as YYYY-MM-DD, or as +N / -N days from today
    def ask_date(self, prompt):
        while True:
            text=input(f"{prompt} (YYYY-MM-DD, or +N days from today): ").strip()
            try:
                if text.startswith(("+", "-")):
                    return self.days_from_today(int(text))
                return date.fromisoformat(text)
            except ValueError:
                print("  please type a date such as 2027-03-15 or +30")

    def ask_list(self, prompt):
        return [part.strip() for part in self.ask_text(f"{prompt} (comma separated)").split(",")]

    # Each menu action is a method; the menu catches ValueError, so a rejected action prints its reason and the menu goes on
    def action_add_traveler(self):
        traveler=Traveler(self.ask_int("traveler id"), self.ask_text("full name"), self.ask_int("age"),
                          self.ask_text(f"membership {Traveler.VALID_MEMBERSHIPS}"), self.ask_int("experience 1-10"))
        self.agency.add_traveler(traveler)
        print(f"  added traveler {traveler.traveler_id}")

    def action_add_guide(self):
        guide=Guide(self.ask_int("guide id"), self.ask_text("full name"), self.ask_list("specialties"),
                    self.ask_int("certification 1-10"), self.ask_number("years of experience"),
                    self.ask_int("most treks per month"))
        self.agency.add_guide(guide)
        print(f"  added guide {guide.guide_id}")

    def action_add_trek(self):
        print(f"  regions: {', '.join(Trek.VALID_REGIONS)}")
        trek=Trek(self.ask_int("trek id"), self.ask_text("name"), self.ask_text("region"),
                  self.ask_int("difficulty 1-10"), self.ask_int("minimum participants"),
                  self.ask_int("maximum participants"), self.ask_date("start date"),
                  self.ask_int("duration in days"), self.ask_number("price"))
        self.agency.add_trek(trek)
        print(f"  added trek {trek.trek_id}")

    def action_register(self):
        traveler=self.find_traveler(self.ask_int("traveler id"))
        trek=self.find_trek(self.ask_int("trek id"))
        if not trek.has_capacity() and trek.is_active():
            answer=input("  the trek is full, join the waiting list? (y/n): ").strip().lower()
            if answer=="y":
                trek.add_to_waiting_list(traveler)
                print(f"  {traveler.name} is number {len(trek.waiting_list)} on the waiting list")
            return
        traveler.register_to_trek(trek)
        print(f"  {traveler.name} registered, the trek is {trek.status}")

    def action_cancel_registration(self):
        traveler=self.find_traveler(self.ask_int("traveler id"))
        trek_id=self.ask_int("trek id")
        rate=traveler.cancel_trek(trek_id)
        print(f"  cancelled with a refund of {rate:.0%}; the trek is {self.find_trek(trek_id).status}")

    def action_assign_guide(self):
        guide=self.find_guide(self.ask_int("guide id"))
        guide.assign_trek(self.find_trek(self.ask_int("trek id")))
        print("  guide assigned")

    def action_change_dates(self):
        trek=self.find_trek(self.ask_int("trek id"))
        trek.set_dates(self.ask_date("new start date"), self.ask_int("duration in days"),
                       self.get_trek_vehicles(trek), self.get_trek_equipment(trek))
        print(f"  the trek now runs {trek.start_date} to {trek.get_end_date()}")

    def action_cancel_trek(self):
        trek=self.find_trek(self.ask_int("trek id"))
        trek.cancel_trek()
        print("  trek cancelled, everyone was released")

    def action_finish_trek(self):
        trek=self.find_trek(self.ask_int("trek id"))
        self.finish_trek(trek, self.ask_int("how many days ago did it end (1 = yesterday)"))
        print(f"  the trek ended on {trek.get_end_date()} and is completed")

    def action_private_tour(self):
        traveler=self.find_traveler(self.ask_int("traveler id"))
        guide=self.find_guide(self.ask_int("guide id"))
        trek=traveler.request_private_tour(guide, self.ask_date("start date"), self.ask_int("duration in days"))
        self.agency.add_trek(trek)
        print(f"  private tour {trek.trek_id} created: {trek.region}, difficulty {trek.difficulty_level}, price {trek.price}")

    def action_lend_equipment(self):
        item=self.find_equipment(self.ask_int(f"equipment id {[(i.equipment_id, i.name) for i in self.equipment]}"))
        trek=self.find_trek(self.ask_int("trek id"))
        print(f"  {item.get_available_quantity(trek.start_date, trek.duration_days)} free on the trek's dates")
        item.loan_to_trek(trek, self.ask_int("quantity"))
        print("  lent")

    def action_assign_vehicle(self):
        vehicle=self.find_vehicle(self.ask_int(f"vehicle id {[(v.transport_id, v.vehicle_type) for v in self.vehicles]}"))
        trek=self.find_trek(self.ask_int("trek id"))
        vehicle.assign_to_trek(trek, self.ask_text("pickup point"))
        enough=Transport.has_enough_seats(trek, self.get_trek_vehicles(trek))
        print(f"  assigned; the trek's vehicles seat everyone: {enough}")

    def action_search(self):
        term=input("search term (text, or a whole number for difficulty): ").strip()
        if term.isdigit():
            term=int(term)
        results=self.agency.search_treks(term)
        print(f"  {len(results)} found: {[f'{t.trek_id} {t.name}' for t in results]}")

    def action_edge_cases(self):
        cases=self.get_edge_cases()
        for number, (name, scenario) in enumerate(cases, 1):
            print(f"  {number}. {name}")
        print(f"  {len(cases)+1}. Run all")
        choice=self.ask_int("edge case")
        if choice==len(cases)+1:
            self.run_all_edge_cases()
        elif 1<=choice<=len(cases):
            cases[choice-1][1]()
            self.print_summary(cases[choice-1][0])
        else:
            print("  no such edge case")

    def action_reset(self):
        self.load_sample_data()
        print("  sample data reloaded, nothing is registered")

    # Returns the menu as pairs of a label and a method, grouped by kind
    def get_menu(self):
        return [
            ("View", None),
            ("Show treks", self.print_treks),
            ("Show travelers", self.print_travelers),
            ("Show guides", self.print_guides),
            ("Trek details", lambda: self.print_trek_details(self.find_trek(self.ask_int("trek id")))),
            ("Show vehicles and equipment", self.print_resources),
            ("Create", None),
            ("Add a traveler", self.action_add_traveler),
            ("Add a guide", self.action_add_guide),
            ("Add a trek", self.action_add_trek),
            ("Registrations", None),
            ("Register a traveler (or join the waiting list)", self.action_register),
            ("Cancel a registration", self.action_cancel_registration),
            ("Request a private tour", self.action_private_tour),
            ("Trek management", None),
            ("Assign a guide", self.action_assign_guide),
            ("Change a trek's dates", self.action_change_dates),
            ("Cancel a trek (agency)", self.action_cancel_trek),
            ("Finish a trek (it moves to the past and is completed)", self.action_finish_trek),
            ("Lend equipment to a trek", self.action_lend_equipment),
            ("Assign a vehicle to a trek", self.action_assign_vehicle),
            ("Reports", None),
            ("Season schedule", self.print_season_schedule),
            ("Membership report", self.print_membership_report),
            ("Guide statistics", lambda: self.print_guide_statistics(self.find_guide(self.ask_int("guide id")))),
            ("Payment report", lambda: self.print_payment_report(self.find_traveler(self.ask_int("traveler id")))),
            ("Search treks", self.action_search),
            ("More", None),
            ("Edge case scenarios", self.action_edge_cases),
            ("Reset to the sample data", self.action_reset),
        ]

    # Shows the menu until the user chooses 0; input that ends, as from a file, also ends the menu
    def run_menu(self):
        self.title(f"Interactive menu of {self.agency.name}, today is {date.today()}")
        actions=[]
        for label, action in self.get_menu():
            if action is not None:
                actions.append((label, action))
        while True:
            print()
            number=0
            for label, action in self.get_menu():
                if action is None:
                    print(f"  [{label}]")
                else:
                    number+=1
                    print(f"  {number:>2}. {label}")
            print("   0. Back to the start menu")
            try:
                choice=input("choice: ").strip()
                if choice=="0":
                    return
                if not choice.isdigit() or not 1<=int(choice)<=len(actions):
                    print("  please choose a number from the menu")
                    continue
                label, action=actions[int(choice)-1]
                print(f"\n>> {label}")
                action()
            except ValueError as error:
                print(f"  REJECTED: {error}")
            except EOFError:
                print("\nno more input, leaving the menu")
                return


    # ------------------------------------------------------------------
    # Start menu
    # ------------------------------------------------------------------

    # Shows the start menu and runs the chosen mode, then returns to it; 0, or input that ends, exits
    def run(self):
        while True:
            print("\nField trek agency simulation")
            print("  1. season  Full season scenario, runs on its own")
            print("  2. menu    Interactive menu")
            print("  3. edge    All edge case scenarios")
            print("  0. exit")
            try:
                mode=input("choice: ").strip().lower()
            except EOFError:
                print("\nno more input, the simulation ends")
                return
            if mode in ("1", "season"):
                self.run_season_scenario()
            elif mode in ("2", "menu"):
                self.run_menu()
            elif mode in ("3", "edge"):
                self.run_all_edge_cases()
            elif mode in ("0", "exit"):
                return
            else:
                print("  please choose 1, 2, 3 or 0, or type season, menu, edge or exit")


# Runs the simulation from its start menu
def main():
    AgencySimulation().run()


if __name__=="__main__":
    main()
