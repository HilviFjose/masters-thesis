# INFUSION CASE
# -------------------------
# PATIENTS
P_num = 100                                          # Number of patients

# Patient demographics
clinicDistribution = [0.25, 0.57, 0.03, 0.15]       # Cancer, Medical, Orthopaedic, Paediatric
patientExtraSupport = [0.5, 0.9, 0.2, 0.1]          # Percentage from each clinic that needs extra support 
clinicsWithNutrition = [1,1,0,1]
clinicsWithAdvanced = [1,1,0,1]
clinicsWithCombination = [1,1,0,1]

# Cancer clinic
therapiesCancer = [5/35*0.9, 5/35*0.9, 25/35*0.9, 0.1] #15 % of the patients have a combination of therapies
continuityCancer = [[0, 0.5, 0.5], [0, 0.5, 0.5], [0.4, 0.5, 0.1]] #Antibiotics, Nutrtion&Fluids and Advanced. Level 1,2,3
utilityCancer = [[1, 0, 0], [0, 0.5, 0.5], [0.1, 0.2, 0.7]]
workloadCancer = [[0.5, 0.5, 0], [0.4, 0.3, 0.3], [0.1, 0.4, 0.5]]

# Medical Clinic
therapiesMedical = [10/30*0.9, 10/30*0.9, 10/30*0.9, 0.1]
continuityMedical = [[0, 0.5, 0.5], [0, 0.5, 0.5], [0.1, 0.3, 0.6]] #Antibiotics, Nutrtion&Fluids and Advanced. Level 1,2,3
utilityMedical = [[1, 0, 0], [0.4, 0.5, 0.1], [0.4, 0.5, 0.1]]
workloadMedical = [[0.5, 0.5, 0], [0.2, 0.3, 0.5], [0, 0.5, 0.5]]

# Orthopaedic Clinic
therapiesOrtho = [1, 0, 0, 0]
continuityOrtho = [[0, 0.5, 0.5], [], []] #Antibiotics, Nutrtion&Fluids and Advanced. Level 1,2,3
utilityOrtho = [[1, 0, 0], [], []]
workloadOrtho = [[0.5, 0.5, 0], [], []]

# Paediatric Clinic
therapiesPaedia = [10/35*0.9, 5/35*0.9, 20/35*0.9, 0.1]
continuityPaedia = [[0, 0.5, 0.5], [0.2, 0.4, 0.4], [0.7, 0.2, 0.1]] #Antibiotics, Nutrtion&Fluids and Advanced. Level 1,2,3
utilityPaedia = [[1, 0, 0], [0.1, 0.2, 0.7], [0, 0.1, 0.9]]
workloadPaedia = [[0.5, 0.5, 0], [0, 0.5, 0.5], [0, 0.3, 0.7]]

# Patterns
patterns_5days = [1]                                                # Patterntype 1
patterns_4days = [2,3,4,5,6]                                        # Patterntype 2
patterns_3days = [7]                                                # Patterntype 3
pattern_2daysspread = [8,9,10]                                      # Patterntype 4
patterns_2daysfollowing = [11,12,13,14]                             # Patterntype 5
patterns_1day = [15,16,17,18,19]                                    # Patterntype 6

# Continuity distribution
#continuityDistribution = [0, 0.5, 0.5]              # Top 1 employee, top 3 employees, all employees
continuityScore = [2, 1, 0]                 
preferredEmployees = [1, 3, 0]

# Patient allocation
allocation = 0.15 # Percentage already allocated to AHH (Overwritten if P_num > 5* E_num')

# Patient utility
#utilityDistribution = [0.5, 0.5, 0]

# Heaviness
#heavinessDistribution = [0.5, 0.5, 0] 

# EMPLOYEES
# Number of employees
E_num = 15
E_generalists = 0.2 #Percentage of employees with profession level 1 and 2 that are generalists
if E_num == 2: 
    preferredEmployees = [1, 2, 0]
# Profession Level 
professionLevels = [1, 2, 3, 4]
professionLevelsProb =  [0.1, 0.4311, 0.4689, 0] #index 0: level 1

# Clinic distribution
E_clinicDistribution = [0.25, 0.6, 0, 0.15]       # Cancer, Medical, Orthopaedic, Paediatric


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
Majorstuen = (59.9282, 10.7126)
refLoc = [depot, Ullern, Ris, Holmenkollen, Sogn, Bjerke, Haugerud, Boler, Lambergseter, Grunerlokka, Majorstuen]

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



