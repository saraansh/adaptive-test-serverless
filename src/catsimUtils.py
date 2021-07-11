from catsim.initialization import FixedPointInitializer
from catsim.selection import The54321Selector
from catsim.estimation import NumericalSearchEstimator
from catsim.stopping import MaxItemStopper
from catsim.irt import icc

def getInitialProficiency (currentProficiency = 0):
  initializer = FixedPointInitializer(currentProficiency)
  initialProficiency = initializer.initialize()
  # print('Examinee initial proficiency:', initialProficiency)
  return initialProficiency


def getEstimatedProficiency (testItemsArray, visitedItemIndices, responses, currentProficiency):
  estimator = NumericalSearchEstimator(dodd=False, method="dichotomous")
  estimatedProficiency = estimator.estimate(items=testItemsArray, administered_items=visitedItemIndices, response_vector=responses, est_theta=currentProficiency)
  # print('Examinee estimated proficiency:', estimatedProficiency)
  return estimatedProficiency


def getNextItemIndex (testItemsArray, visitedItemIndices, currentProficiency):
  selector = The54321Selector(test_size=len(testItemsArray))
  testItemIndex = selector.select(items=testItemsArray, administered_items=visitedItemIndices, est_theta=currentProficiency)
  # ensure no duplicate item is selected
  while testItemIndex in visitedItemIndices:
    testItemIndex = selector.select(items=testItemsArray, administered_items=visitedItemIndices, est_theta=currentProficiency)
  return testItemIndex


def getStopFlag (testItemsArray, visitedItemIndices, currentProficiency, maxVisitedItemsCount):
  stopper = MaxItemStopper(maxVisitedItemsCount)
  stopFlag = stopper.stop(administered_items=testItemsArray[visitedItemIndices], theta=currentProficiency)
  return stopFlag

## TODO: check the reasoning behind trueProficiency
def getCorrectProbability (testItemArray, trueProficiency = 2):
  a, b, c, d = testItemArray
  correctProbability = icc(trueProficiency, a, b, c, d)
  # print('Probability to correctly answer item:', correctProbability)
  return correctProbability
