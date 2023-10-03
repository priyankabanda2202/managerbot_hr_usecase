#python base image
FROM python:3.9

#set working directory in container
WORKDIR /app

#copy everything in working directory
COPY . /app/

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org -r requirements.txt

#Run Hypercorn with our configuration

EXPOSE 5000

CMD [ "hypercorn","-c","hypercorn_config.py","main:app","&","python","scheduler.py" ]