FROM shdowofdeath/genai
WORKDIR /action/
COPY . . 
## RUN pip3 install -r requirements.txt
ENTRYPOINT ["/action/entrypoint.sh"]
