#NEEDS MAJOR RENOVATIONS, might honestly end up doing this manually

sudo apt-get install gnupg curl

curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

sudo apt update

sudo apt install mongodb-org -y

sudo systemctl enable mongod.service
sudo systemctl start mongod.service

wget https://packages.graylog2.org/repo/packages/graylog-6.1-repository_latest.deb

sudo dpkg -i graylog-6.1-repository_latest.deb
sudo apt update
sudo apt install graylog-datanode -y

sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count = "262144 | sudo tee /etc/sysctl.d/99-graylog-datanode.conf

sudo sed -i "/^password_secret =/s/$/ $(< /dev/urandom tr -dc A-Z-a-z-0-9 | head -c${1:-96})/" /etc/graylog/datanode/datanode.conf

grep password_secret /etc/graylog/datanode/datanode.conf > password_secret.txt

sudo systemctl enable graylog-datanode.service
sudo systemctl start graylog-datanode.service

sudo apt install graylog-server -y

echo "you gotta enter a user password bro"

echo -n "Enter Password: " && head -i </dev/stdin | tr -d '\n' | sha256sum | cut -d" " -f1 > user_password.txt

echo "Enter the following: sudo nano /etc/graylog/server/server.conf, then enter the secret password, user password (root_password sha), timezone (root_timezone "America/New_York", and web server ip (http_bind_address)"

sudo systemctl enable graylog-server.service
sudo systemctl start graylog-server.service

tail -f /var/log/graylog-server/server.log


echo "click that mf link, enter org name, and enter the credentials my boy"
