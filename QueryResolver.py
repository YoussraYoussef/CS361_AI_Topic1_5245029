import re

from KnowledgeBase import KB
from SearchAgent import AI


# this class serves as the Query resolver that would parse the query of the user
# the expected query is in the form of print_solution(travel( "Source City","Destination City",["Start Day","End Day"]))
# where Source City, Destination City, Start Day and End Day are parsed .

# this part serves as the main entry point of the program (or the user interface).

# after resolving the query this part uses the loaded knowledge base with the travel agent to present the user
# with the optimal travel guide to take him from Source City to Destination city through flights strictly between
# the before mentioned Start Day End Day
class QR:
    PATH = "Travel Agent KB (2 sheets).xlsx"

    # through the constructor a knowledge base is loaded from a predefined constant file path
    # the file needs to be in the form of an excel file
    def __init__(self):
        self.knowledgeBase = KB(self.PATH)
        self.searcher = AI(self.knowledgeBase)

    # as mentioned in the description of this class the query passed is a string that is then parsed using
    # regular expressions, where the white spaces are removed to ensure smooth parsing
    def resolveQuery(self, query:str):
        query = re.sub("\s+", "", query)
        strWord = "\"([a-zA-Z]+)\""
        template = "\Aprint_solution\(travel\("+strWord+","+strWord+",\["+strWord+","+strWord+"\]\)\)\Z"
        found = re.findall(template, query)
        if len(found) == 0:
            print("Please enter a valid query!")
            return
        else:
            found = found[0]

        From, TO, StartDay, EndDay = found

        StartDay = self.knowledgeBase.weekShort[StartDay]
        EndDay = self.knowledgeBase.weekShort[EndDay]

        # the parsed parameters are then passed to the search agent object which then returns the node
        # associated with the path
        Path = self.searcher.getOptimalPath(From, TO, StartDay, EndDay)

        # in case of a None node being the result which would happen if no path was found within the given constraints
        # these constraints are then loosened to an extra day on both ends
        if Path is None:
            StartDay = self.knowledgeBase.prevDay[StartDay]
            EndDay = self.knowledgeBase.nextDay[EndDay]
            Path = self.searcher.getOptimalPath(From, TO, StartDay, EndDay)
        if Path is None:
            return

        # due to the implementation of the __str__ in the node object printing the node
        # is enough to print the whole path
        print(Path)

        # extra output where we present the total time of the trip in form of hh:mm
        hours = Path.travelTime // 60
        minutes = Path.travelTime % 60
        print("\nthe trip would take", hours, "hours and", minutes, "minutes.")


# in here we find the entry point to our program, and a sample input in the below comment
# print_solution(travel( "Cairo","San Francisco",["Tuesday","Wednesday"]))
queryResolver = QR()
queryResolver.resolveQuery(input())
