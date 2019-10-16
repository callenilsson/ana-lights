import socket
import time

def text_time_to_seconds(text_time):
    minutes = int(text_time[: text_time.index(':')])
    text_time = text_time[text_time.index(':')+1 :]
    seconds = int(text_time[: text_time.index(':')])
    milliseconds = int(text_time[text_time.index(':')+1 :])
    return minutes*60 + seconds + milliseconds/100.0

if __name__ == "__main__":
    #rpi1 = socket.socket()
    #rpi2 = socket.socket()
    rpi3 = socket.socket()
    #rpi1.connect(('192.168.0.150', 9090))
    #rpi2.connect(('192.168.0.179', 9090))
    rpi3.connect(('192.168.0.197', 9090))

    print('Enter song or custom timecode to start from:')
    songs = [['Cloudless skies', '0:00:00'],
            ['Pixeldye', '1:03:52'],
            ['Lumiére', '2:20:21'],
            ['Your name in the stars', '3:00:15'],
            ['Regn', '4:23:15'],
            ["You're somewhere", '5:13:10']]
    for i in range(len(songs)):
        print(i+1, '-', songs[i][0], '(' + songs[i][1] + ')')
    text_input = input()
    if text_input.isdigit():
        song = songs[int(text_input)-1]
        song_start = text_time_to_seconds(song[1])
    else:
        song_start = text_time_to_seconds(text_input)

    # Send timecode to RPi's where to start
    #rpi1.send(str(song_start).encode())
    #rpi2.send(str(song_start).encode())
    rpi3.send(str(song_start).encode())

    # Wait for ready responses from RPi's
    #print(rpi1.recv(1024).decode())
    #print(rpi2.recv(1024).decode())
    print(rpi3.recv(1024).decode())

    # Ready
    input('Press enter to start')
    start_time = time.time()
    #rpi1.send(str(start_time).encode())
    #rpi2.send(str(start_time).encode())
    rpi3.send(str(start_time).encode())
