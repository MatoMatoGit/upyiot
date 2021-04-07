class AvgFilter:

    def __init__(self, depth, dec_round=True):
        self.Depth = depth
        self.Round = dec_round
        self.Values = []

    def Input(self, value):
        """
        Adds an input value to the averaging filter.
        :param value: Value to add.
        :type value: number
        """
        print("Input: {}".format(value))
        # Add the new value to the filter values.
        self.Values.append(value)
        # If the filter has reached its maximum Depth,
        # pop the last item from the filter values.
        if len(self.Values) > self.Depth:
            s = 0
            self.Values.pop(s)
        print("Filter ({}): {}".format(len(self.Values), self.Values))

    def Output(self):
        """
        Calculates the average of the current filter values.
        :return: Average value.
        :rtype: number
        """
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

    def Reset(self):
        """
        Resets the filter values.
        """
        n = len(self.Values)
        for i in range(0, n):
            self.Values.pop(i)

