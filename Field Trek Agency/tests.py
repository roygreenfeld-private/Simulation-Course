from datetime import date, datetime, timedelta
from pprint import pprint
from trek import Trek
from traveler import Traveler
from guide import Guide
from agency import Agency
from equipment import Equipment
from transport import Transport

# Demonstrations of every class and method: a valid use, edge cases and rejected actions.
# Every date is relative to the real date.today(), so the file gives the same results on any day it runs.
# To show the past, a trek's dates are moved with set_dates; "today" itself never changes.

TODAY=date.today()
# The first day of the month two months from now, for checks that need two treks in one month
MONTH_START=(TODAY.replace(day=1)+timedelta(days=62)).replace(day=1)

# Counts the results, so the summary at the end shows whether anything behaved unexpectedly
results={"passed": 0, "failed": 0}


# Returns the date the given number of days from today, negative for the past
def days_from_today(days):
    return TODAY+timedelta(days=days)


# Prints a section title
def section(title):
    print(f"\n{'='*70}\n{title}\n{'='*70}")


# Runs an action that should succeed and prints what it returned
# The action is passed as a lambda, so the call runs only inside the try block
def expect_ok(description, action):
    try:
        result=action()
        if result is None:
            print(f"  OK        {description}")
        else:
            print(f"  OK        {description} -> {result}")
        results["passed"]+=1
        return result
    except ValueError as error:
        print(f"  FAILED    {description}: rejected unexpectedly ({error})")
        results["failed"]+=1


# Runs an action that should be rejected and prints the reason the class gave
def expect_rejected(description, action):
    try:
        action()
        print(f"  FAILED    {description}: accepted, but a rejection was expected")
        results["failed"]+=1
    except ValueError as error:
        print(f"  REJECTED  {description}: {error}")
        results["passed"]+=1


# Prints whether a value matches what the demonstration expects
def expect_equal(description, actual, expected):
    if actual==expected:
        print(f"  OK        {description} -> {actual}")
        results["passed"]+=1
    else:
        print(f"  FAILED    {description}: got {actual}, expected {expected}")
        results["failed"]+=1


# Short helpers that build valid objects, so each demonstration changes only what it checks
def make_trek(trek_id, days_ahead, region="Negev", difficulty=3, min_p=2, max_p=10, duration=3, price=1000):
    return Trek(trek_id, f"Trek {trek_id}", region, difficulty, min_p, max_p,
                days_from_today(days_ahead), duration, price)


def make_traveler(traveler_id, membership="basic", experience=5):
    return Traveler(traveler_id, f"Traveler {traveler_id}", 30, membership, experience)


def make_guide(guide_id, specialties=None, max_monthly=4):
    if specialties is None:
        specialties=["Negev"]
    return Guide(guide_id, f"Guide {guide_id}", specialties, 5, 8, max_monthly)


# ======================================================================
section("1. Constructors: valid objects and invalid input")
# ======================================================================

print("\nTrek")
trek=expect_ok("valid trek", lambda: make_trek(1, 40))
print(f"            new trek starts empty: status={trek.status}, guide={trek.guide}, "
      f"participants={trek.participants}, waiting_list={trek.waiting_list}")
expect_ok("trek in the past is allowed (decision of open question 2)", lambda: make_trek(2, -30))
expect_rejected("id 0", lambda: Trek(0, "A", "Negev", 3, 1, 5, days_from_today(10), 2, 100))
expect_rejected("id as text", lambda: Trek("1", "A", "Negev", 3, 1, 5, days_from_today(10), 2, 100))
expect_rejected("empty name", lambda: Trek(1, "   ", "Negev", 3, 1, 5, days_from_today(10), 2, 100))
expect_rejected("unknown region", lambda: Trek(1, "A", "Alps", 3, 1, 5, days_from_today(10), 2, 100))
expect_rejected("difficulty 11", lambda: Trek(1, "A", "Negev", 11, 1, 5, days_from_today(10), 2, 100))
expect_rejected("difficulty 2.5", lambda: Trek(1, "A", "Negev", 2.5, 1, 5, days_from_today(10), 2, 100))
expect_rejected("minimum above maximum", lambda: Trek(1, "A", "Negev", 3, 6, 5, days_from_today(10), 2, 100))
expect_rejected("minimum 0", lambda: Trek(1, "A", "Negev", 3, 0, 5, days_from_today(10), 2, 100))
expect_rejected("date as text", lambda: Trek(1, "A", "Negev", 3, 1, 5, "2027-01-01", 2, 100))
expect_rejected("datetime instead of date", lambda: Trek(1, "A", "Negev", 3, 1, 5, datetime.now(), 2, 100))
expect_rejected("duration 0", lambda: Trek(1, "A", "Negev", 3, 1, 5, days_from_today(10), 0, 100))
expect_rejected("negative price", lambda: Trek(1, "A", "Negev", 3, 1, 5, days_from_today(10), 2, -100))
expect_rejected("price True", lambda: Trek(1, "A", "Negev", 3, 1, 5, days_from_today(10), 2, True))
expect_rejected("infinite price", lambda: Trek(1, "A", "Negev", 3, 1, 5, days_from_today(10), 2, float("inf")))

print("\nTraveler")
traveler=expect_ok("valid traveler", lambda: Traveler(1, "Dana Levi", 28, "annual", 6))
print(f"            new traveler starts empty: current_treks={traveler.current_treks}, "
      f"completed_treks={traveler.completed_treks}")
expect_rejected("negative id", lambda: Traveler(-1, "Dana", 28, "basic", 5))
expect_rejected("empty name", lambda: Traveler(1, "", 28, "basic", 5))
expect_rejected("age 0", lambda: Traveler(1, "Dana", 0, "basic", 5))
expect_rejected("age as text", lambda: Traveler(1, "Dana", "28", "basic", 5))
expect_rejected("age 121, above the highest realistic age", lambda: Traveler(1, "Dana", 121, "basic", 5))
expect_ok("age 120 (edge)", lambda: Traveler(1, "Dana", 120, "basic", 5).age)
expect_rejected("unknown membership", lambda: Traveler(1, "Dana", 28, "gold", 5))
expect_rejected("experience 0", lambda: Traveler(1, "Dana", 28, "basic", 0))

print("\nGuide")
regions=["Negev", "Arava"]
guide=expect_ok("valid guide", lambda: Guide(1, "Yossi Cohen", regions, 7, 4.5, 3))
regions.append("Carmel")
expect_equal("the guide keeps its own copy of the specialties list", guide.specialties, ["Negev", "Arava"])
expect_rejected("empty specialties", lambda: Guide(1, "Yossi", [], 7, 4, 3))
expect_rejected("specialties as text", lambda: Guide(1, "Yossi", "Negev", 7, 4, 3))
expect_rejected("unknown region", lambda: Guide(1, "Yossi", ["Alps"], 7, 4, 3))
expect_rejected("the same region twice", lambda: Guide(1, "Yossi", ["Negev", "Negev"], 7, 4, 3))
expect_rejected("certification 11", lambda: Guide(1, "Yossi", ["Negev"], 11, 4, 3))
expect_rejected("negative experience", lambda: Guide(1, "Yossi", ["Negev"], 7, -1, 3))
expect_rejected("monthly limit 0", lambda: Guide(1, "Yossi", ["Negev"], 7, 4, 0))

print("\nAgency")
expect_ok("valid agency", lambda: Agency("Desert Steps").name)
expect_rejected("empty name", lambda: Agency(""))

print("\nEquipment")
expect_ok("valid equipment", lambda: Equipment(1, "Tent", 20).total_quantity)
expect_rejected("quantity 0", lambda: Equipment(1, "Tent", 0))
expect_rejected("empty name", lambda: Equipment(1, " ", 5))

print("\nTransport")
expect_ok("valid vehicle", lambda: Transport(1, "Minibus", 20).seats)
expect_rejected("1 seat", lambda: Transport(1, "Jeep", 1))
expect_rejected("empty vehicle type", lambda: Transport(1, "", 5))


# ======================================================================
section("2. Trek: guide and dates")
# ======================================================================

print("\nassign_guide / Guide.assign_trek")
trek=make_trek(10, 30, region="Negev")
guide=make_guide(10, ["Negev"])
expect_ok("assign a Negev guide to a Negev trek", lambda: trek.assign_guide(guide))
expect_equal("both sides are updated", (trek.guide is guide, trek in guide.assigned_treks), (True, True))
expect_rejected("a second guide for the same trek", lambda: trek.assign_guide(make_guide(11)))
expect_rejected("a guide from another region", lambda: make_trek(11, 60, region="Galilee").assign_guide(guide))
expect_rejected("a guide busy on an overlapping trek", lambda: guide.assign_trek(make_trek(12, 31)))
expect_rejected("an object that is not a guide", lambda: make_trek(13, 60).assign_guide("Yossi"))
expect_rejected("Guide.assign_trek with an object that is not a trek", lambda: guide.assign_trek("trek"))

limited=make_guide(12, max_monthly=1)
first=Trek(14, "Month A", "Negev", 3, 1, 5, MONTH_START, 2, 500)
second=Trek(15, "Month B", "Negev", 3, 1, 5, MONTH_START+timedelta(days=10), 2, 500)
expect_ok("guide with a monthly limit of 1 takes one trek", lambda: limited.assign_trek(first))
expect_rejected("a second trek in the same month", lambda: limited.assign_trek(second))

print("\nset_dates")
trek=make_trek(16, 30)
guide=make_guide(16)
trek.assign_guide(guide)
make_trek(17, 50).assign_guide(guide)
expect_ok("move the trek 5 days later", lambda: trek.set_dates(days_from_today(35), 4))
expect_equal("new dates are kept", (trek.start_date, trek.duration_days), (days_from_today(35), 4))
expect_rejected("move onto another trek of the same guide", lambda: trek.set_dates(days_from_today(49), 3))
expect_equal("a rejected move keeps the old dates", trek.start_date, days_from_today(35))
expect_rejected("duration as text", lambda: trek.set_dates(days_from_today(40), "3"))

busy=make_traveler(16)
moving=make_trek(18, 70, region="Galilee", min_p=1)
moving.register(busy)
make_trek(19, 90, region="Galilee", min_p=1).register(busy)
expect_rejected("move onto another trek of a participant", lambda: moving.set_dates(days_from_today(90), 2))


# ======================================================================
section("3. Trek: registration, capacity and waiting list")
# ======================================================================

trek=make_trek(20, 30, difficulty=5, min_p=2, max_p=2)
dana=make_traveler(20, experience=7)
noam=make_traveler(21, experience=5)
beginner=make_traveler(22, experience=2)

print("\nhas_capacity / is_suitable")
expect_equal("empty trek has room", trek.has_capacity(), True)
expect_equal("experience 7 suits difficulty 5", trek.is_suitable(dana), True)
expect_equal("experience 5 suits difficulty 5 (equal is enough)", trek.is_suitable(noam), True)
expect_equal("experience 2 does not suit difficulty 5", trek.is_suitable(beginner), False)

print("\nregister / Traveler.register_to_trek / update_status")
expect_ok("register the first traveler", lambda: trek.register(dana))
expect_equal("one participant is below the minimum of 2", trek.status, "planned")
expect_ok("second traveler registers from the traveler side", lambda: noam.register_to_trek(trek))
expect_equal("the minimum is reached", trek.status, "confirmed")
expect_equal("both sides are updated", (noam in trek.participants, trek in noam.current_treks), (True, True))
expect_equal("the trek is full", trek.has_capacity(), False)
expect_rejected("register to a full trek", lambda: trek.register(make_traveler(23)))
expect_rejected("register the same traveler twice", lambda: trek.register(dana))
expect_rejected("an unsuitable traveler", lambda: make_trek(21, 30, difficulty=5).register(beginner))
expect_rejected("a traveler with an overlapping trek", lambda: make_trek(22, 31).register(dana))
expect_rejected("a trek that already departed", lambda: make_trek(23, -1).register(make_traveler(24)))
expect_rejected("an object that is not a traveler", lambda: make_trek(24, 30).register("Dana"))
expect_rejected("register_to_trek with an object that is not a trek", lambda: dana.register_to_trek("trek"))

print("\nadd_to_waiting_list")
basic=make_traveler(25, "basic")
premium=make_traveler(26, "premium")
expect_ok("basic traveler waits first", lambda: trek.add_to_waiting_list(basic))
expect_ok("premium traveler waits second", lambda: trek.add_to_waiting_list(premium))
expect_rejected("wait twice", lambda: trek.add_to_waiting_list(basic))
expect_rejected("a registered traveler waits", lambda: trek.add_to_waiting_list(dana))
expect_rejected("an unsuitable traveler waits", lambda: trek.add_to_waiting_list(beginner))
expect_rejected("wait for a trek that still has room", lambda: make_trek(25, 30).add_to_waiting_list(basic))

print("\ncancel_registration / promote_from_waiting_list")
expect_ok("Dana cancels", lambda: trek.cancel_registration(dana.traveler_id))
expect_equal("premium is promoted before basic, who arrived earlier",
             [t.traveler_id for t in trek.participants], [21, 26])
expect_equal("basic is still waiting", [t.traveler_id for t in trek.waiting_list], [25])
expect_equal("Dana's own list no longer has the trek", trek in dana.current_treks, False)
expect_rejected("cancel a traveler who is not registered", lambda: trek.cancel_registration(999))
expect_ok("promote when the trek is full does nothing", lambda: trek.promote_from_waiting_list())
expect_equal("nothing changed", len(trek.participants), 2)

print("\nupdate_status back to planned")
expect_ok("Noam cancels, then basic is promoted", lambda: trek.cancel_registration(noam.traveler_id))
small=make_trek(26, 30, min_p=2, max_p=5)
solo=make_traveler(27)
small.register(solo)
small.register(make_traveler(28))
expect_equal("2 of minimum 2", small.status, "confirmed")
small.cancel_registration(28)
expect_equal("after a cancellation, 1 of minimum 2", small.status, "planned")


# ======================================================================
section("4. Trek: refunds, cancellation and completion")
# ======================================================================

print("\ncalculate_refund_rate (by real today, the trek dates set the distance)")
expect_equal("40 days before departure", make_trek(30, 40).calculate_refund_rate(), 1.0)
expect_equal("30 days before departure (edge)", make_trek(31, 30).calculate_refund_rate(), 1.0)
expect_equal("20 days before departure", make_trek(32, 20).calculate_refund_rate(), 0.75)
expect_equal("10 days before departure", make_trek(33, 10).calculate_refund_rate(), 0.5)
expect_equal("7 days before departure (edge)", make_trek(34, 7).calculate_refund_rate(), 0.5)
expect_equal("3 days before departure", make_trek(35, 3).calculate_refund_rate(), 0.0)
expect_rejected("cancel date as text", lambda: make_trek(36, 10).calculate_refund_rate("today"))

print("\nTraveler.cancel_trek returns the refund rate")
trek=make_trek(37, 20)
traveler=make_traveler(30)
trek.register(traveler)
expect_equal("cancel 20 days ahead", traveler.cancel_trek(37), 0.75)
expect_rejected("cancel a trek the traveler is not registered to", lambda: traveler.cancel_trek(37))

print("\ncancel_trek (by the agency)")
trek=make_trek(38, 30, min_p=1, max_p=1)
guide=make_guide(30)
trek.assign_guide(guide)
first=make_traveler(31)
waiting=make_traveler(32)
trek.register(first)
trek.add_to_waiting_list(waiting)
expect_ok("cancel the trek", lambda: trek.cancel_trek())
expect_equal("status", trek.status, "cancelled")
expect_equal("participants and waiting list are released", (trek.participants, trek.waiting_list), ([], []))
expect_equal("the traveler is free again", first.current_treks, [])
expect_equal("the guide is released", (trek.guide, trek in guide.assigned_treks), (None, False))
expect_rejected("cancel twice", lambda: trek.cancel_trek())
expect_rejected("register to a cancelled trek", lambda: trek.register(make_traveler(33)))
expect_rejected("move a cancelled trek", lambda: trek.set_dates(days_from_today(60), 2))

print("\ncomplete_trek / Traveler.add_completed_trek")
trek=make_trek(39, 30, min_p=2)
guide=make_guide(31)
trek.assign_guide(guide)
hikers=[make_traveler(34), make_traveler(35)]
for hiker in hikers:
    trek.register(hiker)
expect_rejected("complete before the trek ended", lambda: trek.complete_trek())
expect_rejected("add_completed_trek before the trek is completed", lambda: hikers[0].add_completed_trek(39))
# The registration happened while the trek was in the future; now its dates move to the past, so it has ended
expect_ok("move the trek to 10 days ago", lambda: trek.set_dates(days_from_today(-10), 3))
expect_ok("complete the trek", lambda: trek.complete_trek())
expect_equal("status", trek.status, "completed")
expect_equal("every participant moved it to completed_treks",
             [(trek in h.completed_treks, trek in h.current_treks) for h in hikers], [(True, False), (True, False)])
expect_rejected("complete twice", lambda: trek.complete_trek())
expect_rejected("complete a planned trek", lambda: make_trek(40, -10).complete_trek())
expect_rejected("remove a completed trek from its guide", lambda: guide.remove_trek(39))
expect_rejected("add_completed_trek for a trek the traveler never had", lambda: hikers[0].add_completed_trek(999))


# ======================================================================
section("5. Traveler: availability, private tour and payments")
# ======================================================================

traveler=make_traveler(40, "premium", experience=6)
trek=make_trek(41, 30, price=1200)
trek.register(traveler)

print("\nis_available")
expect_equal("free on other dates", traveler.is_available(days_from_today(60), 3), True)
expect_equal("busy on the trek dates", traveler.is_available(days_from_today(31), 1), False)
expect_rejected("invalid duration", lambda: traveler.is_available(days_from_today(60), 0))

print("\nrequest_private_tour")
guide=make_guide(40, ["Judean Desert", "Negev"])
private=expect_ok("private tour with a free guide", lambda: traveler.request_private_tour(guide, days_from_today(50), 2))
print(f"            region={private.region} (guide's first specialty), difficulty={private.difficulty_level} "
      f"(traveler's level), price={private.price} (500 per day), status={private.status}")
expect_rejected("guide busy on those dates", lambda: make_traveler(41).request_private_tour(guide, days_from_today(51), 1))
expect_rejected("traveler busy on those dates", lambda: traveler.request_private_tour(make_guide(41), days_from_today(30), 1))
expect_rejected("a date in the past", lambda: make_traveler(42).request_private_tour(make_guide(42), days_from_today(-5), 1))
expect_rejected("an object that is not a guide", lambda: make_traveler(43).request_private_tour("Yossi", days_from_today(80), 1))

print("\ngenerate_payment_report (premium has 20% off; the fee is what a cancellation today would cost)")
pprint(traveler.generate_payment_report(), sort_dicts=False)


# ======================================================================
section("6. Guide: availability, removal and statistics")
# ======================================================================

guide=make_guide(50, ["Negev", "Arava"])
upcoming=make_trek(50, 30)
done=make_trek(51, 60, region="Arava", max_p=4, min_p=2)
upcoming.assign_guide(guide)
done.assign_guide(guide)
done.register(make_traveler(50))
done.register(make_traveler(51))
done.set_dates(days_from_today(-20), 2)
done.complete_trek()

print("\nis_available")
expect_equal("free on other dates", guide.is_available(days_from_today(100), 2), True)
expect_equal("busy on the trek dates", guide.is_available(days_from_today(30), 2), False)

print("\nanalyze_guiding_statistics (completed treks, upcoming treks, average occupancy, regions)")
pprint(guide.analyze_guiding_statistics(), sort_dicts=False)

print("\nremove_trek")
expect_ok("remove the upcoming trek", lambda: guide.remove_trek(50))
expect_equal("both sides are updated", (upcoming.guide, upcoming in guide.assigned_treks), (None, False))
expect_rejected("remove a trek that is not assigned", lambda: guide.remove_trek(50))


# ======================================================================
section("7. Agency: repositories, search and reports")
# ======================================================================

agency=Agency("Desert Steps")
guide=make_guide(60, ["Negev", "Galilee"])
other_guide=make_guide(61, ["Galilee"])

print("\nadd_guide / add_traveler / add_trek")
expect_ok("add a guide", lambda: agency.add_guide(guide))
expect_rejected("add a guide with the same id", lambda: agency.add_guide(make_guide(60)))
expect_rejected("add an object that is not a guide", lambda: agency.add_guide("guide"))
travelers=[make_traveler(60, "basic"), make_traveler(61, "annual"), make_traveler(62, "premium")]
for t in travelers:
    expect_ok(f"add traveler {t.traveler_id}", lambda: agency.add_traveler(t))
expect_rejected("add a traveler with the same id", lambda: agency.add_traveler(make_traveler(60)))

ramon=Trek(60, "Ramon Crater", "Negev", 4, 1, 10, days_from_today(30), 3, 1000)
nahal=Trek(61, "Nahal Amud", "Galilee", 2, 1, 10, days_from_today(31), 2, 600)
arbel=Trek(62, "Mount Arbel", "Galilee", 3, 1, 10, days_from_today(32), 1, 300)
ramon.assign_guide(guide)
nahal.assign_guide(other_guide)
expect_ok("add a trek with a guide from the agency", lambda: agency.add_trek(ramon))
expect_rejected("add a trek whose guide is not in the agency", lambda: agency.add_trek(nahal))
agency.add_guide(other_guide)
expect_ok("add it after the guide joins", lambda: agency.add_trek(nahal))
expect_ok("add a trek with no guide yet", lambda: agency.add_trek(arbel))
expect_rejected("add the same trek id twice", lambda: agency.add_trek(ramon))
ramon.register(travelers[0])
ramon.register(travelers[2])
nahal.register(travelers[1])

print("\nsearch_treks (name, region, guide name, difficulty)")
expect_equal("by name 'crater'", [t.trek_id for t in agency.search_treks("crater")], [60])
expect_equal("by region 'galilee'", [t.trek_id for t in agency.search_treks("galilee")], [61, 62])
expect_equal("by guide name 'Guide 61'", [t.trek_id for t in agency.search_treks("Guide 61")], [61])
expect_equal("by difficulty 3", [t.trek_id for t in agency.search_treks(3)], [62])
expect_equal("no match", agency.search_treks("Everest"), [])
expect_rejected("empty search term", lambda: agency.search_treks("  "))

print("\ngenerate_season_schedule_report (Nahal Amud and Mount Arbel share a day in the Galilee)")
pprint(agency.generate_season_schedule_report(), sort_dicts=False)

print("\ngenerate_membership_report")
pprint(agency.generate_membership_report(), sort_dicts=False)


# ======================================================================
section("8. Extension: Equipment")
# ======================================================================

tents=Equipment(1, "Tent", 10)
trek_a=make_trek(70, 30, duration=3)
trek_b=make_trek(71, 31, duration=3)
trek_c=make_trek(72, 60, duration=2)

print("\nloan_to_trek / get_available_quantity / get_quantity_on_loan")
expect_ok("lend 6 tents to trek A", lambda: tents.loan_to_trek(trek_a, 6))
expect_equal("free on the dates of trek B, which overlap A", tents.get_available_quantity(trek_b.start_date, 3), 4)
expect_equal("on loan on the first day of A", tents.get_quantity_on_loan(trek_a.start_date), 6)
expect_rejected("lend 5 to trek B, only 4 are free", lambda: tents.loan_to_trek(trek_b, 5))
expect_ok("lend 4 to trek B", lambda: tents.loan_to_trek(trek_b, 4))
expect_ok("lend all 10 to trek C, on other dates", lambda: tents.loan_to_trek(trek_c, 10))
expect_rejected("a second loan to the same trek", lambda: tents.loan_to_trek(trek_a, 1))
expect_rejected("quantity 0", lambda: tents.loan_to_trek(make_trek(73, 90), 0))
expect_rejected("an object that is not a trek", lambda: tents.loan_to_trek("trek", 1))

print("\nis_loaned_to / can_supply / set_dates with equipment")
expect_equal("loaned to trek A", tents.is_loaned_to(70), True)
expect_equal("trek C cannot move onto the dates of A", tents.can_supply(72, trek_a.start_date, 2), False)
expect_rejected("set_dates checks the equipment list", lambda: trek_c.set_dates(trek_a.start_date, 2, equipment=[tents]))
expect_equal("trek C kept its dates", trek_c.start_date, days_from_today(60))

print("\nfind_conflicts (a move without the equipment list skips the check)")
expect_equal("no conflicts yet", tents.find_conflicts(), [])
trek_c.set_dates(trek_a.start_date, 2)
expect_equal("A and C are now over the stock", tents.find_conflicts(), [70, 71, 72])
trek_c.set_dates(days_from_today(60), 2)

print("\ncancelled trek frees its tents / return_from_trek")
trek_b.cancel_trek()
expect_equal("B's tents count as free again", tents.get_available_quantity(trek_b.start_date, 3), 4)
expect_equal("return A's tents", tents.return_from_trek(70), 6)
expect_rejected("return again", lambda: tents.return_from_trek(70))


# ======================================================================
section("9. Extension: Transport")
# ======================================================================

bus=Transport(1, "Minibus", 8)
jeep=Transport(2, "Jeep", 4)
trek_a=make_trek(80, 30, max_p=10)
trek_b=make_trek(81, 31)

print("\nassign_to_trek / is_available / is_assigned_to")
expect_ok("assign the minibus to trek A", lambda: bus.assign_to_trek(trek_a, "Beer Sheva station"))
expect_equal("the minibus is assigned to A", bus.is_assigned_to(80), True)
expect_equal("the minibus is busy on A's dates", bus.is_available(trek_a.start_date, 1), False)
expect_rejected("assign it to trek B, which overlaps", lambda: bus.assign_to_trek(trek_b, "Tel Aviv"))
expect_rejected("empty pickup point", lambda: jeep.assign_to_trek(trek_a, " "))
cancelled=make_trek(82, 50)
cancelled.cancel_trek()
expect_rejected("assign to a cancelled trek", lambda: jeep.assign_to_trek(cancelled, "Eilat"))

print("\nhas_enough_seats (one seat is kept for the guide)")
expect_equal("8 seats for 10 travelers and a guide", Transport.has_enough_seats(trek_a, [bus]), False)
jeep.assign_to_trek(trek_a, "Beer Sheva station")
expect_equal("8 + 4 seats", Transport.has_enough_seats(trek_a, [bus, jeep]), True)
expect_rejected("the same vehicle twice", lambda: Transport.has_enough_seats(trek_a, [bus, bus]))
expect_rejected("a vehicle not assigned to the trek",
                lambda: Transport.has_enough_seats(trek_a, [bus, Transport(3, "Van", 6)]))

print("\nset_dates with vehicles / find_conflicts / remove_from_trek")
later=make_trek(84, 60)
bus.assign_to_trek(later, "Tel Aviv")
expect_rejected("set_dates checks the vehicle list", lambda: later.set_dates(trek_a.start_date, 2, vehicles=[bus]))
later.set_dates(trek_a.start_date, 2)
expect_equal("a move without the list shows up as a conflict", bus.find_conflicts(), [(80, 84)])
expect_ok("remove the minibus from the moved trek", lambda: bus.remove_from_trek(84))
expect_equal("no conflicts after the removal", bus.find_conflicts(), [])
expect_rejected("remove it again", lambda: bus.remove_from_trek(84))


# ======================================================================
section("Summary")
# ======================================================================
print(f"\n{results['passed']} checks behaved as expected, {results['failed']} did not")
