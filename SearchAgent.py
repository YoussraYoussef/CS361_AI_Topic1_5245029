from KnowledgeBase import KB

# this class helps keep track of each path when we run the getOptimalPath in the AI class
# this is done because the A* algorithm can be considered as a BFS search algorithm
# so it'd be hard to identify what are the ancestors of a node
class Node:

    # the parameters of the constructor describe the kind of data that the Node would hold.

    # a node represents a stop in the trip at a city, and to represent the stop we need
    # ID: which is the id of the flight that got us to the city represented by the node
    # flight: which holds the data of the flight that has the above mentioned ID
    # departureDay: which is the day we took the flight on since a flight can be available on multiple days
    # arrivalDay: defining the day of arrival for the flight which can be the same as the departureDay or the one after
    # travelTime: which describes the time(in minutes) the trip took so far (up until we reached the city of this node)
    # distanceLeft: describes the distance left until we reach a destination, which is an approximation that is
    #               the calculated displacement between the two cities since we don't know the optimal path yet
    # prevNode: which is a reference to the parent node representing the city we were on before we reached the current
    def __init__(self, ID, flight, departureDay, arrivalDay, travelTime, distanceLeft, prevNode):
        self.ID = ID
        self.flight = flight
        self.departureDay = departureDay
        self.arrivalDay = arrivalDay
        self.travelTime = travelTime
        self.distanceLeft = distanceLeft
        self.prevNode = prevNode

    # this method returns the sum of our travelTime and distanceLeft, we can use this sum as ou heuristic to our node
    def getScore(self):
        return self.travelTime + self.distanceLeft

    # this methods formats the time of a flight described by a dictionary
    # and returns the time as a string in form hh:mm
    def formatTime(self, time):
        h = str(time["hour"])
        m = str(time["minute"])
        if h == "0":
            h = "00"
        if m == "0":
            m = "00"
        return h + ":" + m

    # this method coverts the node to a string when passed to the str format,
    # it append the string of a parent if it isn't None recursively so converting
    # the last node in a path would result in a string of the whole path
    def __str__(self):
        ret = ""
        if self.prevNode is not None:
            ret = str(self.prevNode) + "\n"
        ret += "Use flight " + self.ID + " from " + self.flight["source"] + " to " + self.flight["destination"] + "."
        ret += " Departure time " + self.formatTime(self.flight["departure"]) + " on " + self.departureDay
        ret += " and Arrival time " + self.formatTime(self.flight["arrival"]) + " on " + self.arrivalDay + "."
        return ret

# this class serves as the engine to the program with the core method named getOptimalPath which is called through
# the query resolver, implementing the A* algorithm to find the pest travel path which would have the minimal time
class AI:

    # the constructor's sole responsibility is to set the knowledge base that we'll later use
    def __init__(self, knowledgeBase:KB):
        self.knowledgeBase = knowledgeBase

    # this method is the core of the program, where we calculate the actual optimal path to the trip
    def getOptimalPath(self, source, destination, startDay, endDay):

        # we first set an empty list as our priority queue
        priorityQueue = []

        # we then retrieve the set of allowed days we can be traveling on using the limits passed through
        # the parameters as startDay and endDay
        allowedDays = self.knowledgeBase.allowedDays(startDay, endDay)

        # we then add our initial nodes to the priority queue, each node represents a city we can travel to from
        # our starting source.

        # we do this by searching through each flight
        for id, info in self.knowledgeBase.Flights.items():
            # if the source of that flight matches our starting location
            if info["source"] == source:
                for day in info["available"]:
                    # and if the flight has a day that matches our defined limitations
                    if day in allowedDays:
                        # we calculate the day of arrival to that flight
                        arrivalDay = self.knowledgeBase.arrivalDay(day, info["departure"], info["arrival"])
                        # then we also check that the arrival day is within the constraints
                        if arrivalDay in allowedDays:
                            # then we finally add the node to the priorityQueue, but first we calculate the additional
                            # information that we'll need to pass to the node like the travelTime and distanceLeft
                            travelTime = self.knowledgeBase.differenceinMinutes(day, arrivalDay, info["departure"]
                                                                                , info["arrival"])
                            distanceLeft = self.knowledgeBase.distance(info["destination"], destination)
                            # we then set the node with no parent to be able to recognize later that it's initial
                            node = Node(id, info, day, arrivalDay, travelTime, distanceLeft, None)
                            # then we add it to the priorityQueue
                            priorityQueue.append(node)

        # we then sort the nodes in the priorityQueue using the returned value of getScore for each node
        # which would mean that the node with the lowest score would be at index 0 always.
        priorityQueue.sort(key=Node.getScore)

        # we then set an empty visited list to make sure that no node is considered twice,
        # the visited list would hold a tuple in the form of (flightID, departureDay)
        # and not flightID only since the passenger would blocked from trying to take
        # the same flight but on a different day
        visited = []

        # we then iterate over the priorityQueue until it is emtpy or until we reach a stopping condition
        while priorityQueue:

            # we access the lowest score node at index 0 and save it for later as our current node
            # Note: we expand on the lowest scoring node since this is a minimization
            #       problem where we try to minimize travel time
            oldNode = priorityQueue[0]

            # then we remove the node from the priorityQueue to make sure it isn't accessed again
            priorityQueue.remove(oldNode)

            # if the tuple in the form mentioned above is found within the visited list we skip the node
            if (oldNode.ID, oldNode.departureDay) in visited:
                continue

            # if we reach this point we know for sure that this node is going to be processed and expanded
            # so we add its tuple to the visited list
            visited.append((oldNode.ID, oldNode.departureDay))

            # if we find that the current node has the same flight destination as our ultimate destination
            # we've reached our goal and we return the current node which would then represent our path
            if oldNode.flight["destination"] == destination:
                return oldNode

            # if we haven't reached our destination we expand the current node by doing the same thing when did
            # with our initial nodes but with a few extra steps

            # we still search through each flight
            for id, info in self.knowledgeBase.Flights.items():

                # but this time around we check the flight we're checking has the same source as our previous
                # destination we find in the current node's flight
                if info["source"] == oldNode.flight["destination"]:
                    for day in info["available"]:

                        # we also check if the flight has a departure day that matches our defined limitations
                        if day in allowedDays:
                            arrivalDay = self.knowledgeBase.arrivalDay(day, info["departure"], info["arrival"])

                            # and if the arrival day is also within the constraints
                            if arrivalDay in allowedDays:

                                # we then calculate the data that the nwe node will hold
                                currentTime = oldNode.flight["arrival"]

                                # first thing we need to calculate is the wait time between landing from the flight
                                # we took to get to the current node's city and the departure time of the flight
                                # that we're currently considering
                                waitTime = self.knowledgeBase.differenceinMinutes(oldNode.arrivalDay, day,
                                                                                  currentTime, info["departure"])

                                # if we missed the flight or if the flight would take a wait time more than the allowed
                                # days (meaning it's on a previous day) then we skip that flight and consider another
                                if waitTime < 0 or waitTime > (len(allowedDays) * 24 * 60):
                                    continue

                                # we then calculate the time we'll spend on that flight if we took it
                                travelTime = self.knowledgeBase.differenceinMinutes(day, arrivalDay,
                                                                                    info["departure"], info["arrival"])
                                # and the distance from the destination of that flight to our ultimate destination
                                distanceLeft = self.knowledgeBase.distance(info["destination"], destination)

                                # the we then calculate the total trip of the new node using the values we calculated
                                timeSoFar = oldNode.travelTime + waitTime + travelTime

                                # then we create the new node and add it to the priorityQueue
                                node = Node(id, info, day,  arrivalDay, timeSoFar, distanceLeft, oldNode)
                                priorityQueue.append(node)

            # we make sure to sort the priority Queue to keep it updated and to have the lowest scoring
            # at index 0 for further processing
            priorityQueue.sort(key=Node.getScore)

        # if we reach this point we didn't find an optimal path within the given time window and we return a None
        return None




