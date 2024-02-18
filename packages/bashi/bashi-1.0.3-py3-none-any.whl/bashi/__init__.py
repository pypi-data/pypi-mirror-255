

import os , colorama , subprocess , colorama , collections



def bash(cmd , cwd  = "." , shell = True , text = True , throw = False) : 
    colorama.init()
    print(colorama.Back.GREEN + colorama.Style.BRIGHT + f" $ {cmd}" + " "*10  +  colorama.Style.RESET_ALL , end = "")
    process = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE , text = text)
    stdout, stderr = process.communicate()
    return_code = process.returncode
    if return_code == 0:
        print("\n" + stdout)
    else : 
        print(colorama.Style.BRIGHT + colorama.Fore.RED + f" ==> code {return_code}" +  colorama.Style.RESET_ALL  + colorama.Fore.RED + "\n" + f"{stderr.strip()})" +  colorama.Style.RESET_ALL)
    return collections.namedtuple('ibash', ['code', 'stdout', 'stderr'])(code = return_code ,stdout = stdout , stderr = stderr )

