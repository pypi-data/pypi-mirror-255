import subprocess , threading , os , requests
from urllib.parse import urljoin
from IPython.display import HTML , Javascript 
from google.colab.output import clear
import bashi as b 




def configure(clear = True) : 
    if clear : clear()
    html_code = """
        <button onclick="navigator.clipboard.writeText('{code_to_authenticate}').then(function() {{window.open('https://microsoft.com/devicelogin', '_blank', 'width=500,height=400,scrollbars=yes');}} );" style = " background-color: #1b653f ;  width:100% ; padding : 16px 8px ; height: 75px ; font-size : 20px">Open https://microsoft.com/devicelogin && paste code</button>
    """
    openpath = "https://vscode.dev/tunnel/colab/content"
    vs_code_btn  = f"""
            <button onclick="window.open('{openpath}', '_blank');" style = "color : #dcdcde ;background-color: rgb(31, 117, 203) ;  width:100% ; padding : 16px 8px ; height: 75px ; font-size : 20px">Open VS CODE</button>
    """
    if not os.path.exists("./code") : 
        assert b.bash('''
        curl -Lk 'https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64' --output vscode_cli.tar.gz && tar -xf vscode_cli.tar.gz && rm vscode_cli.tar.gz
        ''').ok
    process = subprocess.Popen("./code tunnel user login --provider microsoft", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    Message = process.stdout.readline()
    code_to_authenticate = [i.strip() for i in Message.strip().split() if i.strip() == i.strip().upper()][0]
    clear()
    display(HTML(html_code.format(code_to_authenticate = code_to_authenticate)))
    process.wait()
    clear()
    threading.Thread(target=lambda  : subprocess.Popen("./code tunnel --accept-server-license-terms   --name colab", shell = True , stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()).start()
    display(HTML(vs_code_btn))


__all__ = ['configure']