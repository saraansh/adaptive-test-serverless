# adaptive-test-serverless

A simple serverless implementation to get the next item in adaptive test

## Requirements

- ### node v12.x
  
  via official website [Download | Node.js](https://nodejs.org/en/download/) or using **nvm**
  
  ```sh
  nvm install v12
  nvm use v12
  ```

- ### serverless v2.x
  
  ```sh
  npm install -g serverless@latest
  ```

- ### python 3.7 + pip 21.x
  
  [Search the web](https://www.google.com/search?q=python+3.7+install+ubuntu&oq=python+3.7+install&aqs=chrome.1.69i57j0l6j69i60.11890j0j7&sourceid=chrome&ie=UTF-8)


## Steps to run the app

1. Clone the repo

    ```sh
    git clone git@github.com:saraansh/adaptive-test-serverless.git
    ```

2. Cleanup & install packages

    ```sh
    rm -rf ./node_modules
    rm *-lock.json
    npm install
    ```

3. Install python modules
  
    ```sh
    pip install -r requirements.txt
    ```

4. Start the app (offline mode)

    ```sh
    npm run start:offline
    ```

6. With the app running, you can now call the following endpoints:
  
    i. **`get-next-test-item`** [📎](http://localhost:5000/development/get-next-test-item)

      ```sh
      curl --location --request POST 'http://localhost:5000/development/get-next-test-item' \
      --header 'Content-Type: application/json' \
      --data-raw '{
          "testItemIds": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
          "visitedItemIds": ["7", "4"],
          "visitedItemResponses": [false, true],
          "currentProficiency": 0,
          "maxVisitedItemsCount": 5
      }'
      
      ```