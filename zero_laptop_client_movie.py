import socket
import time
import numpy as np
from sklearn.linear_model import LinearRegression
import nmap
import pickle
import mss
import threading
import json

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
    if len(text_input) == 0:text_input = '1'
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
    stream_positions = {}
    for pi in pies:
        pi.send('map_select'.encode())
        position = input('Select rpi position: ')
        pi.send(position.encode())
        ip, port = pi.getpeername()
        stream_positions[ip] = position
    with open("stream_positions.json", "w") as outfile: 
        outfile.write(json.dumps(stream_positions)) 

def exitt(pies, stream_pies):
    for pi in pies: pi.close()
    for pi in stream_pies: pi.close()
    exit()

def stream(pies):
    for pi in pies: pi.send('stream'.encode())

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
            
def connect_pies(found_pies, port):
    pies = []
    for found_pie in found_pies:
        rpi = socket.socket()
        rpi.connect((found_pie['ip'], port))
        pies.append(rpi)
    return pies

def Color(red, green, blue, white=0):
    """Convert the provided red, green, blue color to a 24-bit color value.
    Each color component should be a value 0-255 where 0 is the lowest intensity
    and 255 is the highest intensity.
    """
    return (white << 24) | (red << 16) | (green << 8) | blue

def stream_thread(stream_pies):
    with open('stream_positions.json', 'r') as openfile:
        stream_positions = json.load(openfile)

    mon = {'top' : 400, 'left' : 930, 'width' : 1330, 'height' : 288}
    sct = mss.mss()
    while True:
        t = time.time()
        img = np.asarray(sct.grab(mon))[::-1,:,:3]#*0.1
        img[:144,:,:] = img[::2,:,:]
        #print(img.shape)

        for pi in stream_pies:
            img_color = []
            for i in range(len(img)):
                ip, port = pi.getpeername()
                x = int(mon['width']/len(stream_pies) * (int(stream_positions[ip])-1))
                img_color.append(Color(int(img[i,x,1]), int(img[i,x,2]), int(img[i,x,0])))

            data = pickle.dumps(img_color)
            pi.send(data)
        for pi in stream_pies: pi.recv(1024).decode()

        #print(int(1/(time.time()-t)), 'fps')

if __name__ == "__main__":
    print('Scanning for pies...')
    found_pies = get_pies_on_network()
    pies = connect_pies(found_pies, 9100)
    stream_pies = connect_pies(found_pies, 9200)
    threading.Thread(target=stream_thread, args=(stream_pies,)).start()

    while True:
        print('---------------')
        print('1 - Start')
        print('2 - Stop')
        print('3 - Pause')
        print('4 - Resume')
        print('5 - Ending')
        print('6 - Mapping')
        print('7 - Stream')
        print('8 - Exit')
        action = input('Select an action to perform: ')

        if action == '1': start(pies)
        if action == '2': stop(pies)
        if action == '3': pause(pies)
        if action == '4': resume(pies)
        if action == '5': ending(pies)
        if action == '6': mapping(pies)
        if action == '7': stream(pies)
        if action == '8': exitt(pies, stream_pies)