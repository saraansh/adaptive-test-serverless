import json
import numpy as np
from src.catsimUtils import *

## NOTE: Difficulty map (add more if required)
DIFFICULTY_MAP = {
  'Easy': -1,
  'Medium': 0,
  'Hard': 1
}

## NOTE: Score multiplication factor (remove if not required)
SCORE_MUL_FACTOR = {
  'Easy': 0.25,
  'Medium': 0.5,
  'Hard': 1
}


def getNextTestItem(event, context):
  # print("Request Body: ", event["body"])
  # initialize response object
  response = {
    "headers": {
      "Access-Control-Allow-Origin": "*"
    },
    "statusCode": 500,
    "body": json.dumps({ "error": "empty function" })
  }

  try:
    # extract body object from json
    body = json.loads(event["body"])
  except Exception as e:
    print(e)
    response.update({ "body": json.dumps({ "error": "Failed to parse POST data" }) })
    return response

  try:
    # fetch testItemsMap (super set) from json
    with open('./src/testItemsData.json') as f:
      rawTestItems = json.load(f)
      testItems = [
        {
          **i,
          'score': i['score'] * SCORE_MUL_FACTOR[i['difficulty']],
          'arrayValues': [
            i['score'] * SCORE_MUL_FACTOR[i['difficulty']],
            DIFFICULTY_MAP[i['difficulty']],
            0,
            1
          ]
        } for i in rawTestItems
      ]
      testItemIds = [i['testItemId'] for i in testItems]
    
    visitedItemIds, responses = [], []
    estimatedProficiency = getInitialProficiency()
    nextTestItemId, nextCorrectProbability = '', None

    if 'testItemIds' in body:
      testItemIds = body['testItemIds']
      if len(testItemIds):
        # testItems: curate testItems subset using testItemIds from request body
        testItems = [i for i in testItems if i['testItemId'] in testItemIds]
    
    # testItemsArray: generate numpy 2D-array for testItems
    testItemsArray = np.array([i['arrayValues'] for i in testItems])

    if 'visitedItemIds' in body:
      visitedItemIds = body['visitedItemIds']
      # visitedItemIndices: get indices for visitedItemIds from testItems
      visitedItemIndices = [i for (i, j) in enumerate(testItems) if j['testItemId'] in visitedItemIds]

    if 'visitedItemResponses' in body:
      responses = body['visitedItemResponses']

    # currentScore: get the current cumulative score for visitedItems
    currentScore = sum([testItems[j]['score'] for (i, j) in enumerate(visitedItemIndices) if responses[i] == True])

    # update currentProficiency if there are valid visitedItems
    if 'currentProficiency' in body and len(visitedItemIndices):
      currentProficiency = body['currentProficiency']
      estimatedProficiency = getEstimatedProficiency(testItemsArray, visitedItemIndices, responses, currentProficiency)
      if estimatedProficiency == float('inf'):
        estimatedProficiency = 100
      elif estimatedProficiency == float('-inf'):
        estimatedProficiency = -100


    # get max count for visited items
    maxVisitedItemsCount = len(testItemsArray)
    if 'maxVisitedItemsCount' in body:
      maxVisitedItemsCount = body['maxVisitedItemsCount']

    # check for stopFlag before calculating next item
    stopFlag = getStopFlag(testItemsArray, visitedItemIndices, currentProficiency, maxVisitedItemsCount)
    if stopFlag == False:
      nextTestItemIndex = getNextItemIndex(testItemsArray, visitedItemIds, currentProficiency)
      # nextTestItemId: get testItemId for testItemIndex from testItems
      nextTestItemId = testItems[nextTestItemIndex]['testItemId']
      nextItemScore = testItems[nextTestItemIndex]['score']
      nextTestItemArray = np.array(testItems[nextTestItemIndex]['arrayValues'])
      # nextCorrectProbability = getCorrectProbability(nextTestItemArray)
      
    # update and return response
    response.update({
      "statusCode": 200,
      "body": json.dumps({
        "testItemId": nextTestItemId,
        "itemScore": nextItemScore,
        "currentProficiency": estimatedProficiency,
        "currentScore": currentScore
      })
    })
    return response
  except Exception as e:
    print(e)
    response.update({ "body": json.dumps({ "error": str(e) }) })
    return response
