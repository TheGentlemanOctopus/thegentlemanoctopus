class Pattern:
    # Register a parameter
    def register_param(self, name, minimum, maximum, default):      
        #TODO: Check if param exists in __dict__
        self.params[name] = PatternParam(minimum, maximum, default, len(self.params))

    #TODO: Use __getattribute__ instead?
    def __getattr__(self, name):
        #Initalise params
        #TODO: Is there a better way? 
        #I don't like the idea of every Pattern subclass having to call a base constructor
        if not "params" in self.__dict__:
            self.__dict__["params"] = {}
            return self.__dict__["params"]

        if name in self.params:
            return self.params[name].get()

        raise AttributeError("Could not find attribute", name)

    def __setattr__(self, name, value):
        if name in self.params:
            self.params[name].set(value)
        else:
            self.__dict__[name] = value

    #Runs when the pattern
    def on_pattern_select(self, octopus):
        pass

    def status(self):
        return self.__class__.__name__


class PatternParam:
    def __init__(self, minimum, maximum, default, index):
        if minimum > maximum:
            temp = maximum
            maximum = minimum
            minimum = temp

        self.min = float(minimum)
        self.max = float(maximum)
        self.default = float(default)
        self.set(default)

        self.index = index

    def get(self):
        return self.value

    def set(self, value):
        if value < self.min:
            self.value = self.min
        elif value > self.max:
            self.value = self.max
        else:
            self.value = value

    # Current value with respect to range
    def current_percentage(self):
        return (self.value - self.min)/(self.max - self.min)

    def set_percentage(self, percentage):
        self.set(self.min + percentage/(self.max - self.min))


#Example of how to get and set parameters
if __name__ == '__main__':
    pattern = Pattern()
    pattern.register_param("level", 1, 10, 5)
    print "Added Param 'level':", pattern.params["level"].__dict__
    print "Value:", pattern.level