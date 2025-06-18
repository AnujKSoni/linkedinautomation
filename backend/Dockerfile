FROM selenium/standalone-chrome:122.0

USER root

WORKDIR /app

# Install Python & dependencies
RUN apt-get update && apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python3", "app.py"]
