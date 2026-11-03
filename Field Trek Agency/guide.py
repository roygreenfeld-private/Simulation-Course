import math
from trek import Trek


class Guide:
    # Creates a valid guide with no treks; the class only reports an invalid value, the calling code decides how to handle it
    def __init__(self, guide_id, name, specialties, certification_level, experience_years, max_monthly_treks):
        if type(guide_id) is not int or guide_id<=0:
            raise ValueError(f"Invalid guide id: {guide_id}")
        if type(name) is not str or not name.strip():
            raise ValueError(f"Invalid name: {name}")
        if type(specialties) is not list or len(specialties)==0:
            raise ValueError(f"Invalid specialties: {specialties}")
        for region in specialties:
            if region not in Trek.VALID_REGIONS:
                raise ValueError(f"Invalid region: {region}")
        # Assumption: certification uses a 1 to 10 scale, the assignment does not define one
        if type(certification_level) is not int or not 1<=certification_level<=10:
            raise ValueError(f"Invalid certification level: {certification_level}")
        # A whole number is also accepted, as with a trek's price, and is kept as a float below
        if type(experience_years) not in (int, float) or not math.isfinite(experience_years) or experience_years<0:
            raise ValueError(f"Invalid experience years: {experience_years}")
        if type(max_monthly_treks) is not int or max_monthly_treks<1:
            raise ValueError(f"Invalid monthly trek limit: {max_monthly_treks}")

        # Unique identifier of the guide
        self.guide_id=guide_id
        # Full name of the guide
        self.name=name
        # Regions the guide specializes in; a copy, so the calling code's list cannot change it later
        self.specialties=list(specialties)
        # Certification on a scale of 1 to 10, shown in the statistics report only
        self.certification_level=certification_level
        # Treks assigned to the guide, changed only through Trek.assign_guide and remove_trek
        self.assigned_treks=[]
        # Years of experience, can be partial such as 2.5
        self.experience_years=float(experience_years)
        # Most treks the guide can lead in one month, counted by departure month
        self.max_monthly_treks=max_monthly_treks

    # Asks to be assigned to a trek; Trek makes all the checks, so there is one place that assigns
    def assign_trek(self, trek):
        if not isinstance(trek, Trek):
            raise ValueError(f"Invalid trek: {trek}")
        trek.assign_guide(self)

    # Removes a trek from the guide on both sides; a completed trek stays, so the statistics remain correct (assumption)
    def remove_trek(self, trek_id):
        for trek in self.assigned_treks:
            if trek.trek_id==trek_id:
                if trek.status=="completed":
                    raise ValueError(f"Cannot remove completed trek {trek_id}")
                self.assigned_treks.remove(trek)
                trek.guide=None
                return
        raise ValueError(f"Trek {trek_id} is not assigned to guide {self.guide_id}")

    # Returns True if the date range overlaps no assigned trek; ignore_trek_id lets a trek skip itself when it moves
    def is_available(self, start_date, duration_days, ignore_trek_id=None):
        Trek.check_dates(start_date, duration_days)
        for trek in self.assigned_treks:
            if trek.trek_id!=ignore_trek_id and trek.overlaps(start_date, duration_days):
                return False
        return True

    # Returns a statistics report calculated on every call; a cancelled trek has already left assigned_treks, so it is never counted
    def analyze_guiding_statistics(self):
        completed=0
        occupancy_sum=0
        regions={}
        for trek in self.assigned_treks:
            regions[trek.region]=regions.get(trek.region, 0)+1
            if trek.status=="completed":
                completed+=1
                occupancy_sum+=len(trek.participants)/trek.max_participants
        # A guide with no completed treks gets 0 instead of a division by zero
        average_occupancy=0
        if completed>0:
            average_occupancy=round(occupancy_sum/completed, 2)
        return {"guide_id": self.guide_id, "name": self.name, "certification_level": self.certification_level,
                "experience_years": self.experience_years, "completed_treks": completed,
                "upcoming_treks": len(self.assigned_treks)-completed,
                "average_occupancy": average_occupancy, "regions": regions}
