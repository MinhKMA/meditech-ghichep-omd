# Write A Plugin To Monitor MySQL server in Check_MK

## Chuẩn bị: 

### Mô hình 

 - Gồm có một Check_MK server và một host Agent.
    + Check_MK có IP là 192.168.100.65
    + Host Agent có IP là 192.168.100.59 và đã được cài đặt MySQL server
 - Setup môi trường python3 
 - OS sử dụng : CentOS7

 ### Setup môi trường 

 *Lưu ý*: Tất cả các bước này thực hiện trên Server và Agent. Thực hiện từng command :) 

- Thực hiện với user `root` or `sudo`

    ```sh
    yum -y install https://centos7.iuscommunity.org/ius-release.rpm
    yum -y install python35u
    yum -y install python35u-pip
    yum install python35u-devel -y
    mkdir environments
    cd environments
    python3.5 -m venv minhkma
    source minhkma/bin/activate
    pip3 install pymysql
    ```
### Trên Host Agent:

- Kiểm tra đường dẫn tới thư mục chưa plugin agent

    ```sh
    root@zabbix-server:~# check_mk_agent | head
    <<<check_mk>>>
    Version: 1.4.0p25
    AgentOS: linux
    Hostname: zabbix-server
    AgentDirectory: /etc/check_mk
    DataDirectory: /var/lib/check_mk_agent
    SpoolDirectory: /var/lib/check_mk_agent/spool
    PluginsDirectory: /usr/lib/check_mk_agent/plugins
    LocalDirectory: /usr/lib/check_mk_agent/local
    <<<df>>>
    ```
- Download script:

    `cd /usr/lib/check_mk_agent/plugins`
    ```sh
    vim check_mk_info.py 
    #!/root/environments/minhkma/bin/python3.5

    import pymysql
    import time

    def last(connect):
        cur = connect.cursor()
        cur.execute("select VARIABLE_VALUE from information_schema.GLOBAL_STATUS "
                    "where VARIABLE_NAME = 'COM_SELECT' "
                    "or VARIABLE_NAME = 'COM_INSERT' "
                    "or VARIABLE_NAME = 'QUERIES';")
        result = cur.fetchall()
        select = int(result[0][0])
        insert = int(result[1][0])
        query = int(result[2][0])
        return select, insert, query


    def calculator():
        conn = pymysql.connect(host='127.0.0.1',
                                user='root', passwd='minhkma',
                                db='information_schema')
        last_select, last_insert, last_query = last(conn)
        time.sleep(1)
        now_select, now_insert, now_query = last(conn)
        number_select = now_select - last_select
        number_insert = now_insert - last_insert
        number_query = now_query - last_query
        return number_select, number_insert, number_query


    def main():
        number_select, number_insert, number_query = calculator()
        print('<<<check_mk_info>>>')
        print('Number of insert per second : {0}'.format(number_insert))
        print('Number of select per second : {0}'.format(number_select))
        print('Number of query per second : {0}'.format(number_query))


    if __name__ == '__main__':
        main()
    ```
- Thay đổi user, password, tên database trong script theo thông tin database của bạn.

- Phân quyền 

    `chmod +x check_mk_info.py`

- Kiểm tra output của script:

    ```sh
    root@zabbix-server:/usr/lib/check_mk_agent/plugins# ./check_mk_info.py 
    <<<check_mk_info>>>
    Number of insert per second : 1
    Number of select per second : 0
    Number of query per second : 1
    ```
Như vậy script đã thực hiện thành công 

### Trên Check_MK server:

- Thực hiện với user `root` or `sudo`
    
    `yum install tree wget -y`

- Login vào site `monitoring`

    ```sh
    su monitoring
    cd /opt/omd/sites/monitoring/local/share/check_mk
    ```

- Sử dụng lệnh tree để đặt các scripts vào các thư mục cần thiết:

    ```sh
    OMD[monitoring]:/opt/omd/sites/monitoring/local/share/check_mk$ tree 
    .
    ├── 644
    ├── agents
    │   ├── bakery
    │   ├── plugins
    │   └── special
    ├── alert_handlers
    ├── checkman
    ├── checks
    │   ├── check_mk_info
    │   ├── openstack_info
    │   └── redis_info
    ├── inventory
    ├── mibs
    ├── notifications
    ├── pnp-rraconf
    ├── pnp-templates
    ├── reporting
    │   └── images
    └── web
    ├── htdocs
    │   └── images
    └── plugins
        ├── config
        ├── dashboard
        ├── icons
        ├── metrics
        ├── pages
        ├── perfometer
        │   ├── check_mk_info.py
        │   └── openstack_info.py
        ├── sidebar
        ├── views
        ├── visuals
        └── wato
    ```

- Tôi có 2 script có tên là `check_mk_info` và `check_mk_info.py` được đặt lần lượt ở hai thư mục `checks` và `web/plugins/perfometer` . Trong đó:

    + script `check_mk_info` Là script tiếp nhận output từ agent và phân tích dữ liệu hiển thị lên wato theo mỗi line có cấu trúc key = value được tính là một service
    + script `check_mk_info.py` Là script tiếp nhận dữ liệu return từ `check_mk_info` trả về để hiển thị lên thanh perf-o-metter và graph 

- Download hai script : 

    `wget -O https://raw.githubusercontent.com/MinhKMA/meditech-ghichep-omd/master/tools/plugin_msql/check_mk_info`

    `wget -O  https://raw.githubusercontent.com/MinhKMA/meditech-ghichep-omd/master/tools/plugin_msql/check_mk_info.py`

- Phân quyền 
    ```sh
    OMD[monitoring:/opt/omd/sites/monitoring/local/share/check_mk$ pwd 
    /opt/omd/sites/monitoring/local/share/check_mk
    ```

    ```sh
    chmod +x checks/check_mk_info
    chmod +x web/plugins/perfometer/check_mk_info.py
    ```
- Kiểm tra bằng cách debug 

    `check_mk --debug -nv --checks=check_mk_info zabbix-server`

    ```sh
    OMD[monitoring]:/opt/omd/sites/monitoring/local/share/check_mk$ check_mk --debug -nv --checks=check_mk_info zabbix-server
    Check_mk version 1.2.8p21
    CheckMK info MySQL service: Number of insert per second OK - Number of insert per second :  4 
    CheckMK info MySQL service: Number of query per second OK - Number of query per second :  8 
    CheckMK info MySQL service: Number of select per second OK - Number of select per second :  2 
    OK - Agent version 1.4.0p25, execution time 1.1 sec|execution_time=1.108 user_time=0.400 system_time=0.030 children_user_time=0.000 children_system_time=0.000
    ```

*Lưu ý*: Trước khi sử dụng lệnh debug bạn phải add host nếu host chưa được thêm vào site hoặc discovery service.

### Kết quả: 

<img src="https://i.imgur.com/nxx7Bvk.png"> 

<img src="https://i.imgur.com/0cVmKOr.png">



