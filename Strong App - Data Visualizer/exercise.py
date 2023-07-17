class Exercise():
    def __init__(self, name, date_time):
        self.name = name
        self.date_time = date_time
        self.sets = []
        self.best = []

    def __str__(self):
        return f"Name:{self.name},   Timestamp:{self.date_time},   Sets:{self.sets},   Best:{self.best}"
    
    # Appends set (set number, weight, reps) and determines best set
    def add_set(self, set, weight, reps):
        # Zero out empty weight
        if not weight.strip():
            weight = '0'
        self.sets.insert(len(self.sets), [set, weight, reps])
        for s in self.sets:
            # Set default best
            if len(self.best) == 0:
                self.best = s
            
            # More reps
            elif float(s[2]) > float(self.best[2]):
                self.best = s
            
            # More weight
            elif float(s[1]) > float(self.best[1]):
                self.best = s
            