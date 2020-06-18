import pandas as pd
import re
import datetime
import math

# this class acts as a knowledge base for all of the program, it loads the data from the provided excel sheet
# and saves it into dictionaries with the appropriate key for each data point
class KB:

    # this dictionary maps to their latitude and longitude
    Locations = dict()

    # this dictionary maps each flight number to its info (ex. source, destination, ect.)
    Flights = dict()

    # this list keeps track of al the city names
    Cities = []

    # this dictionary maps a day's name to its shortened version as it exists in the flight data
    weekShort = {"Saturday": "sat", "Sunday": "sun", "Monday": "mon", "Tuesday": "tue", "Wednesday": "wed",
                 "Thursday": "thu", "Friday": "fri"}

    # these two dictionaries map each shorten week day to the following or the previous day
    nextDay = {"sat": "sun", "sun": "mon", "mon": "tue", "tue": "wed", "wed": "thu",
               "thu": "fri", "fri": "sat"}
    prevDay = {"sat": "fri", "sun": "sat", "mon": "sun", "tue": "mon", "wed": "tue",
               "thu": "wed", "fri": "thu"}

    # this method accepts a string and removes any white space from the string
    def removeSpace(self, strWord: str):
        return re.sub("\s+", "", strWord)

    # this method accepts a list of strings and applies the previous method to each of them
    def removeSpaceList(self, List):
        retList = []
        for i in range(len(List)):
            retList.append(self.removeSpace(List[i]))
        return retList

    # this method accepts a datetime type parameter of hours and minutes and formats it into a string
    def parseTime(self, Time: datetime):

        return {"hour": int(Time.hour), "minute": int(Time.minute)}

    # this method accepts a list of datetime items and applies the previous method to each of them
    def parseTimeList(self, List):
        retList = []
        for i in range(len(List)):
            retList.append(self.parseTime(List[i]))
        return retList

    # this method accepts a list in the form of a string and converts it to a list of strings
    def parseLists(self, ListofLists):
        retList = []
        for i in range(len(ListofLists)):
            strList = ListofLists[i][1:-1]
            List = strList.split(", ")
            retList.append(List)
        return retList

    # given a deprature day and a departure time and a arrival time this method figures out if the arrival day would
    # be on the same day or on the day after
    def arrivalDay(self, departureDay, departureTime, arrivalTime):
        if arrivalTime["hour"] < departureTime["hour"]:
            return self.nextDay[departureDay]
        elif arrivalTime["hour"] == departureTime["hour"] and arrivalTime["minute"] < departureTime["minute"]:
            return self.nextDay[departureDay]
        else:
            return departureDay

    #given two days this method figures out the number of days between them
    def differenceInDays(self, From, To):
        current = From
        diff = 0
        while current != To:
            current = self.nextDay[current]
            diff += 1
        return diff

    # given an departure time and day, and an arrival time and day this method figures out the time between
    # departure and arrival in minutes
    def differenceinMinutes(self, departureDay, arrivalDay, departureTime, arrivalTime):
        diff = self.differenceInDays(departureDay, arrivalDay) * 60 * 24
        diff += (arrivalTime["hour"] - departureTime["hour"]) * 60
        diff += (arrivalTime["minute"] - departureTime["minute"])
        return diff

    # this method accepts a range of days represented as the start and end of the range and it produces a list of
    # all the days in the range ( including the start and the end )
    def allowedDays(self, start, end):
        allowed = [start]
        while start != end:
            start = self.nextDay[start]
            allowed.append(start)
        return allowed

    # this method accepts two cities and uses the loaded locations for each city (longitude and latitude)
    # to calculate the distance between the two cities using euclidean distance
    def distance(self, From, To):
        Fx, Fy = self.Locations[From]
        Tx, Ty = self.Locations[To]
        return math.sqrt((Tx - Fx)**2 + (Ty - Fy)**2)

    # this constructor uses the above methods to load and record the data as presented in the excel sheet
    # it accepts a path to that excel sheet and it can be mainly split into two parts
    # 1- loading the locations of cities and their names
    # 2- loading the flights and using the flight number as the key
    # loading data from the excel file is done through the pandas library utilizing the library's DataFrame type
    def __init__(self, path):

        # loading city names
        citiesData = pd.read_excel(path, sheet_name="Cities")
        self.Cities = self.removeSpaceList(citiesData["City"])

        # loading location to cities
        for i in range(len(self.Cities)):
            x = citiesData["Longitude"][i]
            y = citiesData["Latitude"][i]
            self.Locations[self.Cities[i]] = (x, y)

        flightsData = pd.read_excel(path, sheet_name="Flights")

        From = self.removeSpaceList(flightsData["Source"])
        To = self.removeSpaceList(flightsData["Destination"])
        fromTime = self.parseTimeList(flightsData["Departure Time"])
        toTime = self.parseTimeList(flightsData["Arrival Time"])
        ID = flightsData["Flight Number"]
        availableDays = self.parseLists(flightsData["List of Days"])

        # loading flights
        for i in range(len(From)):
            self.Flights[ID[i]] = {"source": From[i], "destination": To[i], "departure": fromTime[i],
                                   "arrival": toTime[i], "available": availableDays[i]}


