import subprocess
import os
import sys
import glob


cmd_dir = "G:\\user\\setup_windows10\\ffmpeg-20181210-a271025-win64-static\\ffmpeg-20181210-a271025-win64-static\\bin\\"
cmd_exe = cmd_dir + "ffmpeg.exe"

def FFmpeg( add_command ):
    global cmd_exe
    print(add_command)
    cmd = cmd_exe + add_command
    returncode = subprocess.call(cmd, shell=True)
    print(returncode)

def Ffprobe( add_command ):
    global cmd_dir
    cmd = [cmd_dir + "ffprobe.exe", add_command]
    
    res = ""
    p = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    for line in iter(p.stdout.readline,b''):
        res += line.rstrip().decode("utf8") + '\n'

    return res



def Setup():
    global work_directory
    os.makedirs( work_directory, exist_ok=True)

def Do( in_file ):
    global work_directory
    tmp = in_file[:in_file.rfind(".")]
    tmp = tmp[tmp.rfind("\\")+1:]
    out_file_wav = '{}/{}.wav'.format(work_directory,tmp)
    out_file_movie = '{}/{}.mp4'.format(work_directory,tmp)
    out_mix_file_movie = '{}/{}_mix.mp4'.format(work_directory,tmp)
    
    FFmpeg( ' -y -i "{}" -vcodec copy -map 0:0 "{}"'.format( in_file, out_file_movie) )   
    FFmpeg( ' -y -i "{}" -ab 192 -af "volume=12dB" "{}"'.format( in_file, out_file_wav) )   

    FFmpeg( ' -y -i "{}" -i "{}" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 "{}"'.format( out_file_movie, out_file_wav, out_mix_file_movie ) )
    return out_mix_file_movie

def Do2( items ):
    global work_directory
    out_conect_file = '{}/conect.mp4'.format(work_directory)

    tmp = ""
    for i in items:
        tmp += ' -i "{}" '.format(i)
    FFmpeg( ' -y {} -filter_complex "concat=n={}:v=1:a=1" {}'.format( tmp, len(items), out_conect_file ) )

target_directory = "src_movie"
work_directory = "work"
Setup()

args = sys.argv

step_do = [ True, True, True, True ]

for i in args:
    if i.find('step_do:') >= 0:
        j = i.split(':')
        print(j)
        for k in range( 1, len(j) ):
            if j[k]=='1':
                step_do[k-1] = True
            else:
                step_do[k-1] = False

print('step_do:',step_do)

if step_do[0]:
    files = glob.glob(target_directory+"/"+"*.mp4")
    files.sort()
    print(files)

    for i in files:
        Do( i )

if step_do[1]:
    mix_files = glob.glob(work_directory+"/"+"*mix.mp4")

    print(mix_files)
    Do2(mix_files)


if step_do[2]:
    main = '{}/conect.mp4'.format(work_directory)

    res = Ffprobe(main)
    #print(res)
    lines = res.split('\n')
    time = "0:0"
    for line in lines:
        if line.find("Duration") >= 0 :    
            p1 = line.split(',')[0].split(' ')[3]
            print("Time",p1)
            time = p1

    bgm  = 'a.mp3'
    bgm_volume = '0.03'
    out  = 'conect_2.mp4'
    FFmpeg( ' -y -stream_loop -1 -i "a.mp3" -vcodec copy -af "volume={}" -t {} "a2.mp3"'.format(bgm_volume, time) )
    bgm2 = 'a2.mp3'
    FFmpeg( ' -y -i "{}" -i "{}" -filter_complex "[0:1][1:0] amerge=inputs=2" "{}" -t {} '.format( main, bgm2, out, time ) )

if step_do[3]:
    items = [ "conect_2.mp4", "main_02.mp4" ]
    out_conect_file = "conect_3.mp4"
    tmp = ""
    for i in items:
        tmp += ' -i "{}" '.format(i)
    FFmpeg( ' -y {} -filter_complex "concat=n={}:v=1:a=1" {}'.format( tmp, len(items), out_conect_file ) )
