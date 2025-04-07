Prior to doing the initial login:</br>
run: echo -n "admin" | sha256sum | awk '{print $1}'</br>
edit: /etc/graylog/server/server.conf and set root_password_sha2 = output of run above</br>
get init setup:sudo tail -f /var/log/graylog-server/server.log</br>
login using: admin admin</br>
</br>USE THIS FOR REFERENCE TO INSTALL CLIENTS:</br>
https://go2docs.graylog.org/current/getting_in_log_data/install_sidecar_on_linux.htm#aanchor38
