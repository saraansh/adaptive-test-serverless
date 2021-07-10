import json
import numpy as np
from src.catsimUtils import *

## NOTE: Difficulty map (add more if required)
DIFFICULTY_MAP = {
  'Easy': -1,
  'Medium': 0,
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
    "body": { json.dumps({ "error": "empty function" }) }
  }

  try:
    # extract body object from json
    body = json.loads(event["body"])
  except Exception as e:
    print(e)
    response.update({ "body": json.dumps({ "error": "Failed to parse POST data" }) })
    return response

  try:
    testItemIds, visitedItemIds, responses = [], [], []
    estimatedProficiency = getInitialProficiency()
    nextTestItemId, nextCorrectProbability = '', None

    if 'testItemIds' in body:
      testItemIds = body['testItemIds']
    if 'visitedItemIds' in body:
      visitedItemIds = body['visitedItemIds']
    if 'visitedItemResponses' in body:
      responses = body['visitedItemResponses']

    # fetch testItemsMap (super set) from json
    with open('./src/testItemsData.json') as f:
      testItemsMap = json.load(f)

    # testItems: curate testItems subset from testItemsMap using testItemIds
    testItems = [
      { 'testItemId': i,
        'arrayValues': [testItemsMap[i]['score'], DIFFICULTY_MAP[testItemsMap[i]['difficulty']], 0, 1]
      } for i in testItemIds
    ]
    # testItemsArray: generate numpy 2D-array for testItems subset
    testItemsArray = np.array([i['arrayValues'] for i in testItems])

    # visitedItemIndices: get indices for visitedItemIds from testItems
    visitedItemIndices = [next((j for (j, data) in enumerate(testItems) if data['testItemId'] == i), None) for i in visitedItemIds]

    # update currentProficiency if there are valid visitedItems
    if 'currentProficiency' in body and len(visitedItemIndices):
      currentProficiency = body['currentProficiency']
      estimatedProficiency = getEstimatedProficiency(testItemsArray, visitedItemIndices, responses, currentProficiency)

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
      nextTestItemArray = np.array(testItems[nextTestItemIndex]['arrayValues'])
      nextCorrectProbability = getCorrectProbability(nextTestItemArray)
      print(nextTestItemId, nextTestItemArray, nextCorrectProbability)
      
    # update and return response
    response.update({
      "statusCode": 200,
      "body": json.dumps({
        "testItemId": nextTestItemId,
        "currentProficiency": estimatedProficiency,
        "correctProbability": nextCorrectProbability
      })
    })
    return response
  except Exception as e:
    print(e)
    response.update({ "body": json.dumps({ "error": str(e) }) })
    return response
