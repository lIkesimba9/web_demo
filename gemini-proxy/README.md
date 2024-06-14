docker build  -t gemini_proxy .
docker run --name gemini_proxy --privileged  --device /dev/net/tun --network custom_network -p 8005:8005  --volume ./config:/config gimini_proxy
