#Generelt om distributions: Mange av disse vil være ca.-tall eller maxfactor for en fordeling.1

# PATIENTS
# Number of patients
P_num = 50 
maxActivitiesPerPatient = 25 

# Distributions
treatmentsPerPatient = 1.05 #Number of treatments per patient
#visitsPerTreatment = 3.5 #Number of visits per treatment
activitiesPerVisit = 3.5 #Number of activities per treatment

# Pattern Type Distribution (5days)
frequency1 = 0.2 #Five days a week
frequency2 = 0.2 #Four days a week
frequency3 = 0.2 #Three days spread throughout the week
frequency4 = 0.2 #Two concecutive days
frequency5 = 0.2 #One day a week

# Patterns
patterns_5days = [1]                                                # Patterntype 1
patterns_4days = [2,3,4,5,6]                                        # Patterntype 2
patterns_3days = [7]                                                # Patterntype 3
pattern_2daysspread = [8,9,10]                                      # Patterntype 4
patterns_2daysfollowing = [11,12,13,14]                             # Patterntype 5
patterns_1day = [15,16,17,18,19]                                    # Patterntype 6
#Patterns_distribution = [Patterns_5days = 0.1, Patterns_4days = 0.1]

# Continuity 
continuityFactor1 = 0.25 #Top 1 employee
continuityFactor2 = 0.25 #Top 3 employees
continuityFactor3 = 0.5 #All employees
continuityThreshold1 = 0.4 #Top 1 employee
continuityThreshold2 = 0.2 #Top 3 employees

# Employee history??

# Heaviness
heavinessFactor = [0.05, 0.2, 0.5, 0.2, 0.05] 

# ACTIVITIES
"""
Columns: 
id
patientId
earliestStartTime
latestStartTime
activityDuration
synchronisation
skillRequirement
precedence
sameEmployeeActivityId
visit
treatment
possiblePatterns
patternType
numOfVisits
utility
location
continuityGroup
heaviness
"""
# Activities Distribution 
precedence = 0.5
sync = 0.05
sameEmployee = 0.1 #Prosent??

# Starting time in minutes (1 day)
latestStartTime = 1400

# Profession Requirement
professionReq1 = [0.4, 0.3, 0.3, 0] #index 0: logistics

# Duration in minutes 
minDurationHealth = 45
maxDurationHealth = 120 
minDurationEquip = 5
maxDurationEquip = 40
#Må finne ut av hvordan dette skal fordeles?? Random eller bruke en kjent fordeling?

# Starting time for health activities
minWindowHealth = minDurationHealth
minWindowEquip = minDurationEquip
averageWindowHealth = 200 #average time window between earliest and latest starting time

#Distribution of activities over one day
activitiesNight = 0.2
activitiesDay = 0.6
activitiesEvening = 0.2
#TODO: må håndtere at aktivititeter kan fordeles over flere skift dersom vi ønsker det i datasettet.


# EMPLOYEES
# Number of employees
E_num = 20
# Distributions of employees
E_num_night = 0.1
E_num_day = 0.7
E_num_evening = 0.2

# Profession Level 
professionLevels = [1, 2, 3, 4]
professionLevelsProb =  [0.2, 0.3, 0.5, 0] #index 0: level 1

# Shifts
startNight = 0
endNight = 480
startDay = 480
endDay = 960
startEvening = 960
endEvening = 1440
shifts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

#Employee Restrictions
employeeRestrict = 0.05





