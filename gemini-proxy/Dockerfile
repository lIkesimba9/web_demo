FROM ubuntu:22.04

WORKDIR /app
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y \
    python3.9 python3-pip\
    libgl1-mesa-glx \
    libglib2.0-0 \
    openvpn iproute2 net-tools unzip \
    && rm -rf /var/lib/apt/lists/* 

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /dev/net && \
    mknod /dev/net/tun c 10 200 && \
    chmod 600 /dev/net/tun

RUN echo "HELLO\n"
RUN chmod +x ./start.sh

CMD ["./start.sh"]


