# vs-colabi



## Getting started

a library allow to use vs code tunnel in google colab 
## Installation

```bash
pip install vs-colabi
```

## Example

```python
from vscolabi import configure

configure()
# configure(clear = True, mount = False  , tab = False ) : 
#   clear : True to clear the colab output 
#   mount : True to mount google drive 
#   tab   : True to open vscode in new tab 

```

Steps  : 
*   a button will be display it --> click .
*   this button once is clicked will show pop frame , paste the code inside input , (code is copy the code to clipboard automaitcly ).
*   after contunue the steps in the pop up , it will display a buttons with text open vscode 