# RemotiveLabs - CLI

Use this CLI with our cloud and broker as a compliment to code and web tools.

Read more at https://docs.remotivelabs.com/docs/cloud-cli/Installation

## Cloud and broker API

You can use our CLI against both cloud and broker.

## Cloud

Here summary of what you can do with the cli, for a complete list of cloud features
visit https://docs.remotivelabs.com/docs/category/remotivecloud/

The CLI does not currently support everything but we are working on having them in pair.

* remotive cloud auth
  * Login / Logout
  * Manage personal and service account tokens

* remotive cloud brokers
  * Create broker
  * Delete broker
  * List brokers
  * View broker logs

* remotive cloud licenses 
  * View physical broker licenses for your organisation

* remotive cloud recordings
  * Upload recording
  * Play recording
  * List recordings
  * Download recordings
  * Upload custom configuration (i.e signal transformation)
  * Download custom configurations
  * Delete recordings and configurations

* remotive cloud signal-databases
  * Upload
  * Download
  * Delete

* remotive cloud projects
  * Create
  * Delete
  * List

* remotve cloud service-accounts
  * Create
  * Delete
  * List


### Broker

    remotive cloud auth

## Subscribe to signals

Output from running subscribe against our demo. You can visit https://demoo.remotivelabs.com
to start a broker and subscribe to - from the demo you can copy/paste the exact command to run.

```
remotive broker signals subscribe  \
    --namespace VehicleBus  \
    --signal ID257DIspeed.DI_vehicleSpeed \
    --signal ID129SteeringAngle.SteeringAngle129 \
    --url https://some_url --api-key some-api-key
```

```json
[{"timestamp_us": 1663574225650092, "name": "ID129SteeringAngle.SteeringAngle129", "value": -363.0}, {"timestamp_us": 1663574225650092, 
"name": "ID129SteeringAngle", "value": "0xcb2cd251fe1fff3f"}]
[{"timestamp_us": 1663574225658703, "name": "ID257DIspeed.DI_vehicleSpeed", "value": 7.200000000000003}, {"timestamp_us": 1663574225658703, 
"name": "ID257DIspeed", "value": "0xf3e9240802701201"}]
[{"timestamp_us": 1663574225658708, "name": "ID129SteeringAngle.SteeringAngle129", "value": -363.0}, {"timestamp_us": 1663574225658708, 
"name": "ID129SteeringAngle", "value": "0xd92dd251fe1fff3f"}]
[{"timestamp_us": 1663574225664791, "name": "ID129SteeringAngle.SteeringAngle129", "value": -363.0}, {"timestamp_us": 1663574225664791, 
"name": "ID129SteeringAngle", "value": "0x062ed251fe1fff3f"}]
[{"timestamp_us": 1663574225674805, "name": "ID129SteeringAngle.SteeringAngle129", "value": -363.0}, {"timestamp_us": 1663574225674805, 
"name": "ID129SteeringAngle", "value": "0xf72fd251fe1fff3f"}]
[{"timestamp_us": 1663574225678242, "name": "ID257DIspeed.DI_vehicleSpeed", "value": 7.200000000000003}, {"timestamp_us": 1663574225678242, 
"name": "ID257DIspeed", "value": "0xf4ea240802701201"}]
[{"timestamp_us": 1663574225684858, "name": "ID129SteeringAngle.SteeringAngle129", "value": -363.0}, {"timestamp_us": 1663574225684858, 
"name": "ID129SteeringAngle", "value": "0xbf20d251ff1fff3f"}]
```

## Subscribe with terminal plotting

To just make sure that your signals make sense you can plot them in terminal.

```
remotive broker signals subscribe  \
    --namespace VehicleBus  \
    --signal ID257DIspeed.DI_vehicleSpeed \
    --signal ID129SteeringAngle.SteeringAngle129 \
    --url https://some_url --api-key some-api-key \
    --x-plot --x-plot-size 1000
```

![alt text](cli-plot.png "Cli plotting")
