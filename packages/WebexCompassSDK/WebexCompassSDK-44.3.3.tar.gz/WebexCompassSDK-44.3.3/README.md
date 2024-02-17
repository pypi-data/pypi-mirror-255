# Webex Compass

WebexCompassSDK is a sdk to access Webex Compass platform. Webex Compass is an AI programming assistant that helps developers with troubleshooting and solutions

## Disclaimers
- This SDK is intended for Cisco internal use only, you should uninstall it if you are not Cisco employees
- The API is opt to change in near future without any precaution or notification

## Configuration
You will need configurations below to use Webex Compass:
- client_id
- client_secret
- host address

Please reach your contact for above configuraiton

## Example of Using WebexCompassSDK

To use WebexCompassSDK in your project, follow these steps:

### 1. Install the WebexCompassSDK package:
```
pip install WebexCompassSDK
```

### 2. Import the module into your code:
```python
    import asyncio
    import WebexCompassSDK
```

### 3. Initialize the WebexCompassClient instnace:
```python
    async def _test_start(): 
        client = WebexCompassClient(host_address="<<host-address>>",client_id="<<your-client-id>>",client_secret="your-client-secret")
        await client.start()
        await asyncio.wait_for(client.ready, timeout=100)

    asyncio.run(_test_start())
```

### 4. Fast Anomaly Check:
```python
    report = await client.generate_anomaly_report("<<link>>")
```
The paramerter can local file (current_log.txt, last_run_current_log.txt, or zip file) or a link to control hub or jira.

### 5. Deep Anomaly Analysis
With the fast check result, you can continue to call generate_anomaly_deep_analysis_report for failure details:

```python
    report = await client.generate_anomaly_deep_analysis_report("7159edd516f0b33981d7be140cd114628b902f5866c806fcf3be79f10ac9de47","join meeting","callid-e80f6b25-519f-4ad6-a4ba-6aa4ccff34ff.txt")
```

### 6. Do text classification
Categorize customer input to predined fields in BEMS system.

```python
    input_message = "How do I upgrade an existing plan\n* I invited him to join my meeting room so we could discuss the details of why he's looking to upgrade to an enterprise plan. * Per customer, he's looking to purchase an IP phone, and he was told that it is only available with the enterprise plan. * I advised him that I would forward his concern to our sales team for further assistance. * Submitted isales. * I explained to the customer our process when it comes to endorsements to sales. * Customer understood, and he's allset. * Customer agreed to close the ticket and advised him about the survey."
    report = await copilot.classify_problem_report(input_message)
```
