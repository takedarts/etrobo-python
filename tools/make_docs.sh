#!/bin/bash
CUR_DIR=$(cd $(dirname $0)/..;pwd)
BUILD_DIR=${CUR_DIR}/docs_build

case "$1" in
build)  rm -rf ${BUILD_DIR}
        mkdir -p ${BUILD_DIR}/src/etrobo_python
        cp ${CUR_DIR}/etrobo_python/*.py ${BUILD_DIR}/src/etrobo_python/
        sphinx-apidoc -F -o ${BUILD_DIR}/build ${BUILD_DIR}/src
        cat << EOS >> ${BUILD_DIR}/build/conf.py

import os
import sys
sys.path.insert(0, '${BUILD_DIR}/src')

import etrobo_python
project = 'etrobo-python'
copyright = '2022, {}'.format(etrobo_python.__author__)
author = etrobo_python.__author__
release = etrobo_python.__version__

import sphinx_rtd_theme
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon']
EOS
        sed -i -e '/sphinx\-quickstart/d' ${BUILD_DIR}/build/index.rst
        sphinx-build ${BUILD_DIR}/build ${CUR_DIR}/docs
        ;;
clean)  rm -rf ${BUILD_DIR}
        ;;
*)      echo "Usage: make_docks.sh {build|clean}"
        exit 2
        ;;
esac
exit 0
