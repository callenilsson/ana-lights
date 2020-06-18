import socket
import time
import numpy as np
from sklearn.linear_model import LinearRegression
import nmap

def text_time_to_seconds(text_time):
    minutes = int(text_time[: text_time.index(':')])
    text_time = text_time[text_time.index(':')+1 :]
    seconds = int(text_time[: text_time.index(':')])
    milliseconds = int(text_time[text_time.index(':')+1 :])
    return minutes*60 + seconds + milliseconds/100.0

def start(pies):
    for pi in pies: pi.send('start'.encode())
    songs = [['Cloudless skies', '0:03:69'],
            ['Pixeldye', '4:19:52'],
            ['Lumiére', '12:22:87'],
            ['Your name in the stars', '19:36:21'],
            ['Regn', '23:08:31'],
            ["You're somewhere", '27:23:13']]
    print('---------------')
    for i in range(len(songs)):
        print(i+1, '-', songs[i][0], '(' + songs[i][1] + ')')
    text_input = input('Enter song or custom timecode to start from: ')
    if text_input.isdigit():
        song = songs[int(text_input)-1]
        song_start = text_time_to_seconds(song[1])
    else:
        song_start = text_time_to_seconds(text_input)
    # Wait for ready responses from RPi's
    for pi in pies:
        pi.recv(1024).decode()
        print('RPI Zero ready to start', pi.getpeername()[0])
    
    # Ready
    times = []
    clicks = 5
    for i in range(clicks):
        input('Press enter to start: ' + str(clicks-i))
        times.append(time.time())
    model = LinearRegression().fit(np.arange(clicks).reshape(-1,1), times)
    start_time = model.predict(clicks-1)[0]

    for pi in pies:
        pi.send(str(start_time).encode())

def stop(pies):
    for pi in pies: pi.send('stop'.encode())

def pause(pies):
    for pi in pies: pi.send('pause'.encode())

def resume(pies):
    for pi in pies: pi.send('resume'.encode())

def ending(pies):
    for pi in pies: pi.send('ending'.encode())

def mapping(pies):
    for pi in pies: pi.send('mapping'.encode())
    for pi in pies:
        pi.send('map_select'.encode())
        position = input('Select rpi position: ')
        pi.send(position.encode())

def exitt(pies):
    for pi in pies: pi.close()
    exit()

def get_pies_on_network():
    nm = nmap.PortScanner()
    nm.scan(hosts='192.168.1.0/24', arguments='-sP')
    host_list = nm.all_hosts()
    found_pies = []
    for host in host_list:
        if not('mac' in nm[host]['addresses']): continue
        mac = nm[host]['addresses']['mac']
        vendor = nm[host]['vendor'][mac]
        if 'raspberry' in vendor.lower():
            found_pies.append({
                'ip': host,
                'mac': mac
            })
    return found_pies
            
def connect_pies(found_pies):
    pies = []
    for found_pie in found_pies:
        rpi = socket.socket()
        rpi.connect((found_pie['ip'], 9091))
        pies.append(rpi)
    return pies

if __name__ == "__main__":
    found_pies = get_pies_on_network()
    pies = connect_pies(found_pies)

    while True:
        print('---------------')
        print('1 - Start')
        print('2 - Stop')
        print('3 - Pause')
        print('4 - Resume')
        print('5 - Ending')
        print('6 - Mapping')
        print('7 - Exit')
        action = input('Select an action to perform: ')

        if action == '1': start(pies)
        if action == '2': stop(pies)
        if action == '3': pause(pies)
        if action == '4': resume(pies)
        if action == '5': ending(pies)
        if action == '6': mapping(pies)
        if action == '7': exitt(pies)