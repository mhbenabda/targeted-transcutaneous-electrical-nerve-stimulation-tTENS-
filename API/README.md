## D188 Controller

| Command   | Parameter |Description                              |
| --------  | ------------ | ---------------------------------------- |
| `Initialise` | None | Must be the first function called to initialise the D188 stack and return an instance reference. |
| `SetChannel` | channel | Set which channel is active: [0-8] with zero equivalent to all channels open. |
| `SetMode` | mode | Set which controll mode is used for the selector: 'OFF', 'USB', '8TTL' or '4TTL' |
| `SetIndicator` | state | Set the LED indicators as activated/disactivated: 'ON' or 'OFF'. |
| `SetDelay` | delay | Set the The Delay/De-bounce setting. delay (float): between 0.1-1000 milliseconds. |
| `PrintState` | None | Print the current content of the D188 STATE. |
| `Close` | None | Close and free all resources associated with the instance reference (apiRef). Called once D188 has been finished with. |