FROM python:3.4.3
ADD . /music_reserves
WORKDIR /music_reserves
RUN pip install -r requirements.txt
CMD python app.py run
