Output assets/demo/scan.gif

Require lattence

Set Shell "bash"
Set Width 1000
Set Height 600
Set FontSize 16
Set FontFamily "Menlo"
Set LineHeight 1.2
Set Padding 16
Set BorderRadius 2
Set Framerate 15
Set TypingSpeed 40ms
Set CursorBlink false
Set Theme { "background": "#0B0D10", "foreground": "#E6E9EE", "cursor": "#4C8DFF", "black": "#12151A", "red": "#E5484D", "green": "#3E9B4F", "yellow": "#E2A336", "blue": "#4C8DFF", "magenta": "#8A94A6", "cyan": "#6E7A8A", "white": "#E6E9EE", "brightBlack": "#262C35", "brightRed": "#E5484D", "brightGreen": "#3E9B4F", "brightYellow": "#E2A336", "brightBlue": "#4C8DFF", "brightMagenta": "#8A94A6", "brightCyan": "#6E7A8A", "brightWhite": "#E6E9EE" }

Hide
Type "export PS1='$ '"
Enter
Type "cd examples/vulnerable-agent"
Enter
Type "clear"
Enter
Show

Type "lattence scan . --offline --no-color --out /tmp/lattence-demo --fail-on none"
Enter
Sleep 4s
