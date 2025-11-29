FROM python:3.14-rc
EXPOSE 80
COPY . /app/
WORKDIR /app/
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["/tgbot/bot.py"]
