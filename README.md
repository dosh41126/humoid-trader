install docker


### **1 Remove old Docker versions (if any)**

```bash
sudo apt remove docker docker-engine docker.io containerd runc
```

---

### ** Install prerequisites**

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release
```

---

### ** Add Docker’s official GPG key**

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

---

### ** Add the Docker repository**

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

---

### ** Install Docker Engine + CLI + Compose**

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

---

### **  Run Docker without sudo**

```bash
sudo usermod -aG docker $USER
newgrp docker
```



clone
```
https://github.com/dosh41126/humoid-trader
```

build


```
docker build -t humoid-trader .
```

run



```
docker run --rm -it \
  --cap-add=NET_ADMIN \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$HOME/humoid_data:/data" \
  -v "$HOME/humoid_data/nltk_data:/root/nltk_data" \
  -v "$HOME/humoid_data/weaviate:/root/.cache/weaviate-embedded" \
  humoid-trader
```
