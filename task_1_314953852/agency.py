from datetime import date
from trek import Trek
from traveler import Traveler
from guide import Guide


class Agency:
    # Creates an agency with empty repositories; the class only reports an invalid value, the calling code decides how to handle it
    def __init__(self, name):
        if type(name) is not str or not name.strip():
            raise ValueError(f"Invalid name: {name}")

        # Name of the agency
        self.name=name
        # Traveler repository, changed only through add_traveler
        self.travelers=[]
        # Guide repository, changed only through add_guide
        self.guides=[]
        # Trek repository, changed only through add_trek
        self.treks=[]

    # Adds a traveler to the repository, after checking the type and that the id is new
    def add_traveler(self, traveler):
        if not isinstance(traveler, Traveler):
            raise ValueError(f"Invalid traveler: {traveler}")
        for existing in self.travelers:
            if existing.traveler_id==traveler.traveler_id:
                raise ValueError(f"Traveler id {traveler.traveler_id} already exists")
        self.travelers.append(traveler)

    # Adds a guide to the repository, after checking the type and that the id is new
    def add_guide(self, guide):
        if not isinstance(guide, Guide):
            raise ValueError(f"Invalid guide: {guide}")
        for existing in self.guides:
            if existing.guide_id==guide.guide_id:
                raise ValueError(f"Guide id {guide.guide_id} already exists")
        self.guides.append(guide)

    # Adds a trek to the repository, after checking the type, that the id is new and that its guide is known to the agency
    def add_trek(self, trek):
        if not isinstance(trek, Trek):
            raise ValueError(f"Invalid trek: {trek}")
        for existing in self.treks:
            if existing.trek_id==trek.trek_id:
                raise ValueError(f"Trek id {trek.trek_id} already exists")
        if trek.guide is not None and trek.guide not in self.guides:
            raise ValueError(f"Guide {trek.guide.guide_id} of trek {trek.trek_id} is not in the agency")
        self.treks.append(trek)

    # Returns the season of a date by its month (assumption); a winter runs across two years, so December joins the January after it
    def get_season(self, start_date):
        if type(start_date) is not date:
            raise ValueError(f"Invalid date: {start_date}")
        month=start_date.month
        year=start_date.year
        if month==12:
            return f"winter {year}-{year+1}"
        if month<=2:
            return f"winter {year-1}-{year}"
        if month<=5:
            return f"spring {year}"
        if month<=8:
            return f"summer {year}"
        return f"autumn {year}"

    # Returns the reasons two treks that share a day deserve a warning; the region is the case the system allows, the others are blocked earlier and are kept as a safeguard
    def get_overlap_reasons(self, first, second):
        reasons=[]
        if first.region==second.region:
            reasons.append(f"same region: {first.region}")
        if first.guide is not None and first.guide is second.guide:
            reasons.append(f"same guide: {first.guide.name}")
        for traveler in first.participants:
            if traveler in second.participants:
                reasons.append(f"same traveler: {traveler.name}")
        return reasons

    # Returns the treks grouped by departure season and date, with overlap warnings between active treks; a cancelled trek is left out and a completed one gets no warning
    def generate_season_schedule_report(self):
        treks=[]
        for trek in self.treks:
            if trek.status!="cancelled":
                treks.append(trek)
        treks.sort(key=lambda trek: trek.start_date)

        seasons={}
        for trek in treks:
            guide_name=None
            if trek.guide is not None:
                guide_name=trek.guide.name
            row={"trek_id": trek.trek_id, "name": trek.name, "region": trek.region, "start_date": trek.start_date,
                 "end_date": trek.get_end_date(), "guide": guide_name, "status": trek.status,
                 "participants": len(trek.participants)}
            seasons.setdefault(self.get_season(trek.start_date), []).append(row)

        warnings=[]
        for i in range(len(treks)):
            for second in treks[i+1:]:
                first=treks[i]
                if first.is_active() and second.is_active() and first.overlaps(second.start_date, second.duration_days):
                    reasons=self.get_overlap_reasons(first, second)
                    if reasons:
                        warnings.append({"trek_ids": (first.trek_id, second.trek_id), "reasons": reasons})
        return {"agency": self.name, "seasons": seasons, "warnings": warnings}

    # Returns the matching treks: text searches name, region and guide name, a whole number searches the difficulty level
    def search_treks(self, search_term):
        if type(search_term) is int:
            return [trek for trek in self.treks if trek.difficulty_level==search_term]
        if type(search_term) is not str or not search_term.strip():
            raise ValueError(f"Invalid search term: {search_term}")

        term=search_term.strip().lower()
        results=[]
        for trek in self.treks:
            # A trek with no guide is searched only by its name and region
            texts=[trek.name, trek.region]
            if trek.guide is not None:
                texts.append(trek.guide.name)
            for text in texts:
                if term in text.lower():
                    results.append(trek)
                    break
        return results

    # Returns the travelers, active travelers and expected income of each membership type; the income is what current treks will pay at the final price
    def generate_membership_report(self):
        memberships={}
        for membership_type in Traveler.VALID_MEMBERSHIPS:
            memberships[membership_type]={"travelers": 0, "active_travelers": 0, "expected_income": 0}

        for traveler in self.travelers:
            row=memberships[traveler.membership_type]
            row["travelers"]+=1
            if len(traveler.current_treks)>0:
                row["active_travelers"]+=1
            for trek in traveler.current_treks:
                row["expected_income"]+=traveler.get_final_price(trek)

        total_income=0
        active_travelers=0
        for row in memberships.values():
            row["expected_income"]=round(row["expected_income"], 2)
            total_income+=row["expected_income"]
            active_travelers+=row["active_travelers"]
        return {"agency": self.name, "memberships": memberships, "total_travelers": len(self.travelers),
                "active_travelers": active_travelers, "expected_income": round(total_income, 2)}
