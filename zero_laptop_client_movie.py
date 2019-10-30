import socket
import time

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
    # Send timecode to RPi's where to start
    for pi in pies: pi.send(str(song_start).encode())
    # Wait for ready responses from RPi's
    for pi in pies: print(pi.recv(1024).decode())
    # Ready
    input('Press enter to start')
    for pi in pies: pi.send(str(time.time()).encode())

def stop(pies):
    for pi in pies: pi.send('stop'.encode())

def pause(pies):
    for pi in pies: pi.send('pause'.encode())

def resume(pies):
    for pi in pies: pi.send('resume'.encode())

def ending(pies):
    for pi in pies: pi.send('ending'.encode())

def exitt(pies):
    for pi in pies: pi.close()
    exit()

if __name__ == "__main__":
    rpi1 = socket.socket()
    rpi1.connect(('192.168.0.152', 9091))
    pies = [rpi1]
    for pi in pies: pi.send(str(time.time()).encode())
    exitt(pies)

    while True:
        print('---------------')
        print('1 - Start')
        print('2 - Stop')
        print('3 - Pause')
        print('4 - Resume')
        print('5 - Ending')
        print('6 - Exit')
        action = input('Select an action to perform: ')

        if action == '1': start(pies)
        if action == '2': stop(pies)
        if action == '3': pause(pies)
        if action == '4': resume(pies)
        if action == '5': ending(pies)
        if action == '6': exitt(pies)