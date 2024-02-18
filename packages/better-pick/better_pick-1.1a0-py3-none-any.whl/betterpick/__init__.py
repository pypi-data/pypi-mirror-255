# Better Pick by ScadeBlock
__version__ = "1.1a"
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
import keyboard,os,time
colorama_init()

# Editable Value 
INDICATOR = ">"
COLOR_INDICATOR = False
MULTISELECT_CHECK = f"(x)"
MULTISELECT_UNCHECK = "( )"
# --------------------



def Pick(pick_title,listc,multiselect=False,highlight_color=Fore.GREEN,popup_animation=False,key={"UP":"w","DOWN":"s","SUBMIT":"enter","MULTISELECT_CHOOSE":"space"}):
    global COLOR_INDICATOR,INDICATOR
    if popup_animation:
        lastspace = ""
    else:
        lastspace = " "

    _prefix_spaceblank = (len(INDICATOR)+1) * " "
    if not COLOR_INDICATOR == False:
        _prefix_indicator = COLOR_INDICATOR + lastspace
    else:
        _prefix_indicator = INDICATOR + lastspace
    select = 0
    if multiselect:
        multiselectc = []
        utype = MULTISELECT_UNCHECK
        ctype = MULTISELECT_CHECK
    else:
        utype = ""
        ctype = ""

    while True:
        if type(pick_title) == str: 
            print(pick_title)
        else:
            pick_title()
        for i in range(0,len(listc)):
            if multiselect:
                if i in multiselectc:
                    cm = ctype
                else:
                    cm = utype
                if i == select:
                    prefix = _prefix_indicator
                    print(prefix + " " + cm + " "  + f"{highlight_color}{listc[i]}{Style.RESET_ALL}")
                else:
                    prefix = _prefix_spaceblank
                    print(prefix + " " + cm + " " + listc[i])
            elif multiselect == False: 
                if i == select:
                    prefix = _prefix_indicator
                    print(prefix + " " + f"{highlight_color}{listc[i]}{Style.RESET_ALL}")
                else:
                    prefix = _prefix_spaceblank
                    print(prefix + " " + listc[i])
        while True:
            if keyboard.is_pressed(key["UP"]):
                if not select == 0:
                    select -= 1
                    break
            elif keyboard.is_pressed(key["DOWN"]):
                if not select == len(listc)-1:
                    select += 1
                    break
            elif keyboard.is_pressed(key["SUBMIT"]):
                if multiselect:
                    return multiselectc
                else:
                    return (listc[select],select)
            elif keyboard.is_pressed(key["MULTISELECT_CHOOSE"]):
                if multiselect:
                    if not select in multiselectc:
                        multiselectc.append(select)
                    else:
                        multiselectc.remove(select)
                    break
        time.sleep(0.1)
        os.system('cls' if os.name == 'nt' else 'clear')