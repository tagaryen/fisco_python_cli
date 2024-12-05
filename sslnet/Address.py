from error.Error import exitError

hexChar = {"1":True,"2":True,"3":True,"4":True,"5":True,"6":True,"7":True,"8":True,
           "9":True,"0":True,"a":True,"b":True,"c":True,"d":True,"e":True,"f":True}

def check_address(value):
    if not isinstance(value, str):
        exitError("Value must be string, instead got type {}".format(type(value)))
    
    addrLower = value.lower()
    if addrLower[0] == '0' and addrLower[1] == 'x':
        addrLower = addrLower[2:]
    if len(addrLower) > 40:
        exitError("Invalid addrLower, {}".format(addrLower))
    for c in addrLower :
        if not c in hexChar:
            exitError("Invalid addrLower, {}".format(addrLower))
    
    while len(addrLower) < 40:
        addrLower = "0"+addrLower
    return addrLower