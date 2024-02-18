import math
import matplotlib.pyplot as plt
from .Generaldistribution import Distribution

class Binomial(Distribution):
    """ Binomial distribution class for calculating and 
    visualizing a Binomial distribution.
    
    Attributes:
        mean (float) representing the mean value of the distribution
        stdev (float) representing the standard deviation of the distribution
        data_list (list of floats) a list of floats to be extracted from the data file
        p (float) representing the probability of an event occurring
                
    """

    def __init__(self, prob=0.5, size=20):
        self.p = prob
        self.n = size
        Distribution.__init__(self, prob, size)

        """Function to calculate the mean from p and n
        
        Args: 
            None
        
        Returns: 
            float: mean of the data set
    
        """
        
    def calculate_mean(self):
        self.mean = 1.0 * self.p * self.n
        return self.mean

        """Function to calculate the standard deviation from p and n.
        
        Args: 
            None
        
        Returns: 
            float: standard deviation of the data set
    
        """
        
    def calculate_stdev(self):
        self.stdev = 1.0 * math.sqrt(self.p * self.n * (1.0 - self.p))
        return self.stdev

        """Function to calculate p and n from the data set. The function updates the p and n variables of the object.
        
        Args: 
            None
        
        Returns: 
            float: the p value
            float: the n value
    
        """
        
    def replace_stats_with_data(self):

        self.n = 1.0 * len(self.data)
        self.p = 1.0 * sum(self.data) / len(self.data)
        self.mean = self.calculate_mean()
        self.stdev = self.calculate_stdev()
        
        return self.p, self.n
        
        """Function to output a histogram of the instance variable data using 
        matplotlib pyplot library.
        
        Args:
            None
            
        Returns:
            None
        """
        
    def plot_bar(self):
        plt.bar(x = ['0', '1'], height = [(1 - self.p) * self.n, self.p * self.n])
        plt.title('Bar Chart')
        plt.xlabel('X - Possible Outcomes')
        plt.ylabel('Y - Count')
            
        """Probability density function calculator for the binomial distribution
        
        Args:
            k (float): point for calculating the probability density function
            
        
        Returns:
            float: probability density function output
        """
    
    def calculate_pdf_binomial(self, k):
        a = math.factorial(self.n) / (math.factorial(k) * (math.factorial(self.n - k)))
        b = (self.p ** k) * (1 - self.p) ** (self.n - k)
        return a * b

        """Function to plot the pdf of the binomial distribution
        
        Args:
            None
        
        Returns:
            list: x values for the pdf plot
            list: y values for the pdf plot
            
        """

    def plot_bar_chart_pdf_binomial(self):
        
        x = []
        y = []
        
        for i in range(self.n + 1):
            x.append(i)
            y.append(self.calculate_pdf_binomial(i))
            
        plt.bar(x, y)
        plt.title('Bar Chart of the Distribution of Outcomes')
        plt.xlabel('Probability')
        plt.ylabel('Outcome')
        plt.show()
        
        return x, y
        
        """Function to add together two Binomial distributions with equal p
        
        Args:
            other (Binomial): Binomial instance
            
        Returns:
            Binomial: Binomial distribution
            
        """
    def __add__(self, other):
        
        try:
            assert self.p == other.p, 'p values are not equal'
        except AssertionError as error:
            raise
        
        result = Binomial()
        result.n = self.n + other.n
        result.p = self.p
        result.calculate_mean()
        result.calculate_stdev()
        
        return result
    
        """Function to output the characteristics of the Binomial instance
        
        Args:
            None
        
        Returns:
            string: characteristics of the Binomial object
        
        """

    def __repr__(self):
        return "mean {}, standard deviation {}, p {}, n {}".format(self.mean, self.stdev, self.p, self.n)
        
    
