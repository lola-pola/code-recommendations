FROM shdowofdeath/genai
WORKDIR /action/
COPY . . 
ENTRYPOINT ["/action/entrypoint.sh"]
