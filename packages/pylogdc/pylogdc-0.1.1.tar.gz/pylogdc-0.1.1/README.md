# PyLogDc

PyLogDc je Python balíček, který umožňuje logovat zprávy do Discord serveru pomocí webhooků s podporou barev.
PyLogDc is Python package, you can log actions of your code / alert to your Discord server using webhook. 
You can use color that you want (using HEX code) or use some of prepared colors.
## Prepared colors
Success = #5cb85c
Info = #5bc0de
Warning = #f0ad4e 
Danger = #d9534f

## Install
For install, run this command in your console / powershell

```bash
pip install pylogdc
```

## Usage
```python
from PyLogDc.logthis import log_this
webhookURL = "https://discord.com/api/webhooks/......." # Replace with your actual Discord webhook URL
log_this('Test Header', 'Test message', 'info', webhookURL) # Without footer
log_this('Test Header', 'Test message', 'info', webhookURL, "Test Footer") # With footer
```
Remember to replace webhookURL with your actual Discord webhook URL.
