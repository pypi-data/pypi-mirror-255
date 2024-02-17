class skillbot:
    def __init__(self, name, skill):
        self.name = name
        self.skill = skill
        self.powered_on = False

    def power_on(self):
        self.powered_on = True
        print(f"{self.name} is now powered on and ready to {self.skill}!")
      
    def power_off(self):
      self.powered_on = False
      print(f"{self.name} has been powered off.")
      
    def perform_skill(self):
        if self.powered_on:
            print(f"{self.name} is showcasing its {self.skill} skill!")
        else:
            print(f"{self.name} is not powered on. Please turn it on first.")
