import copy
from math import lcm

#What increment percentage you want to test clock decrease by
CLOCK_INCREMENT_DECREASE = .01

#Time each task takes to complete
t1c = 1
t2c = 1
t3c = 1
t4c = 3
#Deadline Time where deadline = sample period
t1d = 6
t2d = 10
t3d = 12
t4d = 20
#Compute LCM time to check for how long you have to check something is scheduleable
LCM = lcm(t1d, t2d, t3d, t4d)
print(f"Checking to LCM time {LCM}")
T1, T2, T3, T4 = [], [], [], []
#Time when its possible a task will start
task_start_times = []



#example point = [start time, deadline time, time to complete task]
for i in range(round(LCM/t1d)):
    T1.append([i*t1d, (i+1)*t1d, t1c])
    task_start_times.append(i*t1d)

for i in range(round(LCM/t2d)):
    T2.append([i*t2d, (i+1)*t2d, t2c])
    task_start_times.append(i*t2d)

for i in range(round(LCM/t3d)):
    T3.append([i*t3d, (i+1)*t3d, t3c])
    task_start_times.append(i*t3d)

for i in range(round(LCM/t4d)):
    T4.append([i*t4d, (i+1)*t4d, t4c])
    task_start_times.append(i*t4d)


print(T1)
print(T2)
print(T3)
print(T4)
#remove time duplicates, and then sort in ascending order
task_start_times = [*set(task_start_times)]
task_start_times.sort()
print(f"Task Time Starts: {task_start_times}")
print('\n')


Tasks = [T1, T2, T3, T4]
#Start every time at least reducing by this percent
max_clock_reduction = .00

def find_clock_reduction(task_order):
    global max_clock_reduction
    clock_violation = False
    #always start at the max to see if its posible to beat the highest value
    clock_reduction = 0
    time = 0
    original_task_order = copy.deepcopy(task_order)
    while not(clock_violation):
        ##reduce clock by one percent every iteriation
        clock_reduction += CLOCK_INCREMENT_DECREASE
        task_time_multiplier = 1/(1-clock_reduction)
        #scale the time it takes to complete a task based on completeion time
        for task in range(len(task_order)):
            task_order[task][2] *= task_time_multiplier
        #iterate throught the task on priority to complete them
        for task in range(len(task_order)):
            ##if the next priority task has more time to complete do that task
            if (task_order[task][2] > 0):
                ##Time until task can start
                task_start_time = task_order[task][0]    
                #if highest priority task can start
                if (task_start_time <= time): 
                    #complete the priority task
                    time += task_order[task][2]
                    task_order[task][2] = 0
                    # if deadline not met, then exit showing this clock reduction is not possible
                    if (time > task_order[task][1]):
                        clock_violation =True
                #Else if the highest priority task cannot start yet, complete other tasks in priority ques until its start time
                else: 
                    while (time < task_order[task][0]):
                        #check next potential start time for a task 
                        for start_time in task_start_times:
                            if start_time > time:
                                next_time = start_time
                                break
                        for backup_task in range(len(task_order)):
                            #if the backup task isnt complete and can start
                            if ((task_order[backup_task][2] > 0) and task_order[backup_task][0] <= time):
                                #check if can complete whole task before next one starts
                                if (next_time - time >= task_order[backup_task][2]):
                                    time_to_add = task_order[backup_task][2]
                                    task_order[backup_task][2] = 0
                                    if (time + time_to_add > task_order[backup_task][1]):
                                        clock_violation = True
                                    time += time_to_add
                                #else complete partial of scondary task until next one is available
                                else:
                                    task_order[backup_task][2] -= next_time - time
                                    
                                    if (next_time > task_order[backup_task][1]):
                                        # print(f"missed deadline after partial completion at {next_time} for deadline {task_order[backup_task][1]}")
                                        clock_violation = True
                                    time = next_time
                                    #recheck through priorities of tasks available
                                    break
                        time = next_time       
                    #Once  highest priority task start available, implement
                    time += task_order[task][2]
                    task_order[task][2] = 0
                    if (time > task_order[task][1]):
                        clock_violation =True
            if (time >= LCM):
                clock_violation = True
        #reset all the times left to completetion for tasks
        task_order = copy.deepcopy(original_task_order)
        time = 0
    #the clock reduction will fail at an increment of +.01 extra                
    clock_reduction -= CLOCK_INCREMENT_DECREASE
    if (max_clock_reduction < clock_reduction):
        max_clock_reduction = clock_reduction
        for task in range(len(task_order)):
            task_order[task][2] *= task_time_multiplier
        print(f"Task Schedule Point Order: {task_order}")
        print('\n')
        print(f"Max Clock Reduction = {max_clock_reduction}")  
        return True
    #Tied Priority orders
    elif(max_clock_reduction == clock_reduction):     
        return "Equivalent"
    else:
        return False

#Iterate through all priorities tested
for count1, p1 in enumerate(Tasks, 1):
    for count2, p2 in enumerate(Tasks, 1):
        if (p2 != p1):
            for count3, p3 in enumerate(Tasks, 1):
                if (p3!=p2 and p3!=p1):
                    for count4, p4 in enumerate(Tasks, 1):
                        if(p4!= p3 and p4 != p2 and p4 != p1):
                            task_priority_order = []
                            for task in p1:
                                task_priority_order.append(copy.deepcopy(task))   
                            for task in p2:
                                task_priority_order.append(copy.deepcopy(task))
                            for task in p3:
                                task_priority_order.append(copy.deepcopy(task))
                            for task in p4:
                                task_priority_order.append(copy.deepcopy(task))
                            
                            
                            reduced = find_clock_reduction(task_priority_order)
                            if (reduced == "Equivalent"):
                                print(F"Equivalent Priority order: T{count1}, T{count2}, T{count3}, T{count4}")
                            elif(reduced):
                                print(F"Priority order: T{count1}, T{count2}, T{count3}, T{count4}")
#Test a priority order
# example = []
# for task in T3:
#     example.append(copy.deepcopy(task))
# for task in T2:
#     example.append(copy.deepcopy(task))
# for task in T1:
#     example.append(copy.deepcopy(task))
# for task in T4:
#     example.append(copy.deepcopy(task))

# find_clock_reduction(example)


print("finished")

