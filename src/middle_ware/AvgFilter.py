class AvgFilter:

    ##
    # Constructor
    # @param[in] depth Filter depth
    #
    def __init__(self, depth):
        self.depth = depth
        self.filter_values = []

    ##
    # Adds an input sample to the averaging filter.
    # @param[in] sample Input sample
    #
    def Input(self, sample):
        print("Input: {}".format(sample))
        # Add the new sample to the filter values.
        self.filter_values.append(sample)
        # If the filter has reached its maximum depth,
        # pop the last item from the filter values.
        if len(self.filter_values) > self.depth:
            s = 0
            self.filter_values.pop(s)
        print("Filter ({}): {}".format(len(self.filter_values), self.filter_values))

    ##
    # Calculates the average of the current filter
    # values.
    # @retval average
    #
    def Output(self):
        filter_sum = 0
        # Calculate the sum of all filter values.
        for s in self.filter_values:
            filter_sum += s
        print("Sum: {}".format(filter_sum))
        # The average is the sum divided by the current amount of
        # samples.
        avg = filter_sum / len(self.filter_values)
        print("Average: {}".format(avg))
        # Round the average to the nearest integer.
        avg = round(avg)
        print("Output: {}".format(avg))
        return avg

    ##
    # Resets the filter values.
    #
    def Reset(self):
        print("Reset")
        n = len(self.filter_values)
        for i in range(0, n):
            print("Deleting item", i)
            self.filter_values.pop(i)

