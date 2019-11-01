FROM nvcr.io/nvidia/tensorflow:19.08-py3

RUN git clone http://github.com/nickwalton/AIDungeon.git
RUN cd AIDungeon

RUN pip install -r requirements.txt
RUN cd generator/ctrl
RUN ./install_ctrl_py3.sh
RUN ./download_model.sh

CMD exec guincorn --bind :%PORT --workers 1 --threads 8 app:app
