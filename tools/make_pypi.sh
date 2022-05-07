#!/bin/bash
CUR_DIR=$(cd $(dirname $0)/..;pwd)
cd ${CUR_DIR}

case "$1" in
build)  python setup.py sdist
        python setup.py bdist_wheel
        ;;
upload) read -p "upload to PyPI ? (y/N): " ans
        case "$ans" in
            [yY]*) ;;
            *) exit 1 ;;
        esac
        twine upload dist/*
        ;;
test)   read -p "upload to Test PyPI ? (y/N): " ans
        case "$ans" in
            [yY]*) ;;
            *) exit 1 ;;
        esac
        twine upload -r testpypi dist/*
        ;;
clean)  rm -rf build
        rm -rf dist
        rm -rf etrobo_python.egg-info
        ;;
*)      echo "Usage: make_docks.sh {build|upload|test|clean}"
        exit 2
        ;;
esac
exit 0
