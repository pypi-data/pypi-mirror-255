def connect_wifi():
    import esp32
    import network
    from time import sleep

    try:
        nvs = esp32.NVS("wifi_creds")
        buf = bytearray(1024)
        size = nvs.get_blob("ssid", buf)
        ssid = buf[:size].decode()
        size = nvs.get_blob("password", buf)
        password = buf[:size].decode()
        size = nvs.get_blob("hostname", buf)
        hostname = buf[:size].decode()
        size = nvs.get_blob("country", buf)
        country = buf[:size].decode()

        print("Connecting WiFi to '{0}'...".format(ssid))

        if country:
            try:
                network.country(country)
            except AttributeError:
                pass

        if hostname:
            try:
                network.hostname(hostname)
            except AttributeError:
                pass

        wifi = network.WLAN(network.STA_IF)
        wifi.active(False)
        wifi.active(True)
        wifi.connect(ssid, password)
        max_wait = 140
        while max_wait and wifi.status() == network.STAT_CONNECTING:
            max_wait -= 1
            sleep(0.1)
        print("Connection status:", wifi.isconnected())
    except:
        print("WiFi secrets are kept in NVM. Please store them there!")

connect_wifi()
