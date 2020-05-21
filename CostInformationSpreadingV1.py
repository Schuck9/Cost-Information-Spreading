"""
A simple implementation of Cost information Spreadning 
@date: 2020.5.21
@author: Tingyu Mo
"""
import numpy as np 
import os 
import time

def reputationDynamics(costSpreadReputation, actionRulePopulation, socialNormPopulationWide, spreadDonorReputationOrNot):
    ### Update reputation through rounds of donation games

    ### reset image matrix (everyone is randomly good or bad)
    imageArray = np.random.choice([0,1], Ntotal)
    imageMatrixTemp = np.ones((Ntotal, Ntotal),dtype = np.int)
    for indexInd in range(0,Ntotal):
        imageMatrixTemp[:,indexInd] = np.ones(Ntotal) * imageArray[indexInd]
    
    numCooperativeAction = 0;
    payoffAll = np.zeros(Ntotal);
    #####
    for iRound in range(0,(Ntotal * roundGamePerIndividual)):
        #### roundGamePerIndividual per individual
        donorNow = np.random.choice(indexAllIndividuals)
        ##### select the Recipient
        listRecipients = indexAllIndividuals.copy()
        indexDonorNow = np.where(listRecipients == donorNow)
        np.delete(listRecipients, indexDonorNow)
        recipientNow =  np.random.choice(listRecipients)
        ##### select the Observer
        listObservers = listRecipients.copy()
        indexRecipientNow = np.where(listObservers == recipientNow)
        np.delete(listObservers, indexRecipientNow)
        observerNow =  np.random.choice(listObservers)

        ##### Start the GAME
        actionRuleDonor = actionRulePopulation[donorNow]
        #### Action rule : (G, B) = (1, 0) means C with Good, D with Bad
        actionIntended = actionRuleDonor[1 - imageMatrixTemp[donorNow,recipientNow]]
        if actionIntended == 1 and np.random.rand() > probFailedCooperation:
            ### Cooperate
            actionActual = 1
        else:
            #### Defect: fail to cooperate and intend to defect
            actionActual = 0
        numCooperativeAction = numCooperativeAction + actionActual
        ### calculate payoffs
        payoffAll[donorNow] = payoffAll[donorNow] - cost * actionActual
        payoffAll[recipientNow] = payoffAll[recipientNow] + benefit * actionActual



        # println("Donor = $donorNow, Recipient = $recipientNow, Observer = $observerNow");
        # reputationRecipientFromDonor = imageMatrixTemp[donorNow, recipientNow]
        # println("Reputation of recipient from Donor = $reputationRecipientFromDonor")
        # println("Reputation of recipient from Observer = $reputationRecipientFromObserver")
        # println("Action rule of Donor --- (G, B)")
        # display(actionRuleDonor)
        # println("Action intended of Donor = $actionIntended")
        # println("Actual action of Donor = $actionActual")
        # sleep(15)

        # println("Donor = $donorNow, Recipient = $recipientNow, Observer = $observerNow");
        # println("Updated Reputation of donor from Observer = $updatedReputationInTheEyesOfObserver")
        # println("Group that Observer belongs to = $groupObserverBelongs")


        if spreadDonorReputationOrNot[observerNow] == 1:
            reputationRecipientFromObserver = imageMatrixTemp[observerNow, recipientNow]
            ### Update the donor's reputation from Observer's eye
            imageMatrixTemp[observerNow, donorNow] = socialNormPopulationWide[2^orderNorm - (actionActual * 2 + reputationRecipientFromObserver)-1];
			### error in reputation assignment
            # if rand() < probReverseReputation
            #     imageMatrixTemp[observerNow, donorNow] = 1 - imageMatrixTemp[observerNow, donorNow];
            # 
            updatedReputationInTheEyesOfObserver = imageMatrixTemp[observerNow, donorNow]
            ### Observer spread the updated reputation of the Donor
            imageMatrixTemp[:, donorNow] = updatedReputationInTheEyesOfObserver * np.ones(Ntotal)
            ### Observer pays a cost --- costSpreadReputation
            payoffAll[observerNow] = payoffAll[observerNow] - costSpreadReputation
            ### Everyone thinks that the Observer is Good.
            imageMatrixTemp[:, observerNow] = np.ones(Ntotal)
            # println("Observer spreads Donor's reputation")
        

        # println("Updated image matrix")
        # display(imageMatrixTemp)
        # sleep(15)

        # xyz
    
    ### record cooperation rate
    cooperationRate = (numCooperativeAction * 1.0) / (Ntotal * roundGamePerIndividual)

    ### use Accumulated Payoffs

    return cooperationRate, payoffAll


def actionRuleDynamics(selectionIntensity, costSpreadReputation, fileName):
    ### initially indiviudals adopt random strategies from AllC, Disc, AllD
    indexActionRule = np.random.choice([0,1,3],size = Ntotal)
    actionRulePopulation = actionRulePossible[indexActionRule]
    ##
    spreadDonorReputationOrNot  = np.random.choice([0,1],size = Ntotal)
    ### Social norm currently in use
    socialNormPopulationWide = socialNormPossible[indexSocialNormNow]
    ###
    # println("Ntotal = $Ntotal");
    # println("actionRulePopulation");
    # println(actionRulePopulation);D
    # println("socialNormPopulationWide");
    # println(socialNormPopulationWide);
    #
    sumCoopRatio = 0
	
    for iGeneration in range(1,numGeneration):
        ### Reputation dynamics
        cooperationRate, payoffAll = reputationDynamics(costSpreadReputation, actionRulePopulation, socialNormPopulationWide, spreadDonorReputationOrNot)
        ###
        sumCoopRatio += cooperationRate
        generalCoopRatio = sumCoopRatio * 1.0 / iGeneration
        # if (iGeneration > 500000 and iGeneration % 500000 == 1) or iGeneration == 1:
        if (iGeneration > 10000 and iGeneration % 10000 == 1) or iGeneration == 1:
           print("Epoch[{}] , generalCoopRatio:{}".format(iGeneration,generalCoopRatio))
           temp = str(generalCoopRatio) + " "
           with open(fileName, "a") as f:
              f.write(temp)
           
		
        ### Update action rules according to the Fermi-imitation rule
        focalPlayer = np.random.choice(indexAllIndividuals,size =1)
        ### choose a role model different from the focal player
        RestPlayer = indexAllIndividuals.copy()
        np.delete(RestPlayer,focalPlayer)
        roleModel = np.random.choice(RestPlayer)
        probImitation = 1 / (1 + np.exp(-selectionIntensity * (payoffAll[roleModel] - payoffAll[focalPlayer])))
        if np.random.rand() < mutationRate:
            #### mutation occurs, switch to a random strategy
            actionRulePopulation[focalPlayer] = actionRulePossible[np.random.choice([0,1,3])]
            spreadDonorReputationOrNot[focalPlayer] = np.random.choice([0,1])
        elif np.random.rand() < probImitation:
            ### imitation happens, imitate the action rule of the role model
            actionRulePopulation[focalPlayer] = actionRulePopulation[roleModel]
            spreadDonorReputationOrNot[focalPlayer] = spreadDonorReputationOrNot[roleModel]



if __name__ == '__main__':
	Ntotal = 50 #dimention
	benefit = 1.0
	cost = 0.1

	numGeneration = 10000000 #Epoch

	mutationRate = 0.01;
	roundGamePerIndividual = 5

	probFailedCooperation = 0.05
	# probReverseReputation = 0.0;

	### Image Scoring -> 3, Stern Juding -> 9, Simple Standing -> 11
	indexSocialNormNow = 3 
	### set the output folder
	# outputFileFolder = r"D:\2020春课程资料\博弈论科研\代价声望传播\003_选择强度\Image_Scoring")

	if not os.path.exists('./result'):
		os.mkdir('./result')
	dir_str = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
	outputFileFolder = os.path.join("./result/{}".format(dir_str))
	os.mkdir(outputFileFolder)
	fileName = os.path.join(outputFileFolder , "coopRate.txt")
	if not os.path.exists(fileName):
		os.mknod(fileName)
	#### Second order norms
	orderNorm = 2
	#### action rule : (G, B) = (1, 0) means C with Good, D with Bad
	# actionRulePossible = hcat(digits.(Int, 0:(2^orderNorm - 1), base = 2, pad = orderNorm)...)'
	actionRulePossible = np.array([[0,0],[1,0],[0,1],[1,1]])
	### All action rules
	# 0  0 --- All D
	# 1  0 --- Discriminator
	# 0  1 --- paradoxical Discriminator
	# 1  1 --- All C

	#### social norm : (CG, CB, DG, DB) = (1, 0, 0, 1) --- Stern Judging
	#### means C with Good is Good, C with Good is Bad, D with Good is Bad, D with Bad is Good
	# socialNormPossible = hcat(digits.(Int, 0:(2^(2^orderNorm) - 1), base = 2, pad = 2^orderNorm)...)'
	socialNormPossible = np.array([
		[0,0,0,0],
		[1,0,0,0],
		[0,1,0,0],
		[1,1,0,0],
		[0,0,1,0],
		[1,0,1,0],
		[0,1,1,0],
		[1,1,1,0],
		[0,0,0,1],
		[1,0,0,1],
		[0,1,0,1],
		[1,1,0,1],
		[0,0,1,1],
		[1,0,1,1],
		[0,1,1,1],
		[1,1,1,1],
		])
	#### All social norms
	###(1)  0  0  0  0
	###(2)  1  0  0  0
	###(3)  0  1  0  0
	###(4)  1  1  0  0 --- Image Scoring
	###(5)  0  0  1  0
	###(6)  1  0  1  0
	###(7)  0  1  1  0
	###(8)  1  1  1  0
	###(9)  0  0  0  1
	###(10) 1  0  0  1 --- Stern Judging
	###(11) 0  1  0  1
	###(12) 1  1  0  1 --- Simple Standing
	###(13) 0  0  1  1
	###(14) 1  0  1  1
	###(15) 0  1  1  1
	###(16) 1  1  1  1
	###
	indexAllIndividuals = np.arange(0,Ntotal)

	### Run the evolution of action rules

	selectionIntensityArray = [1.7];
	for indexSelectionIntensity in range(len(selectionIntensityArray)):
		costSpreadReputation = 0.01
		selectionIntensity = selectionIntensityArray[indexSelectionIntensity]
		for iRepeat in range(1,4):
			fileNameMain = os.path.join(outputFileFolder , "coopRate_omega=" + str(selectionIntensity) + "_repeat" + str(iRepeat) + ".txt")
			if not os.path.exists(fileNameMain):
				os.mknod(fileNameMain)
			actionRuleDynamics(selectionIntensity, costSpreadReputation, fileNameMain)
	