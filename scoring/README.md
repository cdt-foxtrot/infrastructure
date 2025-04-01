install:
- python3
- python3-flask
- python3-pymysql
- python3-requests
- git
- MySQL
  
oneliner:
`apt install python3 python3-flask python3-pymysql python3-requests git mysql-server smb-client -y` (and the mysql one)

then:
- clone repo `git clone https://github.com/cdt-foxtrot/infrastructure.git`
- run the scoring sql script
- run the api server
