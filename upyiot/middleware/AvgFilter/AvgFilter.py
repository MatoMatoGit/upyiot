class AvgFilter:

    ##
    # Constructor
    # @param[in] Depth Filter Depth
    #
    def __init__(self, depth, dec_round=True):
        self.Depth = depth
        self.Round = dec_round
        self.Values = []

    ##
    # Adds an input sample to the averaging filter.
    # @param[in] sample Input sample
    #
    def Input(self, sample):
        print("Input: {}".format(sample))
        # Add the new sample to the filter values.
        self.Values.append(sample)
        # If the filter has reached its maximum Depth,
        # pop the last item from the filter values.
        if len(self.Values) > self.Depth:
            s = 0
            self.Values.pop(s)
        print("Filter ({}): {}".format(len(self.Values), self.Values))

    ##
    # Calculates the average of the current filter
    # values.
    # @retval average
    #
    def Output(self):
        filter_sum = 0
        # Calculate the sum of all filter values.
        for s in self.Values:
            filter_sum += s
        print("Sum: {}".format(filter_sum))
        # The average is the sum divided by the current amount of
        # samples.
        avg = filter_sum / len(self.Values)
        print("Average: {}".format(avg))

        if self.Round is True:
            # Round the average to the nearest integer.
            avg = round(avg)

        print("Output: {}".format(avg))
        return avg

    ##
    # Resets the filter values.
    #
    def Reset(self):
        print("Reset")
        n = len(self.Values)
        for i in range(0, n):
            print("Deleting item", i)
            self.Values.pop(i)

