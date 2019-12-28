import subprocess
import os, sys, glob, shutil
import argparse

def FFmpeg( add_command ):
    cmd = "ffmpeg " + add_command
    returncode = subprocess.call(cmd, shell=True)
    print(returncode)

def Ffprobe( add_command ):
    cmd = ["ffprobe.exe", add_command]

    res = ""
    p = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    for line in iter(p.stdout.readline,b''):
        res += line.rstrip().decode("utf8") + '\n'

    return res

def Setup( setup_status ):
    global work_directory
    
    if setup_status.args.clean_work:
        shutil.rmtree(work_directory)
    os.makedirs( work_directory, exist_ok=True)

def CleanDirectory( directory ):
    global work_directory

    d = work_directory + '/' + directory
    
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs( d, exist_ok=True)


def DoStep1( target_directory, in_file ):
    global work_directory
    target_directory = work_directory + '/' + target_directory
    tmp = in_file[:in_file.rfind(".")]
    tmp = tmp[tmp.rfind("\\")+1:]
    out_file_wav = '{}/{}.wav'.format(target_directory,tmp)
    out_file_movie = '{}/{}.mp4'.format(target_directory,tmp)
    out_mix_file_movie = '{}/{}_mix.mp4'.format(target_directory,tmp)
    
    FFmpeg( ' -y -i "{}" -vcodec copy -map 0:0 "{}"'.format( in_file, out_file_movie) )   
    FFmpeg( ' -y -i "{}" -ab 192 -af "volume=12dB" "{}"'.format( in_file, out_file_wav) )   
    FFmpeg( ' -y -i "{}" -i "{}" -c:v copy -c:a aac -strict -2 -map 0:v:0 -map 1:a:0 "{}"'.format( out_file_movie, out_file_wav, out_mix_file_movie ) )


def DoStep2( items, out_path ):
    tmp = ""
    for i in items:
        tmp += ' -i "{}" '.format(i)
    FFmpeg( ' -y {} -filter_complex "concat=n={}:v=1:a=1" -strict -2 {}'.format( tmp, len(items), out_path ) )


def DoSetup3(base_movie, bgm, bgm_volume, out_path):
    res = Ffprobe(base_movie)
    lines = res.split('\n')
    time = "0:0"
    for line in lines:
        if line.find("Duration") >= 0 :    
            p1 = line.split(',')[0].split(' ')[3]
            print("Time",p1)
            time = p1

    tmp_bgm = out_path + "_loop.mp3"

    FFmpeg( ' -y -stream_loop -1 -i "{}" -af "volume={}" -t "{}" "{}"'.format(bgm, bgm_volume, time, tmp_bgm) )
        
    FFmpeg( ' -y -i "{}" -i "{}" -filter_complex "[0:1][1:0] amerge=inputs=2" "{}" -t "{}" '.format( base_movie, tmp_bgm, out_path, time ) )


src_materials_directory = "src_materials"
src_movie_directory = "src_movie"
work_directory = "work"

class SetupStatus():

    def __init__(self):
        global src_movie_directory
        global src_materials_directory
        
        p = argparse.ArgumentParser()
        p.add_argument('-s', '--step_do',    default="1 1 1 1", help="実行するステップを指定する")
        p.add_argument('-c', '--clean_work', default=False,     help="一時ディレクトリを削除してから実行する")
        p.add_argument('-e', '--eye_catch',  default="1",       help="アイキャッチの挿入位置")
        p.add_argument('-b', '--bgm_volume', default="0.03",    help="bgmの音量を設定する")
        args = p.parse_args()

        tmp = args.step_do.split(' ')
        step_do = []
        for k in tmp:
            step_do.append(k=='1')

        tmp = args.eye_catch.split(' ')
        eye_catch_insert_pos = []
        for k in tmp:
            eye_catch_insert_pos.append(int(k))

        src_files = glob.glob(src_movie_directory+"/"+"*.mp4")
        src_files.sort()
        
        tmp = []
        tmp2 = []
        for i in range(len(src_files)):
            for j in eye_catch_insert_pos:
                if j==i :
                    if (len(tmp2)>0):
                        #tmp.append(tmp2)
                        tmp.append("conect_movies {}".format(len(tmp2)))
                        tmp.append("eyecatch")
                        tmp2 = []
                        break
                    else:
                        tmp.append("eyecatch")
                        break
            tmp2.append(i)
        if (len(tmp2)>0):
            tmp.append("conect_movies {}".format(len(tmp2)))
            tmp2 = []
        movie_command = tmp

        eye_catch_movies = glob.glob(src_materials_directory+"/eyecatch/"+"*.mp4")
        bgms = glob.glob(src_materials_directory+"/bgm/"+"*.mp3")
        end_movies = glob.glob(src_materials_directory+"/end_movie/"+"*.mp4")

        if len(end_movies) > 0 :
            tmp.append("end_movie")

        self.args                 = args
        self.step_do              = step_do
        self.eye_catch_insert_pos = eye_catch_insert_pos
        self.src_files            = src_files
        self.movie_command        = movie_command

        self.eye_catch_movies     = eye_catch_movies
        self.bgms                 = bgms
        self.end_movies           = end_movies
        
        
setup_status = SetupStatus()

print(vars(setup_status))
Setup(setup_status)

step_counte = -1
step_counte += 1
if setup_status.step_do[step_counte]:
    files = glob.glob(src_movie_directory+"/"+"*.mp4")
    files.sort()
    print(files)

    CleanDirectory("Step1")
    for i in files:
        DoStep1( "Step1", i )

step_counte += 1
if setup_status.step_do[step_counte]:
    
    mix_files = glob.glob(work_directory+"/Step1/"+"*mix.mp4")

    CleanDirectory("Step2")

    target_directory = work_directory + '/' + "Step2"
    use_movie_count = 0
    for i, command in enumerate( setup_status.movie_command ):
        print(command)
        tmp = command.split(' ')
        
        out_path = target_directory+'/'+str(i)+'.mp4'

        if tmp[0] == "eyecatch":
            shutil.copy( setup_status.eye_catch_movies[0], out_path )

        if tmp[0] == "end_movie":
            shutil.copy( setup_status.end_movies[0], out_path )

        if tmp[0] == "conect_movies":
            movie_num = int(tmp[1])
            if movie_num == 1:
                shutil.copy( mix_files[use_movie_count], out_path )
            else :
                tmp_mix_files = []
                DoStep2( mix_files[use_movie_count:use_movie_count+movie_num], out_path)

            use_movie_count += movie_num 


step_counte += 1
if setup_status.step_do[step_counte]:
    src_files = glob.glob(work_directory+"/Step2/"+"*.mp4")
    src_files.sort()

    CleanDirectory("Step3")

    target_directory = work_directory + '/' + "Step3"
    for i, command in enumerate( setup_status.movie_command ):
        print(command)
        tmp = command.split(' ')
        
        out_path = target_directory+'/'+str(i)+'.mp4'

        if tmp[0] == "eyecatch":
            print("e")
            shutil.copy( src_files[i], out_path )

        if tmp[0] == "end_movie":
            shutil.copy( src_files[i], out_path )

        if tmp[0] == "conect_movies":
            movie_num = int(tmp[1])
            print("m",tmp[1], src_files[i])
            DoSetup3( src_files[i], setup_status.bgms[0], setup_status.args.bgm_volume, out_path)

step_counte += 1
if setup_status.step_do[step_counte]:
    src_files = glob.glob(work_directory+"/Step3/"+"*.mp4")
    src_files.sort()

    CleanDirectory("Step4")
    target_directory = work_directory + '/' + "Step4"
    out_conect_file = target_directory + "/out.mp4"
    tmp = ""
    for i in src_files:
        tmp += ' -i "{}" '.format(i)
    FFmpeg( ' -y {} -filter_complex "concat=n={}:v=1:a=1" {}'.format( tmp, len(src_files), out_conect_file ) )

print("End")