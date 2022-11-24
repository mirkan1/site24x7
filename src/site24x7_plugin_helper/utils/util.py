FUNCTIONAL_KEYS = 'plugin_version|heartbeat_required|status|units|msg|onchange|display_name|AllAttributeChart'

def guessMetricByType(main_dict, check_dict):
    '''only accepts int, float and str'''
    for i in check_dict:
        if i in FUNCTIONAL_KEYS:
            continue
        if isinstance(check_dict[i], tuple):
            continue
        elif isinstance(check_dict[i], list):
            continue
        elif isinstance(check_dict[i], dict):
            continue
        elif check_dict[i] is None:
            continue
        elif check_dict[i] is bool:
            continue
        try:
            float(check_dict[i])
            main_dict[i] = 'count'
        except ValueError:
            main_dict[i] = 'string'
    return main_dict

def validatePluginData(result:dict):
    '''validation method - This is only for Output validation purpose'''
    mandatory = ['heartbeat_required','plugin_version']
    value = {'heartbeat_required':["true","false",True,False],'status':[0,1]}
    for field in mandatory:
        if field not in result:
            raise Exception(f"{field} is mandatory")
    for field,val in value.items():
        if field in result and result[field] not in val:
            raise Exception(f"{field} can only be in following format:\n{val}")
    try:
        int(result['plugin_version'])
    except ValueError as err:
        raise Exception(f"plugin_version must be an int:\n{value['plugin_version']}") from err
    attributes_list=[]
    for key,value in result.items():
        if key not in FUNCTIONAL_KEYS:
            attributes_list.append(key)
    if len(attributes_list) == 0:
        raise Exception("No attributes found")
    return True
