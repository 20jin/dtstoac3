import os
import shutil
import subprocess

def main():
    work_dir = '/mnt/y/encoding/'
    dir_lists = search(work_dir, True)
    print(f"encoding 내 디렉토리 수: {len(dir_lists)}\n")
    for cur_dir in dir_lists:
        print(f"시작: {cur_dir}")
        encoding(cur_dir)
        print(f"끝: {cur_dir}\n\n")


def encoding(cur_dir):
    file_list = os.listdir(cur_dir)
    mkv_files = [file for file in file_list if file.endswith(".mkv")]
    print(f"mkv리스트 : {mkv_files}")
    if len(mkv_files) > 1:
        # TODO : MKV 파일이 여러개일때 처리못함
        print("mkv file 이 두개 이상존재합니다.")
        return
    mkv_full_path = os.path.join(cur_dir, mkv_files[0])
    print(mkv_full_path)
    audio_stream = getAudioStreamList(os.path.join(mkv_full_path))
    print(audio_stream)

    if len(audio_stream) == 1:
        # Done : Audio 스트림이 DTS하나일때
        if 'dts' in audio_stream[0]:
            #처리
            filename, extension = os.path.splitext(mkv_full_path)
            origin_name = filename + '_origin' + extension
            shutil.move(mkv_full_path, origin_name)
            #ffmpeg -i "xxx.mkv" -map 0:0 -map 0:1 -map 0:1 -c:v copy -c:a:0 ac3 -ac 6 -b:a:0 640k -c:a:1 copy xxx.mkv
            ffmpeg_proc = subprocess.Popen(args=[f'ffmpeg -i \"{origin_name}\" -map 0:v -map 0:a -map 0:a -c:v copy -c:a:0 ac3 -ac 6 -b:a:0 640k -c:a:1 copy \"{mkv_full_path}\"'], shell=True)
            ffmpeg_proc.wait(timeout=20*60)
            try:
                if os.path.getsize(origin_name) <= os.path.getsize(mkv_full_path):
                    if os.path.isfile(origin_name):
                        os.remove(origin_name)
                        print(f"{origin_name} 삭제됨")
                    done(cur_dir)
            except os.error:
                print("error in getsize")
        else:
            # Done: Audio 스트림 하나인데 DTS아닐때
            print("dts가 없으므로 완료처리")
            done(cur_dir)
    # TODO : Audio 스트림이 여러개일 경우


def done(arg_dir):
    #move
    if os.path.isdir(arg_dir) and os.path.exists(arg_dir):
        shutil.move(arg_dir, '/mnt/y/영화/')
        print("처리 완료")




def getAudioStreamList(mkv_filename):
    p1 = subprocess.Popen(args=['ffmpeg', '-i', mkv_filename], stderr=subprocess.PIPE,
                          stdout=subprocess.PIPE)
    p2 = subprocess.Popen(args=['grep', 'Stream.*Audio'], stdin=p1.stderr, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    p1.stdout.close()

    out, err = p2.communicate()

    audio_stream = []
    for line in out.decode('utf-8').split('\n'):
        if line.strip().startswith('Stream') and 'Audio:' in line:
            audio_stream.append(line)
    return audio_stream

def search(dirname, is_fullname=False):
    filenames = os.listdir(dirname)
    if is_fullname is True:
        full_filename = []
        for filename in filenames:
            full_filename.append(os.path.join(dirname, filename))
        return full_filename
    else:
        return filenames


main()