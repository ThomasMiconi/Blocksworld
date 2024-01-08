import re
import pdb
import sys
import random







def check_plan(plan):   # plan should be a list of strings

    # This version works, but see the restrictions below

    # For now, we assume that the initial state and goal descriptions are valid.
    # Also, goals only involve two blocks
    
    # We stop checking and reaturn 'success' as soon as we detect that the state
    # implements the goal. We do NOT require the generator to output 'OK' or
    # otherwise acknowledge that the goal has been reached. This means that the
    # generator doesn't need a success detector to be successful. Anything after
    # goal has been reached is ignored.
    
    # Ideally we would like incorrect state descriptions to be caught right at the
    # point of incorrectness.  This version made some progress towards that goal.
    # Now, duplicate blocks in state descriptions are caught as soon as they are
    # mentioned, and so are blocks that are not part of current_state.


    lines = [line.rstrip() for line in plan]

    stage = 'state'
    success = False
    error_type = ''
    current_state = []
    current_goal = []

    for numline, l in enumerate(lines):
        
        #print(">"+l+"<")

        # We ignore the first line, which should simply say 'state:' - again, we assume
        # the initial state description is valid.
        if numline == 0:
            assert l == 'state:'
            continue

        if stage == 'state':
            if lines[numline-1] == 'state:': 
                # Initialize read_state if 1st line of state description. Hacky, but works
                read_state = []
            if re.match('^(b[0-9] on )+table$', l):
                blocks = l.split(' on ')
                assert blocks[-1] == 'table'
                read_state.append(blocks[:-1])
                if len(sum(read_state, [])) != len(set(sum(read_state, []))):  
                    # If there are any doublets
                    error_type = 'Duplicate block in state description'; break
                if current_state != []:  # Again, we assume that the initial state description is correct
                    if not set(sum(read_state, [])).issubset( set(sum(current_state, [])) ):
                        error_type = 'Some blocks in state description are not in current_state'; break
            elif l == 'goal:':
                # State description is over. Was it any good?
                if read_state == []:
                    error_type = 'No state description or invalid state description'; break
                if current_state == []:  
                    # We don't check the initial state description. We should check
                    # whether blocks are not used multiple times. 
                    current_state = read_state
                elif sorted(["".join(x) for x in read_state]) != sorted(["".join(x) for x in current_state]):
                    error_type = 'Described state is not identical to current state'; break  
                stage = 'goal'
                continue
            else:
                error_type = 'Syntax error in state description'; break 

        if stage == 'goal':
            if lines[numline-1] == 'goal:':  # Hacky, but works
                read_goal = []
            if re.match('^b[0-9] on b[0-9]$', l):
                if read_goal != []:
                    error_type = 'Multiple goal descriptions'; break
                read_goal = l.split(' on ')
                if current_goal == []:
                    # Again, we don't check initial goal description. We should
                    # check if it involves two different blocks, all present in the
                    # state description
                    current_goal = read_goal
                # Check if the goal has actually been reached
                assert success == False
                for pile in current_state:
                    if "".join(current_goal) in "".join(pile):
                        #print("Success detected!")
                        success = True
                if success:
                    break
            elif l == 'action:':  
                # Goal description is over, let's check it
                # Note that this is only executed if we have a next action prompt -i.e. not if this is the last goal statement in the plan with no further action.
                if read_goal == []:
                    error_type = 'No state description or invalid state description'; break
                if current_goal != read_goal:
                    error_type = 'Described goal is not identical to current goal'; break

                stage = 'action'
                continue
            else:
                error_type = 'Syntax error in goal description'; break

        if stage == 'action':
            if lines[numline-1] == 'action:':
                read_action = []
            if  re.match('put b[0-9] on b[0-9]$', l) or re.match('put b[0-9] on table$', l):
                if read_action != []:
                    error_type = 'Multiple action descriptions'; break
                read_action = l[4:].split(' on ')
            elif l == 'state:':
                if read_action[0] == read_action[1]:
                    error_type = 'Action involves same block twice'; break
                b1_reachable = b2_reachable = False
                if read_action[1] == 'table':
                    b2_reachable = True   # Table is always reachable
                for pile in current_state:
                    if read_action[0] == pile[0]:
                        b1_reachable = True
                    if read_action[1] == pile[0]:
                        b2_reachable = True
                if not (b1_reachable and b2_reachable):
                    errortype = 'Action involves blocks not reachable or not in state'; break
                for numpile, pile in enumerate(current_state):
                    if read_action[0] == pile[0]:
                        if len(pile) == 1:
                            current_state.pop(numpile) 
                        else:
                            current_state[numpile] = current_state[numpile][1:]
                    if read_action[1] == pile[0]:
                        current_state[numpile] = [read_action[0]] + current_state[numpile]
                if read_action[1] == 'table':
                    current_state.append([read_action[0]])
                stage = 'state'
                continue

    # We are out of the loop. Several conditions are possible.
    
    # success == True: the goal has been succesfully reached with no error along
    # the way
    
    # success == False, error_type == '': The goal has not been reached, but no
    # error has occurred
    
    # success == False, error_type != '', numline == len(lines)-1: The goal has not
    # been reached, error has occurred on the very last line, possibly indicating
    # an incomplete line rather than an actual error by the generator
    
    # success == False, error_type != '', numline < len(lines)-1: The goal has not
    # been reached, error has occurred before the very last line, indicating an
    # actual error by the generator
    
    # For now we do not distinguish between the last two cases, treating incomplete
    # lines as actual errors. This should discourage too-long generations, but this
    # in turn may be a o problem if we want to allow and encourage "cogitation".

    #if success:
    #    print("Success!")
    #elif error_type == '':
    #    print("Goal not reached, but no error detected")
    #else:
    #    print("Error: "+error_type)
    #print("Total number of lines in plan:", len(lines))
    #print("Last processed line (l."+str(numline)+"): >"+lines[numline]+"<")

    return {'success':success, 'error_type': error_type, 
            'last_line':lines[numline], 'last_line_num': numline,
            'plan': lines}





def problemgen(nb_blocks=6):

    blocks = ['b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9']
    random.shuffle(blocks)
    blocks = blocks[:nb_blocks]

    nb_piles = random.randint(1, nb_blocks)  # Nb. of different piles. 1 to nb_blocks inclusive
    piles = []
    for nb in range(nb_piles):
        piles.append([blocks[nb]]) # Each pile has at least one element

    for nb2 in range(nb+1, nb_blocks):
        piles[random.randint(0, nb_piles-1)].append(blocks[nb2])

# Pick two positions with distance at least 2 (so they're not on top of each other already)
    while True:
        posblock1 = random.randint(0, nb_blocks-1)
        posblock2 = random.randint(0, nb_blocks-1)
        if posblock1 > posblock2+1 or posblock2 > posblock1+1:
            break

    flattenedlist = sum(piles, [])
    problem = [flattenedlist[posblock1], flattenedlist[posblock2]] 


    random.shuffle(piles)
    return {'state':piles, 'goal':problem}
    #print("state:",[" on ".join(p)+" on table" for p in piles],"| goal:"," on ".join(problem))



if __name__ == "__main__":

    with open('plan5.txt') as f:
        plan = [l.rstrip() for l in f]

    o = check_plan(plan)
    print(o)

    problem = problemgen(nb_blocks=6)
    print("state:")
    state = [" on ".join(x)+" on table" for x in problem['state']]
    for l in state:
        print(l)
    print('goal:')
    print(" on ".join(problem['goal']))


