#Generelt om distributions: Mange av disse vil være ca.-tall eller maxfactor for en fordeling.1

# PATIENTS
# Number of patients
P_num = 50 
maxActivitiesPerPatient = 25 

# Distributions
treatmentsPerPatient = 1.05                     #Number of treatments per patient
activitiesPerVisit = 2.5                        #Number of activities per treatment
maxActivitiesPerVisit = 6                       #Max number of activities per visit
A_numProb = [0.25, 0.05, 0.3, 0.05, 0.3, 0.05]    #Probability of the number of activities from 1 to 6 in a visit

# Pattern Type Distribution (5days) - Decides visits per treatment
frequency1 = 0.2                #Five days a week
frequency2 = 0.2                #Four days a week
frequency3 = 0.2                #Three days spread throughout the week
frequency4 = 0.1                #Two days spread throughout the week
frequency5 = 0.1                #Two concecutive days
frequency6 = 0.2                #One day a week
patternTypes = [frequency1, frequency2, frequency3, frequency4, frequency5, frequency6]

# Patterns
patterns_5days = [1]                                                # Patterntype 1
patterns_4days = [2,3,4,5,6]                                        # Patterntype 2
patterns_3days = [7]                                                # Patterntype 3
pattern_2daysspread = [8,9,10]                                      # Patterntype 4
patterns_2daysfollowing = [11,12,13,14]                             # Patterntype 5
patterns_1day = [15,16,17,18,19]                                    # Patterntype 6

# Continuity distribution
continuityDistribution = [0.25, 0.25, 0.5] #Top 1 employee, top 3 employees, all employees

# Employee history??

# Heaviness
heavinessDistribution = [0.05, 0.2, 0.5, 0.2, 0.05] 

# ACTIVITIES
# Activities Distribution 
#precedence = 0.5
#sync = 0.05
#sameEmployee = 0.1 #Prosent??
pd_min = 30                     #Min pickup and delivery time limit
pd_max = 120                    #Max pickup and delivery time limit

# Profession Requirement
professionReq1 = [0.4, 0.3, 0.3, 0] #index 0: logistics

# Duration in minutes 
minDurationHealth = 15
maxDurationHealth = 120 
minDurationEquip = 5
maxDurationEquip = 30
#TODO: Må finne ut av hvordan dette skal fordeles?? Random eller bruke en kjent fordeling?

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
E_num = 25
# Distributions of employees
E_num_night = 0.1
E_num_day = 0.7
E_num_evening = 0.2

# Profession Level 
professionLevels = [1, 2, 3, 4]
professionLevelsProb =  [0.2, 0.3, 0.5, 0] #index 0: level 1

# Employee Restrictions
employeeRestrict = 0.05

# Working period
days = 5

# DEPOT LOCATION
depot = (59.9365, 10.7396)





