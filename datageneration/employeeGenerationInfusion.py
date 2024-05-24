
import os
import pandas as pd
import numpy as np
import random 
import sys
sys.path.append( os.path.join(os.path.split(__file__)[0],'..') )  # Include subfolders
from config import construction_config_infusion

def assign_shifts(employees):
    #get index lists for each skill
    skill_1=[i for i,e in enumerate(employees) if e[1]==1]
    skill_2=[i for i,e in enumerate(employees) if e[1]==2]
    skill_3=[i for i,e in enumerate(employees) if e[1]==3]

    #put all skill 1 to day-shift
    for index in skill_1:
        employees[index][2].append(2)
    
    #put the three first skill 2 to each shift
    #employees[skill_2.pop(0)][2].append(1)  #night
    employees[skill_2.pop(0)][2].append(2)  #day
    #employees[skill_2.pop(0)][2].append(3)  #evening

    #put the three first skill 3 to each shift
    employees[skill_3.pop(0)][2].append(1)  #night
    employees[skill_3.pop(0)][2].append(2)  #day
    employees[skill_3.pop(0)][2].append(3)  #evening

    
    skill_23 = skill_2 + skill_3            #index of remaining skill 2 and 3 not yet assigned shift
    random.shuffle(skill_23)                #randmize the order of skill 2 and 3

    n_night = 1                             #initial employees in night shift
    n_day = len(skill_1) + 2                #initial employees in day shift
    n_evening = 1                           #initial employees in evening shift

    #iterate remaining skill 2 and 3, fill first 70% at day, then 20% at evening, and remaining 10% at night
    for index in skill_23:
        if n_day<0.7*len(employees):                #put in day-shift if less than 70% assigned
            employees[index][2].append(2)
            n_day+=1
        elif n_day+n_evening<0.9*len(employees):    #put in evening-shift if less than 90% assigned
            employees[index][2].append(3)
            n_evening+=1
        else:
            employees[index][2].append(1)           #put in night-shift
            n_night+=1

    #add same shift for remaining week for each employee
    for e in employees:
        shifts=[e[2][0]+i*3 for i in range(1,construction_config_infusion.days)]    #same shift each working day
        e[2].extend(shifts)

    #verify results, set to "if False:"" to disable
    if True:        
        night=[e for e in employees if e[2][0]==1]
        day=[e for e in employees if e[2][0]==2]
        evening=[e for e in employees if e[2][0]==3]

        #print(n_night,n_day,n_evening)
        #print(len(night),len(day),len(evening))

#TESTING
#employees=[[i+1,random.randint(1,3),[]] for i in range(100)]  #generate employes with id, skill end empty shift list [[id,skill,[]],...]
#print(employees)

#assign_shifts(employees)
#print(employees)

def employeeGenerator():
    df_employees = pd.DataFrame(columns=['employeeId', 'professionalLevel', 'schedule'])

    profession_levels = np.random.choice(construction_config_infusion.professionLevels, 
                                         construction_config_infusion.E_num, 
                                         p=construction_config_infusion.professionLevelsProb)

    employees = []
    for index, level in enumerate(profession_levels): 
        employees.append([index+1, level, []])          # EmployeeId, Profession Level, Schedule

    shifts_assignment = assign_shifts(employees)       # TODO: Uncomment for shifts night, day and evening

    for e in employees: 
        schedule = []
        #schedule = [2, 5, 8, 11, 14]                    # TODO: Set schedule = [] for shifts night, day and evening
        df_employees = df_employees._append({
            'employeeId': e[0],
            'professionalLevel': e[1],
            'schedule': e[2] #schedule#
        },ignore_index=True)
    
    file_path = os.path.join(os.getcwd(), 'data', 'employees.csv')
    df_employees.to_csv(file_path, index=False)
    
    return df_employees

def employeeGeneratorOnlyDay():
    df_employees = pd.DataFrame(columns=['employeeId', 'professionalLevel', 'clinic', 'schedule'])

    if construction_config_infusion.E_num > 5:
        first_levels = np.array([1, 2, 2, 3, 3])
        remaining_levels = np.random.choice(construction_config_infusion.professionLevels, 
                                         construction_config_infusion.E_num-5, 
                                         p=construction_config_infusion.professionLevelsProb)
        profession_levels = np.concatenate([first_levels, remaining_levels])
    elif construction_config_infusion.E_num == 5:
        profession_levels = np.array([1, 2, 2, 3, 3])
    elif construction_config_infusion.E_num == 4:
        profession_levels = np.array([1, 2, 3, 3])
    elif construction_config_infusion.E_num == 3:
        profession_levels = np.array([2, 3, 3])
    elif construction_config_infusion.E_num == 2:
        profession_levels = np.array([2, 3])
    else:
        profession_levels = np.array([3])

    employees = []
    for index, level in enumerate(profession_levels): 
        employees.append([index+1, level, [2, 5, 8, 11, 14]])          # EmployeeId, Profession Level, Schedule

    # Beregne eksakt antall klinikker basert på fordeling
    clinic_counts = (np.array(construction_config_infusion.clinicDistribution) * construction_config_infusion.E_num).astype(int)
    clinics = np.hstack([np.full(count, i) for i, count in enumerate(clinic_counts, start=1)])

    # Justere for manglende eller ekstra klinikker på grunn av avrunding
    current_total_clinics = len(clinics)
    if current_total_clinics < construction_config_infusion.E_num:
        # Legg til manglende klinikker
        extra_clinics = np.random.choice(range(1, len(clinic_counts) + 1), 
                                         construction_config_infusion.E_num - current_total_clinics,
                                         p=construction_config_infusion.clinicDistribution)
        clinics = np.concatenate([clinics, extra_clinics])
    elif current_total_clinics > construction_config_infusion.E_num:
        # Fjern overflødige klinikker tilfeldig
        np.random.shuffle(clinics)
        clinics = clinics[:construction_config_infusion.E_num]

    np.random.shuffle(clinics)  # Blande klinikker for å tildele tilfeldig

    # Tildele klinikk 0 til ansatte med profesjon 1 og justere fordelingen
    for i, level in enumerate(profession_levels):
        if level == 1:
            # Finn en ikke-null klinikk og bytt den ut
            non_zero_index = np.where(clinics != 0)[0][0]
            clinics[i], clinics[non_zero_index] = 0, clinics[i]

    # Fyll DataFrame
    for e, c in zip(employees, clinics):
        df_employees = df_employees._append({
            'employeeId': e[0],
            'professionalLevel': e[1],
            'clinic': c,
            'schedule': e[2]
        }, ignore_index=True)    
    
    file_path = os.path.join(os.getcwd(), 'data', 'employees.csv')
    df_employees.to_csv(file_path, index=False)
    
    return df_employees

#employeeGeneratorOnlyDay()