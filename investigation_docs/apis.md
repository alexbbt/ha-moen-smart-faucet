# API Captures

This doc outlines the important API calls for the moen faucet control.

## Login

### Request
POST: https://4j1gkf0vji.execute-api.us-east-2.amazonaws.com/prod/v1/oauth2/token
content-type: application/x-www-form-urlencoded
user-agent: Smartwater-iOS-prod-3.39.0

``` JSON
'{"password":"<REDACTED>","client_id":"<REDACTED>","username":"<REDACTED>"}': ''
```

### Response
``` JSON
{
    "token": {
        "id_token": "<REDACTED>",
        "access_token": "<REDACTED>",
        "token_type": "Bearer",
        "refresh_token": "<REDACTED>",
        "expires_in": 3600
    }
}
```


## Account Info

### Request
GET: https://4j1gkf0vji.execute-api.us-east-2.amazonaws.com/prod/v1/users/me
content-type: application/json
user-agent: Smartwater-iOS-prod-3.39.0
authorization: Bearer <REDACTED>


### Response

```JSON
{
    "status": "CONFIRMED",
    "enabled": true,
    "createDate": "2025-02-19T17:22:24.668Z",
    "updateDate": "2025-02-19T17:22:39.350Z",
    "id": "7d29a42e-0ac8-4567-b24b-4f2af3b867bc",
    "legacyId": "us-east-2:55cca2c3-e429-c7d7-779b-69fa9f8cd02d",
    "emailVerified": true,
    "firstName": "<REDACTED>",
    "lastName": "<REDACTED>",
    "email": "<REDACTED>",
    "account": {
        "id": "cf81f8f7-7dae-44ea-879d-9b3b06a82a68"
    },
    "integrations": {
        "flo": {
            "state": "synced"
        }
    }
}
```

## Get Locations

### Request

GET: https://api.prod.iot.moen.com/v3/locations?limit=100
authorization: Bearer
content-type: application/json
user-agent: Smartwater-iOS-prod-3.39.0
authorization: Bearer <REDACTED>

### Response

```JSON
{
    "params": {
        "userId": "7d29a42e-0ac8-4567-b24b-4f2af3b867bc",
        "start": 0,
        "limit": 100,
        "rootOnly": false
    },
    "total": 1,
    "locations": [
        {
            "id": "859b049b-d917-416b-b271-dbbf531be112",
            "level": 0,
            "name": "<REDACTED>",
            "address": "<REDACTED>",
            "city": "<REDACTED>",
            "state": "<REDACTED>",
            "country": "<REDACTED>",
            "postalCode": "<REDACTED>",
            "geolocation": {
                "lat": 47.0000000,
                "lng": -122.0000000,
                "precision": "specific",
                "src": "system"
            },
            "timeZone": "America/Los_Angeles",
            "account": {
                "id": "cf81f8f7-7dae-44ea-879d-9b3b06a82a68"
            },
            "preferences": {
                "childModeEnabled": false,
                "childLimitTemp": 40.56,
                "safetyLimitTemp": 48.89,
                "safetyModeEnabled": true
            },
            "src": "system",
            "linkedLocations": {
                "flo": {
                    "id": "109b13b0-bd11-469a-9c4f-0765b3c26b52",
                    "linked": "2025-02-19T17:23:25.585Z"
                }
            },
            "createdAt": 1739985745254
        }
    ]
}
```

## Get User Details and Tempature Definitions:

### Request

POST: https://exo9f857n8.execute-api.us-east-2.amazonaws.com/prod/v1/invoker
content-type: application/json
authorization: Bearer <REDACTED>
user-agent: Smartwater-iOS-prod-3.39.0

```JSON
{
    "body": {
        "locale": "en_US"
    },
    "escape": false,
    "fn": "smartwater-app-user-api-prod-get",
    "parse": false
}
```
### Response

```JSON
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST",
    "Payload": "{\"statusCode\":200,\"body\":{\"createdAt\":1739985759369,\"defaultFaucet\":\"101046568\",\"externalProviderId\":\"7d29a42e-0ac8-4567-b24b-4f2af3b867bc\",\"federatedIdentity\":\"us-east-2:55cca2c3-e429-c7d7-779b-69fa9f8cd02d\",\"firstName\":\"<REDACTED>\",\"identityProvider\":\"COGNITO\",\"language\":\"en_US\",\"lastName\":\"<REDACTED>\",\"locale\":\"en_US\",\"temperatureDefinitions\":{\"hot\":\"hottest\",\"<REDACTED>rm\":40.56,\"cold\":\"coldest\"},\"updatedAt\":1748908101250,\"username\":\"<REDACTED>\"}}"
}
```

## List Devices

This lists multiple device types, we should ignore FLO devices, as those are handled by another integration, but we <REDACTED>nna look for VAK devices.

### Request

POST: https://exo9f857n8.execute-api.us-east-2.amazonaws.com/prod/v1/invoker
content-type: application/json
authorization: Bearer <REDACTED>
user-agent: Smartwater-iOS-prod-3.39.0

```JSON
{
    "parse": false,
    "body": {
        "locale": "en_US"
    },
    "fn": "smartwater-app-device-api-prod-list",
    "escape": false
}
```
### Response

```JSON
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST",
    "Payload": "{\"statusCode\":200,\"body\":[{\"duid\":\"b31f2954-f449-4788-adc1-bc88a8e731fd\",\"nickname\":\"Kitchen Faucet\",\"federatedIdentity\":\"us-east-2:55cca2c3-e429-c7d7-779b-69fa9f8cd02d\",\"deviceType\":\"VAK\",\"createdAt\":1759184574359,\"roomId\":\"1ebee350-eee6-11ef-b7a7-cf353cf3130f\",\"locationId\":\"859b049b-d917-416b-b271-dbbf531be112\",\"color\":\"2b59c3\",\"sku\":\"300000\",\"clientId\":\"101046568\",\"defaultFaucet\":true,\"firm<REDACTED>reVersion\":\"v1.1.8c\",\"wifiNetwork\":\"temp\",\"connected\":true,\"lastConnect\":1759263362470,\"wifiRssi\":-73,\"wifiNoPoll\":false,\"state\":\"idle\",\"flowCalSrc\":\"factory\",\"beeperVolume\":0,\"sensorDisable\":0,\"freezeEnable\":false,\"defaultFlowRate\":100,\"maxFlowRate\":100,\"trickleFlowRate\":10,\"purgeTimeout\":120,\"handleTimeout\":300,\"sensorTimeout\":300,\"voiceTimeout\":300,\"dispenseActivateTimeout\":120,\"safetyLimitTemp\":48.889999,\"safetyModeEnabled\":true,\"childLimitTemp\":40.560001,\"childModeEnabled\":false,\"defaultTemp\":\"handle\",\"handleReverse\":false,\"gestureMode\":\"na\",\"setpointColdTemp\":0,\"setpoint<REDACTED>rmTemp\":40.556,\"setpointHotTemp\":100,\"lowFlowRate\":50,\"unwinterizeTimeout\":60,\"healthProtectTimeout\":120,\"sensorConfig\":\"gesture_handle\",\"batteryLifeRemaining\":-1,\"batteryPercentage\":100,\"batterySavingLevel\":\"normal\",\"powerSource\":\"battery\",\"volume\":497082,\"temperature\":26.681999,\"temperatureLast\":28.385,\"learnedMinTemp\":24.283001,\"learnedMaxTemp\":49.328999,\"temperatureGoal\":\"specific\",\"assemblyAirTemp\":21,\"isFreezing\":false},{\"duid\":\"c0355c5d-6e49-4f6f-b063-76222ec2bb67\",\"nickname\":\"Flo Shutoff\",\"federatedIdentity\":\"us-east-2:55cca2c3-e429-c7d7-779b-69fa9f8cd02d\",\"deviceType\":\"FLO\",\"updatedAt\":1756748363392,\"createdAt\":1739986111712,\"roomId\":\" \",\"locationId\":\"859b049b-d917-416b-b271-dbbf531be112\",\"clientId\":\"c0355c5d-6e49-4f6f-b063-76222ec2bb67\"}]}"
}
```

## List Presets

### Request

POST: https://exo9f857n8.execute-api.us-east-2.amazonaws.com/prod/v1/invoker
content-type: application/json
authorization: Bearer <REDACTED>
user-agent: Smartwater-iOS-prod-3.39.0

```JSON
{
    "body": {
        "locale": "en_US"
    },
    "fn": "smartwater-app-preset-api-prod-list",
    "escape": false,
    "parse": false
}
```
### Response

```JSON
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST",
    "Payload": "{\"statusCode\":200,\"body\":[]}"
}
```

## List Locations

### Request

POST: https://exo9f857n8.execute-api.us-east-2.amazonaws.com/prod/v1/invoker
content-type: application/json
authorization: Bearer <REDACTED>
user-agent: Smartwater-iOS-prod-3.39.0

```JSON
{
    "parse": false,
    "body": {
        "locale": "en_US"
    },
    "fn": "smartwater-app-location-api-prod-list",
    "escape": false
}
```
### Response

```JSON
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST",
    "Payload": "{\"statusCode\":200,\"body\":[{\"src\":\"moen\",\"nickname\":\"<REDACTED>\",\"federatedIdentity\":\"us-east-2:55cca2c3-e429-c7d7-779b-69fa9f8cd02d\",\"safetyLimitTemp\":48.89,\"childModeEnabled\":false,\"childLimitTemp\":40.56,\"safetyModeEnabled\":true,\"locationId\":\"859b049b-d917-416b-b271-dbbf531be112\"}]}"
}
```

## Expand Device Attributes

This is where we can fetch details about the device like wifi strength and network. Good for debugging info.

### Request

GET https://api.prod.iot.moen.com/v3/device/b31f2954-f449-4788-adc1-bc88a8e731fd?expand=addons&units=imperial HTTP/2.0
content-type: application/json
user-agent: Smartwater-iOS-prod-3.39.0
authorization: Bearer <REDACTED>

Query Params

```YAML
expand: addons
units: imperial
```
### Response

```JSON
{
    "duid": "b31f2954-f449-4788-adc1-bc88a8e731fd",
    "clientId": "101046568",
    "nickname": "Kitchen Faucet",
    "type": "vak",
    "location": {
        "id": "859b049b-d917-416b-b271-dbbf531be112"
    },
    "connected": true,
    "lastConnect": "2025-09-30T20:16:02.470Z",
    "connectivity": {
        "type": "wifi",
        "net": "temp",
        "rssi": -73
    },
    "firm<REDACTED>re": {
        "version": "v1.1.8c"
    },
    "powerSource": "battery",
    "battery": {
        "percentage": 100
    }
}
```

## Winterize

I think this might be the toggle option.

### Request

GET https://api.prod.iot.moen.com/v1/actions/routine/winterize?location=859b049b-d917-416b-b271-dbbf531be112 HTTP/2.0
content-type: application/json
user-agent: Smartwater-iOS-prod-3.39.0
authorization: Bearer <REDACTED>

Query Params
```YAML
location: 859b049b-d917-416b-b271-dbbf531be112
```
### Response

```JSON
{
    "winterize": false,
    "routine": "winterize",
    "modified": 1759132850855,
    "locationId": "859b049b-d917-416b-b271-dbbf531be112"
}
```


## Shadow?

### Request

POST: https://exo9f857n8.execute-api.us-east-2.amazonaws.com/prod/v1/invoker
content-type: application/json
authorization: Bearer <REDACTED>
user-agent: Smartwater-iOS-prod-3.39.0

```JSON
{
    "parse": false,
    "fn": "smartwater-app-shadow-api-prod-get",
    "escape": false,
    "body": {
        "clientId": "101046568",
        "shadow": true,
        "locale": "en_US"
    }
}
```
### Response

```JSON
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST",
    "Payload": "{\"statusCode\":200,\"body\":{\"state\":{\"desired\":{\"safetyModeEnabled\":true,\"childModeEnabled\":false,\"sensorTimeout\":300,\"voiceTimeout\":300,\"handleTimeout\":300,\"dispenseActivateTimeout\":120,\"defaultFlowRate\":100,\"deviceLost\":true,\"freezeEnable\":false},\"reported\":{\"firm<REDACTED>reVersion\":\"v1.1.8c\",\"wifiNetwork\":\"temp\",\"connected\":true,\"lastConnect\":1759263362470,\"wifiRssi\":-73,\"wifiNoPoll\":false,\"state\":\"idle\",\"flowCalSrc\":\"factory\",\"beeperVolume\":0,\"sensorDisable\":0,\"freezeEnable\":false,\"defaultFlowRate\":100,\"maxFlowRate\":100,\"trickleFlowRate\":10,\"purgeTimeout\":120,\"handleTimeout\":300,\"sensorTimeout\":300,\"voiceTimeout\":300,\"dispenseActivateTimeout\":120,\"safetyLimitTemp\":48.889999,\"safetyModeEnabled\":true,\"childLimitTemp\":40.560001,\"childModeEnabled\":false,\"defaultTemp\":\"handle\",\"handleReverse\":false,\"gestureMode\":\"na\",\"setpointColdTemp\":0,\"setpoint<REDACTED>rmTemp\":40.556,\"setpointHotTemp\":100,\"lowFlowRate\":50,\"unwinterizeTimeout\":60,\"healthProtectTimeout\":120,\"sensorConfig\":\"gesture_handle\",\"batteryLifeRemaining\":-1,\"batteryPercentage\":100,\"batterySavingLevel\":\"normal\",\"powerSource\":\"battery\",\"volume\":497082,\"temperature\":26.681999,\"temperatureLast\":28.385,\"learnedMinTemp\":24.283001,\"learnedMaxTemp\":49.328999,\"temperatureGoal\":\"specific\",\"assemblyAirTemp\":21,\"isFreezing\":false},\"delta\":{\"deviceLost\":true}},\"metadata\":{\"desired\":{\"safetyModeEnabled\":{\"timestamp\":1759184574},\"childModeEnabled\":{\"timestamp\":1759184574},\"sensorTimeout\":{\"timestamp\":1759254995},\"voiceTimeout\":{\"timestamp\":1759254995},\"handleTimeout\":{\"timestamp\":1759254995},\"dispenseActivateTimeout\":{\"timestamp\":1759254995},\"defaultFlowRate\":{\"timestamp\":1759184891},\"deviceLost\":{\"timestamp\":1759243730},\"freezeEnable\":{\"timestamp\":1759254995}},\"reported\":{\"firm<REDACTED>reVersion\":{\"timestamp\":1759254956},\"wifiNetwork\":{\"timestamp\":1759263366},\"connected\":{\"timestamp\":1759263366},\"lastConnect\":{\"timestamp\":1759263366},\"wifiRssi\":{\"timestamp\":1759254956},\"wifiNoPoll\":{\"timestamp\":1759254956},\"state\":{\"timestamp\":1759269624},\"flowCalSrc\":{\"timestamp\":1759254956},\"beeperVolume\":{\"timestamp\":1759254956},\"sensorDisable\":{\"timestamp\":1759254956},\"freezeEnable\":{\"timestamp\":1759254956},\"defaultFlowRate\":{\"timestamp\":1759254956},\"maxFlowRate\":{\"timestamp\":1759254956},\"trickleFlowRate\":{\"timestamp\":1759254956},\"purgeTimeout\":{\"timestamp\":1759254956},\"handleTimeout\":{\"timestamp\":1759254956},\"sensorTimeout\":{\"timestamp\":1759254956},\"voiceTimeout\":{\"timestamp\":1759254956},\"dispenseActivateTimeout\":{\"timestamp\":1759254956},\"safetyLimitTemp\":{\"timestamp\":1759254956},\"safetyModeEnabled\":{\"timestamp\":1759254956},\"childLimitTemp\":{\"timestamp\":1759254956},\"childModeEnabled\":{\"timestamp\":1759254956},\"defaultTemp\":{\"timestamp\":1759255003},\"handleReverse\":{\"timestamp\":1759254956},\"gestureMode\":{\"timestamp\":1759254956},\"setpointColdTemp\":{\"timestamp\":1759254956},\"setpoint<REDACTED>rmTemp\":{\"timestamp\":1759254956},\"setpointHotTemp\":{\"timestamp\":1759254956},\"lowFlowRate\":{\"timestamp\":1759254956},\"unwinterizeTimeout\":{\"timestamp\":1759254956},\"healthProtectTimeout\":{\"timestamp\":1759254956},\"sensorConfig\":{\"timestamp\":1759254956},\"batteryLifeRemaining\":{\"timestamp\":1759254956},\"batteryPercentage\":{\"timestamp\":1759254956},\"batterySavingLevel\":{\"timestamp\":1759254956},\"powerSource\":{\"timestamp\":1759254956},\"volume\":{\"timestamp\":1759269624},\"temperature\":{\"timestamp\":1759269624},\"temperatureLast\":{\"timestamp\":1759269624},\"learnedMinTemp\":{\"timestamp\":1759254975},\"learnedMaxTemp\":{\"timestamp\":1759254975},\"temperatureGoal\":{\"timestamp\":1759269624},\"assemblyAirTemp\":{\"timestamp\":1759263686},\"isFreezing\":{\"timestamp\":1759263686}}},\"version\":1429,\"timestamp\":1759270686}}"
}
```


## Get Daily Ussage

Can be used to store stats about <REDACTED>ter usage.

### Request

POST: https://exo9f857n8.execute-api.us-east-2.amazonaws.com/prod/v1/invoker
content-type: application/json
authorization: Bearer <REDACTED>
user-agent: Smartwater-iOS-prod-3.39.0

```JSON
{
    "parse": false,
    "body": {
        "devices": [
            "101046568"
        ],
        "timezoneOffset": -7,
        "depth": "DAILY",
        "locale": "en_US",
        "queryDate": 1759270686,
        "future": true
    },
    "fn": "smartwater-app-usage-api-prod-get-v1",
    "escape": false
}
```
### Response

```JSON
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST",
    "Payload": "{\"statusCode\":200,\"body\":{\"current\":{\"usage\":{\"0\":0,\"1\":1078893,\"2\":0,\"3\":0,\"4\":0,\"5\":0,\"6\":0,\"7\":0,\"8\":949511,\"9\":75031,\"10\":3475465,\"11\":134519,\"12\":3026539,\"13\":0,\"14\":0,\"15\":497082,\"16\":0,\"17\":0,\"18\":0,\"19\":0,\"20\":0,\"21\":0,\"22\":0,\"23\":0},\"total\":9237040},\"future\":{\"usage\":{\"0\":0,\"1\":0,\"2\":0,\"3\":0,\"4\":0,\"5\":0,\"6\":0,\"7\":0,\"8\":0,\"9\":0,\"10\":0,\"11\":0,\"12\":0,\"13\":0,\"14\":0,\"15\":0,\"16\":0,\"17\":0,\"18\":0,\"19\":0,\"20\":0,\"21\":0,\"22\":0,\"23\":0}}}}"
}
```


## Session

Not really sure what this does.

### Request

POST: https://exo9f857n8.execute-api.us-east-2.amazonaws.com/prod/v1/invoker
content-type: application/json
authorization: Bearer <REDACTED>
user-agent: Smartwater-iOS-prod-3.39.0

```JSON
{
    "body": {
        "limit": 5,
        "locale": "en_US",
        "clientId": "101046568"
    },
    "escape": false,
    "fn": "smartwater-app-session-api-prod-get-v1",
    "parse": false
}
```
### Response

```JSON
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST",
    "Payload": "{\"statusCode\":200,\"body\":{\"data\":[{\"secondGesture\":9,\"motorCurrentHotMilliAmpSeconds\":61,\"minTempC\":24.792,\"timeToTargetTemp\":0,\"maxFlowUlPerSec\":60645,\"source\":\"sensor\",\"sessionEndReason\":\"complete\",\"motorCurrentColdMilliAmpSeconds\":103,\"firstGesture\":9,\"clientId\":\"101046568\",\"durationMs\":8996,\"targetTempC\":37.117001,\"cmdSrcBitmask\":12,\"thirdGesture\":9,\"avgTempC\":26.681999,\"maxTempC\":28.385,\"totalGestures\":0,\"purgeVolUl\":0,\"gesturesUsedBitmask\":0,\"motorActiveHotTimeMs\":492,\"totalVolUl\":497082,\"motorActiveColdTimeMs\":840,\"timestamp\":1759269612},{\"secondGesture\":9,\"motorCurrentHotMilliAmpSeconds\":0,\"minTempC\":24.337,\"timeToTargetTemp\":0,\"maxFlowUlPerSec\":19987,\"source\":\"handle\",\"sessionEndReason\":\"complete\",\"motorCurrentColdMilliAmpSeconds\":41,\"firstGesture\":9,\"clientId\":\"101046568\",\"durationMs\":129,\"targetTempC\":0,\"cmdSrcBitmask\":8,\"thirdGesture\":9,\"avgTempC\":24.407,\"maxTempC\":24.472,\"totalGestures\":0,\"purgeVolUl\":0,\"gesturesUsedBitmask\":0,\"motorActiveHotTimeMs\":0,\"totalVolUl\":2575,\"motorActiveColdTimeMs\":204,\"timestamp\":1759260638},{\"secondGesture\":9,\"motorCurrentHotMilliAmpSeconds\":0,\"minTempC\":24.525,\"timeToTargetTemp\":0,\"maxFlowUlPerSec\":56940,\"source\":\"handle\",\"sessionEndReason\":\"complete\",\"motorCurrentColdMilliAmpSeconds\":97,\"firstGesture\":9,\"clientId\":\"101046568\",\"durationMs\":17380,\"targetTempC\":0,\"cmdSrcBitmask\":12,\"thirdGesture\":9,\"avgTempC\":25.410999,\"maxTempC\":26.548,\"totalGestures\":0,\"purgeVolUl\":0,\"gesturesUsedBitmask\":0,\"motorActiveHotTimeMs\":0,\"totalVolUl\":941296,\"motorActiveColdTimeMs\":720,\"timestamp\":1759260616},{\"secondGesture\":9,\"motorCurrentHotMilliAmpSeconds\":0,\"minTempC\":26.497999,\"timeToTargetTemp\":0,\"maxFlowUlPerSec\":55477,\"source\":\"handle\",\"sessionEndReason\":\"complete\",\"motorCurrentColdMilliAmpSeconds\":100,\"firstGesture\":9,\"clientId\":\"101046568\",\"durationMs\":12264,\"targetTempC\":0,\"cmdSrcBitmask\":8,\"thirdGesture\":9,\"avgTempC\":26.662001,\"maxTempC\":28.127001,\"totalGestures\":0,\"purgeVolUl\":0,\"gesturesUsedBitmask\":0,\"motorActiveHotTimeMs\":0,\"totalVolUl\":644106,\"motorActiveColdTimeMs\":948,\"timestamp\":1759260590},{\"secondGesture\":9,\"motorCurrentHotMilliAmpSeconds\":65,\"minTempC\":29.597,\"timeToTargetTemp\":9635,\"maxFlowUlPerSec\":78097,\"source\":\"handle\",\"sessionEndReason\":\"complete\",\"motorCurrentColdMilliAmpSeconds\":79,\"firstGesture\":9,\"clientId\":\"101046568\",\"durationMs\":14768,\"targetTempC\":0,\"cmdSrcBitmask\":8,\"thirdGesture\":9,\"avgTempC\":32.000999,\"maxTempC\":33.944,\"totalGestures\":0,\"purgeVolUl\":0,\"gesturesUsedBitmask\":0,\"motorActiveHotTimeMs\":584,\"totalVolUl\":1058943,\"motorActiveColdTimeMs\":580,\"timestamp\":1759259252}],\"lastEvaluatedKey\":{\"clientId\":\"101046568\",\"timestamp\":1759259252}}}"
}
```


## Update

This might be the process to enable the <REDACTED>ter

### Request

POST: https://exo9f857n8.execute-api.us-east-2.amazonaws.com/prod/v1/invoker
content-type: application/json
authorization: Bearer <REDACTED>
user-agent: Smartwater-iOS-prod-3.39.0

These four request bodys all have the same response

```JSON
{
    "parse": false,
    "body": {
        "payload": {
            "commandSrc": "app",
            "freezeEnable": false
        },
        "locale": "en_US",
        "clientId": "101046568"
    },
    "fn": "smartwater-app-shadow-api-prod-update",
    "escape": false
}
```

```JSON
{
    "parse": false,
    "body": {
        "locale": "en_US",
        "payload": {
            "commandSrc": "app",
            "handleTimeout": 300
        },
        "clientId": "101046568"
    },
    "fn": "smartwater-app-shadow-api-prod-update",
    "escape": false
}
```

```JSON
{
    "escape": false,
    "parse": false,
    "fn": "smartwater-app-shadow-api-prod-update",
    "body": {
        "payload": {
            "commandSrc": "app",
            "sensorTimeout": 300,
            "voiceTimeout": 300
        },
        "locale": "en_US",
        "clientId": "101046568"
    }
}
```

```JSON
{
    "fn": "smartwater-app-shadow-api-prod-update",
    "escape": false,
    "parse": false,
    "body": {
        "locale": "en_US",
        "payload": {
            "commandSrc": "app",
            "dispenseActivateTimeout": 120
        },
        "clientId": "101046568"
    }
}
```

### Response

```JSON
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST",
    "Payload": "{\"statusCode\":200,\"body\":{\"status\":true}}"
}
```


## Setting temp to coldest

### Request

POST: https://exo9f857n8.execute-api.us-east-2.amazonaws.com/prod/v1/invoker
content-type: application/json
authorization: Bearer <REDACTED>
user-agent: Smartwater-iOS-prod-3.39.0

```JSON
{
    "parse": false,
    "fn": "smartwater-app-shadow-api-prod-update",
    "body": {
        "payload": {
            "flowRate": 100,
            "temperature": "coldest",
            "commandSrc": "app",
            "command": "run"
        },
        "locale": "en_US",
        "clientId": "101046568"
    },
    "escape": false
}
```
### Response

```JSON
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST",
    "Payload": "{\"statusCode\":200,\"body\":{\"status\":true}}"
}
```


## Turn off the <REDACTED>ter

### Request

POST: https://exo9f857n8.execute-api.us-east-2.amazonaws.com/prod/v1/invoker
content-type: application/json
authorization: Bearer <REDACTED>
user-agent: Smartwater-iOS-prod-3.39.0

```JSON
{
    "parse": false,
    "escape": false,
    "fn": "smartwater-app-shadow-api-prod-update",
    "body": {
        "payload": {
            "commandSrc": "app",
            "command": "stop"
        },
        "clientId": "101046568",
        "locale": "en_US"
    }
}
```
### Response

```JSON
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST",
    "Payload": "{\"statusCode\":200,\"body\":{\"status\":true}}"
}
```


## Set hottest

### Request

POST: https://exo9f857n8.execute-api.us-east-2.amazonaws.com/prod/v1/invoker
content-type: application/json
authorization: Bearer <REDACTED>
user-agent: Smartwater-iOS-prod-3.39.0

```JSON
{
    "parse": false,
    "body": {
        "payload": {
            "flowRate": 100,
            "temperature": "hottest",
            "commandSrc": "app",
            "command": "run"
        },
        "clientId": "101046568",
        "locale": "en_US"
    },
    "fn": "smartwater-app-shadow-api-prod-update",
    "escape": false
}
```
### Response

```JSON
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST",
    "Payload": "{\"statusCode\":200,\"body\":{\"status\":true}}"
}
```

## Set Specific Temp

### Request

POST: https://exo9f857n8.execute-api.us-east-2.amazonaws.com/prod/v1/invoker
content-type: application/json
authorization: Bearer <REDACTED>
user-agent: Smartwater-iOS-prod-3.39.0

Here are a few examples, they all seem to take decimal celcius, which can be from converting from F

```JSON
{
    "parse": false,
    "fn": "smartwater-app-shadow-api-prod-update",
    "body": {
        "locale": "en_US",
        "payload": {
            "flowRate": 100,
            "temperature": 23.89,
            "commandSrc": "app",
            "command": "run"
        },
        "clientId": "101046568"
    },
    "escape": false
```

```JSON
{
    "fn": "smartwater-app-shadow-api-prod-update",
    "parse": false,
    "body": {
        "locale": "en_US",
        "clientId": "101046568",
        "payload": {
            "flowRate": 100,
            "temperature": 25.56,
            "commandSrc": "app",
            "command": "run"
        }
    },
    "escape": false
}
```

```JSON
{
    "parse": false,
    "escape": false,
    "fn": "smartwater-app-shadow-api-prod-update",
    "body": {
        "payload": {
            "flowRate": 100,
            "temperature": 34.44,
            "commandSrc": "app",
            "command": "run"
        },
        "clientId": "101046568",
        "locale": "en_US"
    }
}
```

### Response

```JSON
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST",
    "Payload": "{\"statusCode\":200,\"body\":{\"status\":true}}"
}
```
