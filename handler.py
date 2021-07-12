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
  'Easy': 1,
  'Medium': 1,
  'Hard': 1
}


def getNextTestItem(event, context):
  ## print("\n\nRequest Body (event):", event["body"], "\n\n")
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
    ## print("\n\nRequest Body (parsed):", body, "\n\n")
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
          'difficulty': DIFFICULTY_MAP[i['difficulty']],
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
    maxDifficulty, minDifficulty = 1, -1
    strictMode = False

    if 'strictMode' in body:
      strictMode = bool(body['strictMode'])

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
      visitedItemIndices = []
      for i in visitedItemIds:
        for j, k in enumerate(testItems):
          if i == k['testItemId']:
            visitedItemIndices.append(j)
      ## visitedItemByIndices = [testItems[i]['testItemId'] for i in visitedItemIndices]
      ## print('\nvisitedItemIds:', visitedItemIds, '\nvisitedItemIndices:', visitedItemIndices, '\nvisitedItemByIndices:', visitedItemByIndices, '\n')

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
      prevTestItemIndex, prevTestItemResponse = visitedItemIndices[-1], responses[-1]
      prevTestItem = testItems[prevTestItemIndex]
      ## print('\nprevTestItem:', prevTestItem, '\n\n')
      if (prevTestItemResponse and (prevTestItem['difficulty'] < maxDifficulty or strictMode)) or (not prevTestItemResponse and (prevTestItem['difficulty'] == minDifficulty) and not strictMode):
        acceptableDifficulties = [prevTestItem['difficulty']]
        if (prevTestItem['difficulty'] + 1 <= maxDifficulty):
          acceptableDifficulties.append(prevTestItem['difficulty'] + 1)
        ## print('\n1st', strictMode, acceptableDifficulties)
      else:
        acceptableDifficulties = [prevTestItem['difficulty']]
        if (prevTestItem['difficulty'] - 1 >= minDifficulty):
          acceptableDifficulties.append(prevTestItem['difficulty'] - 1)
        ## print('\n2nd', strictMode, acceptableDifficulties)
      nextTestItemIndex = getNextItemIndex(testItemsArray, visitedItemIndices, currentProficiency)
      while testItems[nextTestItemIndex]['difficulty'] not in acceptableDifficulties:
        nextTestItemIndex = getNextItemIndex(testItemsArray, visitedItemIndices, currentProficiency)
      # nextTestItemId: get testItemId for testItemIndex from testItems
      nextTestItemId = testItems[nextTestItemIndex]['testItemId']
      nextItemScore = testItems[nextTestItemIndex]['score']
      ## nextTestItemArray = np.array(testItems[nextTestItemIndex]['arrayValues'])
      ## nextCorrectProbability = getCorrectProbability(nextTestItemArray)
      
    # update and return response
    response.update({
      "statusCode": 200,
      "body": json.dumps({
        "testItemId": nextTestItemId,
        "itemScore": nextItemScore,
        "currentProficiency": estimatedProficiency,
        "currentScore": currentScore,
      })
    })
    return response
  except Exception as e:
    print(e)
    response.update({ "body": json.dumps({ "error": str(e) }) })
    return response
