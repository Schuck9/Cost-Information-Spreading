using Random
using DelimitedFiles

function reputationDynamics(costSpreadReputation, actionRulePopulation, socialNormPopulationWide, spreadDonorReputationOrNot)
    ### Update reputation through rounds of donation games

    ### reset image matrix (everyone is randomly good or bad)
    imageArray = rand(0:1, Ntotal)
    imageMatrixTemp = ones(Int, Ntotal, Ntotal)
    for indexInd in 1:Ntotal
        imageMatrixTemp[:,indexInd] = ones(Ntotal) * imageArray[indexInd]
    end
    numCooperativeAction = 0;
    payoffAll = zeros(Ntotal);
    #####
    for iRound in 1:(Ntotal * roundGamePerIndividual)
        #### roundGamePerIndividual per individual
        donorNow = rand(indexAllIndividuals)
        ##### select the Recipient
        listRecipients = copy(indexAllIndividuals)
        indexDonorNow = findall(xx->xx == donorNow, listRecipients);
        deleteat!(listRecipients, indexDonorNow)
        recipientNow =  rand(listRecipients)
        ##### select the Observer
        listObservers = copy(listRecipients)
        indexRecipientNow = findall(xx->xx == recipientNow, listObservers)
        deleteat!(listObservers, indexRecipientNow)
        observerNow =  rand(listObservers)

        ##### Start the GAME
        actionRuleDonor = actionRulePopulation[donorNow, :];
        #### Action rule : (G, B) = (1, 0) means C with Good, D with Bad
        actionIntended = actionRuleDonor[2 - imageMatrixTemp[donorNow, recipientNow]];
        if actionIntended == 1 && rand() > probFailedCooperation
            ### Cooperate
            actionActual = 1;
        else
            #### Defect: fail to cooperate and intend to defect
            actionActual = 0;
        end
        numCooperativeAction = numCooperativeAction + actionActual;
        ### calculate payoffs
        payoffAll[donorNow] = payoffAll[donorNow] - cost * actionActual;
        payoffAll[recipientNow] = payoffAll[recipientNow] + benefit * actionActual;



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


        if spreadDonorReputationOrNot[observerNow] == 1
            reputationRecipientFromObserver = imageMatrixTemp[observerNow, recipientNow];
            ### Update the donor's reputation from Observer's eye
            imageMatrixTemp[observerNow, donorNow] = socialNormPopulationWide[2^orderNorm - (actionActual * 2 + reputationRecipientFromObserver)];
			### error in reputation assignment
            # if rand() < probReverseReputation
            #     imageMatrixTemp[observerNow, donorNow] = 1 - imageMatrixTemp[observerNow, donorNow];
            # end
            updatedReputationInTheEyesOfObserver = imageMatrixTemp[observerNow, donorNow]
            ### Observer spread the updated reputation of the Donor
            imageMatrixTemp[:, donorNow] = updatedReputationInTheEyesOfObserver * ones(Ntotal)
            ### Observer pays a cost --- costSpreadReputation
            payoffAll[observerNow] = payoffAll[observerNow] - costSpreadReputation
            ### Everyone thinks that the Observer is Good.
            imageMatrixTemp[:, observerNow] = ones(Ntotal)
            # println("Observer spreads Donor's reputation")
        end

        # println("Updated image matrix")
        # display(imageMatrixTemp)
        # sleep(15)

        # xyz
    end
    ### record cooperation rate
    cooperationRate = (numCooperativeAction * 1.0) / (Ntotal * roundGamePerIndividual)

    ### use Accumulated Payoffs

    return cooperationRate, payoffAll
end

function actionRuleDynamics(selectionIntensity, costSpreadReputation, fileName)
    ### initially indiviudals adopt random strategies from AllC, Disc, AllD
    indexActionRule = rand([1,2,4], Ntotal);
    actionRulePopulation = actionRulePossible[indexActionRule, :];
    ##
    spreadDonorReputationOrNot = rand([0, 1], Ntotal);

    ### Social norm currently in use
    socialNormPopulationWide = socialNormPossible[indexSocialNormNow, :];
    ###
    # println("Ntotal = $Ntotal");
    # println("actionRulePopulation");
    # println(actionRulePopulation);D
    # println("socialNormPopulationWide");
    # println(socialNormPopulationWide);
    #
	sumCoopRatio = 0
	
    for iGeneration in 1:numGeneration
        ### Reputation dynamics
        cooperationRate, payoffAll = reputationDynamics(costSpreadReputation, actionRulePopulation, socialNormPopulationWide, spreadDonorReputationOrNot);
        ###
		sumCoopRatio += cooperationRate
		generalCoopRatio = sumCoopRatio * 1.0 / iGeneration
		if (iGeneration > 500000 && iGeneration % 500000 == 1) || iGeneration == 1
		   temp = string(generalCoopRatio) * " "
           open(fileName, "a") do io
              write(io, temp);
           end
		end
        ### Update action rules according to the Fermi-imitation rule
        focalPlayer = rand(indexAllIndividuals); 
        ### choose a role model different from the focal player
        roleModel = rand(append!([1:focalPlayer - 1;], [focalPlayer + 1:Ntotal;]));
        probImitation = 1 / (1 + exp(-selectionIntensity * (payoffAll[roleModel] - payoffAll[focalPlayer])));
        if rand() < mutationRate
            #### mutation occurs, switch to a random strategy
            actionRulePopulation[focalPlayer, :] = actionRulePossible[rand([1,2,4]), :];
            spreadDonorReputationOrNot[focalPlayer] = rand([0,1])
        elseif rand() < probImitation
            ### imitation happens, imitate the action rule of the role model
            actionRulePopulation[focalPlayer, :] = actionRulePopulation[roleModel, :];
            spreadDonorReputationOrNot[focalPlayer] = spreadDonorReputationOrNot[roleModel]
        end
        ###
    end
end


#####------------------ Main program ----------------------------#####
Ntotal = 50
benefit = 1.0
cost = 0.1

numGeneration = 10000000;

mutationRate = 0.01;
roundGamePerIndividual = 5

probFailedCooperation = 0.05;
# probReverseReputation = 0.0;

### Image Scoring -> 4, Stern Juding -> 10, Simple Standing -> 12
indexSocialNormNow = 4
### set the output folder
outputFileFolder = raw"D:\2020春课程资料\博弈论科研\代价声望传播\003_选择强度\Image_Scoring"
fileName = outputFileFolder * "\\coopRate.txt";
#### Second order norms
orderNorm = 2;
#### action rule : (G, B) = (1, 0) means C with Good, D with Bad
actionRulePossible = hcat(digits.(Int, 0:(2^orderNorm - 1), base = 2, pad = orderNorm)...)';
### All action rules
# 0  0 --- All D
# 1  0 --- Discriminator
# 0  1 --- paradoxical Discriminator
# 1  1 --- All C

#### social norm : (CG, CB, DG, DB) = (1, 0, 0, 1) --- Stern Judging
#### means C with Good is Good, C with Good is Bad, D with Good is Bad, D with Bad is Good
socialNormPossible = hcat(digits.(Int, 0:(2^(2^orderNorm) - 1), base = 2, pad = 2^orderNorm)...)';
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
indexAllIndividuals = [1:Ntotal;];

### Run the evolution of action rules

selectionIntensityArray = [1.7];
for indexSelectionIntensity in 1:length(selectionIntensityArray)
    costSpreadReputation = 0.01
	selectionIntensity = selectionIntensityArray[indexSelectionIntensity]
	for iRepeat in 1:3
        fileNameMain = outputFileFolder * "\\coopRate" * "_omega=" * string(selectionIntensity) * "_repeat" * string(iRepeat) * ".txt";
        actionRuleDynamics(selectionIntensity, costSpreadReputation, fileNameMain)
    end
end
