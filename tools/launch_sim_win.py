'''Windows環境でシミュレータを起動するためのスクリプト。
このスクリプトからシミュレータを起動することで、Windows上の（WSL上ではない）プログラムから
シミュレータに対して命令/観測値を送受信することが可能となる。
'''
import os
import pathlib
import subprocess
import time
import urllib.error
import urllib.request


def main() -> None:
    if 'HOMEPATH' not in os.environ:
        raise Exception('Home path is not found.')

    sim_path = pathlib.Path(os.environ['HOMEPATH']) / 'etrobosim'

    if not sim_path.is_dir():
        raise Exception(f'Simulator is not installed: {sim_path}')

    versions = [p.name for p in sim_path.iterdir()]

    if len(versions) == 0:
        raise Exception(f'Simulator is not found: {sim_path}')

    subprocess.Popen([sim_path / max(versions) / 'etrobosim.exe'])

    while True:
        try:
            req = urllib.request.Request('http://127.0.0.1:54000/')
            with urllib.request.urlopen(req) as res:
                pass
            break
        except urllib.error.URLError:
            time.sleep(0.5)
            continue

    data = '{"athrillHost":"127.0.0.1"}'.encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:54000/', data=data)
    with urllib.request.urlopen(req) as res:
        print(res.read().decode('utf-8'))


if __name__ == '__main__':
    main()
