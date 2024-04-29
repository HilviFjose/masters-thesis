# ANTIBIOTICS INFUSION CASE
# -------------------------
# PATIENTS
P_num = 15                                          # Number of patients

# Patient demographics
clinicDistribution = [0.3, 0.2, 0.2, 0.3]
specialisationDistribution = [0.7, 0.7, 0.7, 0.7]
patientExtraSupport = [0.8, 0.7, 0.2, 0.4] #Percentage from each clinic that needs extra support 

# Pattern Type Distribution (5days) - Decides visits per treatment
frequency1 = 0.3                # Five days a week
frequency2 = 0.0                # Four days a week
frequency3 = 0.0                # Three days spread throughout the week
frequency4 = 0.7                # Two days spread throughout the week
frequency5 = 0.0                # Two concecutive days
frequency6 = 0.0                # One day a week
patternTypes = [frequency1, frequency2, frequency3, frequency4, frequency5, frequency6]

# Patterns
patterns_5days = [1]                                                # Patterntype 1
patterns_4days = [2,3,4,5,6]                                        # Patterntype 2
patterns_3days = [7]                                                # Patterntype 3
pattern_2daysspread = [8,9,10]                                      # Patterntype 4
patterns_2daysfollowing = [11,12,13,14]                             # Patterntype 5
patterns_1day = [15,16,17,18,19]                                    # Patterntype 6

# Continuity distribution
continuityDistribution = [0, 0.5, 0.5]      #Top 1 employee, top 3 employees, all employees
continuityScore = [2, 1, 0]                 #TODO: Sjekk om verdiene på disse på endres
preferredEmployees = [1, 3, 0]

# Patient allocation
allocation = 0.15 #Percentage already allocated to AHH (Overwritten if P_num > 5* E_num')

# Patient utility
utilityDistribution = [1, 0, 0]

# Heaviness
heavinessDistribution = [0.5, 0.5, 0] 

# ACTIVITIES
pd_min = 60                     #Min pickup and delivery time limit
pd_max = 150                    #Max pickup and delivery time limit

# Profession Requirement
# If logistics workers can't deliver medicine..
professionReq1 = [0, 0.3, 0.7, 0] #index 0: logistics

# Duration in minutes 
minDurationHealth = 15
maxDurationHealth = 120 
minDurationEquip = 5
maxDurationEquip = 30
#TODO: Må finne ut av hvordan dette skal fordeles?? Random eller bruke en kjent fordeling?

# EMPLOYEES
# Number of employees
E_num = 3
E_generalists = 0.2 #Percentage of employees with profession level 1 and 2 that are generalists

# Distributions of employees
E_num_night = 0.1
E_num_day = 0.7
E_num_evening = 0.2

# Profession Level 
professionLevels = [1, 2, 3, 4]
professionLevelsProb =  [0.2, 0.3, 0.5, 0] #index 0: level 1

# Employee Restrictions and History
employeeRestrict = 0.05
employeeHistory = 0.90

# Working period
days = 5

# LOCATION
area = 2                        # Allowing for locations X km area around the depot and reference locations
depot = (59.9365, 10.7396)      # Lat and lon for Oslo University Hospital
Ullern = (59.9400, 10.6665)
Ris = (59.9564, 10.6973)
Holmenkollen = (59.9653, 10.6566)
Sogn = (59.9548, 10.7429)
Bjerke = (59.9386, 10.8148)
Haugerud = (59.9218, 10.8353)
Boler = (59.8926, 10.8215)
Lambergseter = (59.8655, 10.8131)
Grunerlokka = (59.9233, 10.7871)
StHanshaugen = (59.9329, 10.7506)
Majorstuen = (59.9282, 10.7126)
refLoc = [depot, Ullern, Ris, Holmenkollen, Sogn, Bjerke, Haugerud, Boler, Lambergseter, Grunerlokka, StHanshaugen, Majorstuen]

# DAY
startday = 480
endday = 960

max_num_of_activities_in_visit = 5

#Weights for complexity for activity
a_w_oportunity_space = 0.5
a_w_precedens_act = 0.5


#Weights for complexity for visit 
v_w_oportunity_space = 0.5
v_w_num_act= 0.5





