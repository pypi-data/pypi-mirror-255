# Oqtant API

The Oqtant API provides everything you need to get started working with QuantumMatter and the Oqtant REST API. For more information regarding the Oqtant REST API refer to our [Oqtant REST API Docs](oqtant_rest_api_docs.md)

## Capabilities

- Access all the functionality of the Oqtant Web App (https://oqtant.infleqtion.com)

  - BARRIER (Barrier Manipulator) jobs
  - BEC (Ultracold Matter) jobs

- Build parameterized (i.e. optimization) experiments using the QuantumMatter class

- Submit and retrieve results

## How Oqtant Works

- Instantiate a QuantumMatterFactory and log in with your Oqtant account

- Create QuantumMatter objects with the QuantumMatterFactory

  - 1D parameter sweeps are supported

- Submit the QuantumMatter to Oqtant to be run on the hardware in a FIFO queue

  - Once submitted a job is created and associated with the QuantumMatter object

- Retrieve the results of the job from Oqtant into the QuantumMatter object

  - These results are available in future python sessions

- Extract, visualize, and analyze the results

## Considerations

- Oqtant cannot interact with jobs that have been deleted

- Job results and limits are restricted to the Oqtant account used to authenticate the QuantumMatterFactory

- All QuantumMatter objects that have been submitted will be processed even if the python session is ended before they complete
