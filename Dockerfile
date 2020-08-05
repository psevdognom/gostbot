FROM python:latest
EXPOSE 80
COPY . /app/
WORKDIR /app/
RUN pip install -r requirements.txt
VOLUME ["/app/tgbot/data"]
ENTRYPOINT ["python"]
CMD ["/tgbot/bot.py"]
