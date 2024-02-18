import math
import matplotlib.pyplot as plt
from .Generaldistribution import Distribution # the folder with data

class Binomial(Distribution):

    # TODO: make a Binomial class that inherits from the Distribution class. Use the specifications below.
    """ Binomial distribution class for calculating and
    visualizing a Binomial distribution.
    Attributes:
        mean (float) representing the mean value of the distribution
        stdev (float) representing the standard deviation of the distribution
        data_list (list of floats) a list of floats to be extracted from the data file
        p (float) representing the probability of an event occurring
    """
    #       A binomial distribution is defined by two variables:
    #           the probability of getting a positive outcome (p), the number of trials (n)
    #       If you know these two values, you can calculate the 'mean' and the 'standard deviation'
    #       For example, if you flip a fair coin 25 times, p = 0.5 and n = 25
    #       You can then calculate the mean and standard deviation with the following formula:
    #           mean = p * n
    #           standard deviation = sqrt(n * p * (1 - p))

    # TODO: define the init function
    # TODO: store the probability of the distribution in an instance variable p
    # TODO: store the size of the distribution in an instance variable n
    # TODO: Now that you know p and n, you can 'calculate the mean' and 'standard deviation'
        # You can use the calculate_mean() and calculate_stdev() methods defined below
        # 'along with the __init__ function' from the Distribution class

    def __init__(self, prob=0.5, trials=20): # data set is '1' or '0'
        self.p = prob
        self.n = trials

        # need to count 'mean' and 'stdev' cannot refer to self.mean, self.stdev -> as is parrent element
        # You can use the calculate_mean() and calculate_stdev() methods defined below
        # 'along with the __init__ function' from the Distribution class
        Distribution.__init__(self, self.calculate_mean(), self.calculate_stdev())

    # TODO: write a method calculate_mean() according to the specifications below

    def calculate_mean(self):
        """Function to 'calculate the mean' from p and n
        Args:
            None
        Returns:
            float: 'mean of the data set' -> self.mean
        """
        # probability * number of tries
        self.mean = self.p * self.n

        return self.mean

    # TODO: write a calculate_stdev() method according to the specifications below.
    def calculate_stdev(self):
        """Function to 'calculate the standard deviation' from p and n.
        Args:
            None
        Returns:
            float: standard deviation of the data set
        """
        # sqrt(n * p * (1 - p))
        sigma = math.sqrt(self.n * self.p * (1 - self.p))
        self.stdev = sigma

        return self.stdev

    # TODO: write a replace_stats_with_data() method according to the specifications below.
    # The read_data_file() from the 'Generaldistribution class 'can read in a data file.
    # Because the Binomialdistribution class 'inherits' from the Generaldistribution class, you don't need to re-write
    # this method. However, the method 'doesn't update' the mean or standard deviation of a distribution.
    # Hence you are going to write a method that 'calculates n, p, mean and standard deviation'
    # from a data set and then 'updates' all the n, p, mean and stdev 'attributes'.
    # Assume that the 'data' is a list of zeros and ones like [0 1 0 1 1 0 1].
    #       Write code that:
    #           updates the 'n' attribute of the binomial distribution
    #           updates the 'p' value of the binomial distribution by calculating the
    #               number of 'positive trials divided by the total trials'
    #           updates the 'mean' attribute
    #           updates the 'standard deviation' attribute
    #
    #       Hint: You can use the calculate_mean() and calculate_stdev() methods defined previously.

    def replace_stats_with_data(self):
        """Function to calculate 'p' and 'n' from the 'data set'. The function updates the 'p and n' variables of the object.
        Args:
            None
        Returns:
            float: the p value
            float: the n value
        """
        # CANNOT COUNT self.data myself, I do not know the inputs from the user!!!
        # self.data = self.read_data_file("numbers_binomial.txt")

        self.n = len(self.data) # do not assign into another variable

        # each probability - 1 happend, 0 - fail
        # P(X=k)=(k n) * p^k * (1−p)^n−k
        # Let's say you're flipping a fair coin (where the probability of getting heads, p, is 0.5)
        # 5 times (so n = 5). Find the probability of getting exactly 3 heads (k=3).
        # P(X=3)=(5 3) * 0.5^3 * (0.5)^5-3 # 0.3125

        counts = sum(1 for step in self.data if step == 1)

        # 1. what is the probability of the data set - is counted in 'pdf' density of prob of binomial distribution
        # self.p = math.factorial(self.n)/math.factorial(counts) * (self.p**counts * (1 - self.p)**(self.n - counts))

        self.p = 1.0 * sum(self.data) / len(self.data)  # ratio of happenings per 1 trial

        # 2. count mean and standard deviation
        self.mean = self.calculate_mean()
        self.stdev = self.calculate_stdev()

        return self.p, self.n

    # TODO: write a method plot_bar() that outputs a 'bar chart of the data' set according to the following specifications.
    def plot_bar(self):
        """Function to 'output a histogram' of the instance variable 'data' using
        matplotlib pyplot library.
        Args:
            None
        Returns:
            None
        """
        #  A 'bar graph' is used to compare discrete or categorical variables in a graphical format
        # plt.bar(name[0:10], price[0:10])
        # whereas a 'histogram' depicts the frequency distribution of variables in a dataset (continues data)
        plt.hist(self.data)
        plt.title("Bar Chart of the probability of appearance")
        plt.xlabel("Outcome")
        plt.ylabel("Counts")

    #TODO: Calculate the 'probability density function' of the binomial distribution
    def pdf(self, occurance):
        """Probability 'density function' calculator for the binomial distribution.
        Args:
            k (float): point for calculating the probability density function
        Returns:
            float: probability density function output
        """
        # Write a method to 'plot the probability density function' of the binomial distribution
        factorial_trials = math.factorial(self.n) / (math.factorial(occurance) * (math.factorial(self.n - occurance)))
        prob_of_happening = (self.p**occurance) * (1 - self.p)**(self.n - occurance)
        prob = factorial_trials * prob_of_happening

        return prob

    # TODO: Use a 'bar chart to plot the probability density' function from
        # k = 0 to k = n

        #   Hint: You'll need to use the pdf() method defined above to calculate the
        #   density function 'for every value of k'.

        #   Be sure to label the 'bar chart' with a 'title', 'x' label and 'y' label
        #   This method should also return the 'x and y values' used to make the chart
        #   The x and y values should be stored in separate lists
    def plot_bar_pdf(self):

        """Function to plot the pdf of the binomial distribution
        Args:
            None
        Returns:
            list: x values for the pdf plot
            list: y values for the pdf plot
        """
        x = []
        y = []

        # populate x, y arrays
        # for each trial create the 'occurance'
        for i in range(self.n + 1): # incl. last one
            x.append(i)
            y.append(self.pdf(i)) # probability of each number

        # create bar chart
        plt.bar(x, y)
        plt.xlabel("Probability")
        plt.ylabel("Value")
        plt.title("Bar Chart")

        plt.show()

        return x, y

    def __add__(self, other):
    # write a method to output the 'sum of two binomial distributions'. Assume both distributions have the same p value.
        """Function to add together two Binomial distributions with equal p
        Args:
            other (Binomial): Binomial instance

        Returns:
            Binomial: Binomial distribution
        """

        try:
            assert self.p == other.p, 'p values are not equal'
        except AssertionError as error:
            raise

        # TODO: Define addition for two binomial distributions. Assume that the
        # p values of the two distributions are the 'same'. The formula for
        # 'summing two binomial distributions' with different p values is more complicated,
        # so you are only expected to implement the case for two distributions with equal p.

        # the 'try, except statement' above will raise an exception if the p values are not equal
        # Hint: When adding two binomial distributions, the p value remains the same
        #   The 'new n value' is the 'sum of the n values' of the two distributions.

        result = Binomial()           # instance of Binomial distribution to add with other instance of Bin. dist.
        result.n = result.n + other.n
        result.p = other.p
        result.calculate_mean()
        result.calculate_stdev()

        return result


    # use the __repr__ magic method to output the characteristics of the binomial distribution object.
    def __repr__magic():
        """Function to output the characteristics of the Binomial instance
        Args:
            None
        Returns:
            string: characteristics of the Binomial object
        """
        # TODO: Define the representation method so that the output looks like
        #       mean 5, standard deviation 4.5, p .8, n 20
        #       with the values replaced by whatever the actual distributions values are
        #       The method should return a string in the expected format

        return "mean {}, standard deviation {}, p {}, n {}".format(self.mean, self.stdev, self.p, self.n)
