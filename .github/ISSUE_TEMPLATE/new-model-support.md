---
name: New Model Support Request
about: Request support for a new Moen Smart Water Network faucet model
title: "[NEW MODEL] Model Name - Model Number"
labels: enhancement, new-model
assignees: ''
---

## Faucet Information

**Model Name:**
**Model Number:**
**Product Family:** (e.g., MotionSense Wave, U by Moen, etc.)

## Testing Status

- [ ] I have this faucet model
- [ ] I can test the integration with this model
- [ ] I have a Moen account with this faucet registered
- [ ] The faucet is connected to my network
- [ ] The official Moen app can control this faucet

## Additional Information

**Faucet Features:**
- [ ] MotionSense activation
- [ ] Voice control
- [ ] Preset volume dispensing
- [ ] Custom volume control
- [ ] Other: ________________

**API Compatibility:**
- [ ] I can access the faucet via the Moen mobile app
- [ ] I can see the faucet in my Moen account
- [ ] I can control dispensing from the app

## Test Results (if applicable)

If you've already tested the integration with this model, please provide:

**Integration Status:**
- [ ] Works perfectly
- [ ] Partially works (describe issues below)
- [ ] Doesn't work (describe errors below)

**Issues Encountered:**
```
Describe any problems or limitations you found
```

**Logs:**
```
Paste relevant Home Assistant logs here (remove any sensitive information)
```

> [!IMPORTANT]
> **If the integration doesn't work with your model:**
> We may need to perform packet capture analysis to understand the API differences. This involves:
> 1. Using a network monitoring tool (like mitmproxy or Wireshark)
> 2. Capturing traffic from the official Moen mobile app
> 3. Analyzing the API calls to identify differences from the tested model
>
> If packet capture is needed, we'll provide detailed instructions for safely capturing and sharing the network traffic (with sensitive data removed).

## Additional Notes

Any other information that might be helpful for adding support for this model.
