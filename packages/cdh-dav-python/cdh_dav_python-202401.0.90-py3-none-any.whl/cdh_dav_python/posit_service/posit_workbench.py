import os
import subprocess
from cdh_dav_python.cdc_admin_service.environment_logging import LoggerSingleton

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class PositWorkbench:
    @staticmethod
    def install_python_system_components():
        script = """
        cd ~  && \
        INSTALL_DIR="$$HOME/.local"  && \
        wget https://www.sqlite.org/2023/sqlite-autoconf-3420000.tar.gz && \
        tar -xf sqlite-autoconf-3420000.tar.gz && \
        cd sqlite-autoconf-3420000 && \
        gcc  -c -fPIC sqlite3.c -o sqlite3.o  && \
        ar rcs libsqlite3.a sqlite3.o && \
        gcc -shared -o libsqlite3.so sqlite3.o && \
        mkdir -p $$HOME/.local/bin && \
        mkdir -p $$HOME/.local/bin/sqlite-autoconf-3420000 && \
        mv ~/sqlite-autoconf-3420000/libsqlite3.so $$HOME/.local/bin/sqlite-autoconf-3420000/libsqlite3.so && \
        mv ~/sqlite-autoconf-3420000/sqlite3.o $$HOME/.local/bin/sqlite-autoconf-3420000/sqlite3.o && \
        export LD_LIBRARY_PATH=$$HOME/.local/bin/sqlite-autoconf-3420000:$$LD_LIBRARY_PATH   && \
        wget https://www.python.org/ftp/python/3.9.9/Python-3.9.9.tar.xz  && \
        tar -xvf Python-3.9.9.tar.xz  && \
        cd Python-3.9.9 && \
        ./configure --prefix=$$INSTALL_DIR && \
        make  && \
        make altinstall  && \
        echo "export PATH=\"$$INSTALL_DIR/bin:\$$PATH\"" >> ~/.bashrc  && \
        source ~/.bashrc  && \
        python3.9 --version
        """
        try:
            subprocess.run(script, check=True, shell=True, text=True)
        except subprocess.CalledProcessError as e:
            print("An error occurred:", e)
