import subprocess , threading , os , requests
from urllib.parse import urljoin
from IPython.display import HTML , Javascript 
from google.colab.output import clear as clear_output
import bashi as b 
from google.colab import drive



def configure(clear = True, mount = False  , tab = False ) : 
    if clear : clear_output()
    if mount : drive.mount('/content/drive')
    singletab = "" if tab else ",'width=500,height=400,scrollbars=yes'"
    html_code = """
    <!DOCTYPE html> <html lang="en"> <head> <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>Section with Button</title> <style> body {{margin: 0; padding: 0; font-family: Arial, sans-serif; }} .section {{background-color: #fff; padding: 50px; text-align: center; }} .button {{display: inline-block; padding: 20px 40px; /* Adjust padding to make the button bigger */ font-size: 25px; /* Increase font size */ background-color: #007bff; color: #fff; border: none; border-radius: 5px; cursor: pointer; width: 80%; font-weight: 400; letter-spacing: 2px ; }} </style> </head> <body> <section class="section"> <button onclick="navigator.clipboard.writeText('{code_to_authenticate}').then(function() {{window.open('https://microsoft.com/devicelogin', '_blank', 'width=500,height=400,scrollbars=yes');}} );" class = "button">Open https://microsoft.com/devicelogin and Paste code </button> </section> </body> </html>    """
    openpath = "https://vscode.dev/tunnel/colab/content"
    vs_code_btn  = """
      <!DOCTYPE html> <html lang="en"> <head> <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>Section with Button</title> <style> body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }} .section {{background-color: #fff; padding: 50px; text-align: center; }} .button {{display: inline-block; padding: 20px 40px; /* Adjust padding to make the button bigger */ font-size: 25px; /* Increase font size */ background-color: #007bff; color: #fff; border: none; border-radius: 5px; cursor: pointer; width: 80%; font-weight: 400; letter-spacing: 2px ; }} </style> </head> <body> <section class="section"> <button onclick="window.open('{openpath}', '_blank' {singletab});" class = "button" >Open vs-code .</button> </section> </body> </html>    
    """.format(openpath = openpath)
    if not os.path.exists("./code") : 
        assert b.bash('''
        curl -Lk 'https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64' --output vscode_cli.tar.gz && tar -xf vscode_cli.tar.gz && rm vscode_cli.tar.gz
        ''').ok
    process = subprocess.Popen("./code tunnel user login --provider microsoft", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    Message = process.stdout.readline()
    code_to_authenticate = [i.strip() for i in Message.strip().split() if i.strip() == i.strip().upper()][0]
    clear_output()
    display(HTML(html_code.format(code_to_authenticate = code_to_authenticate)))
    process.wait()
    clear_output()
    threading.Thread(target=lambda  : subprocess.Popen("./code tunnel --accept-server-license-terms   --name colab", shell = True , stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()).start()
    display(HTML(vs_code_btn))


__all__ = ['configure']