FROM nvcr.io/nvidia/tensorflow:19.08-py3

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r requirements.txt
RUN cd generator/ctrl
RUN ls
RUN sh install_ctrl_py3.sh
RUN sh download_model.sh

CMD exec guincorn --bind :%PORT --workers 1 --threads 8 app:app
