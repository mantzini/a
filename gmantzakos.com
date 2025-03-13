[Interface]
PrivateKey = OCQIPpHmx4zYEchCiyNC8t8qw3/6+t2c7G9IDsiAPn4=
Address = 192.168.100.53/32
DNS = 1.1.1.1

[Peer]
PublicKey = hEaXFxGwq/iK19FT1iJygpWvRYBE2w0Ew7sEqyQDVXw=
AllowedIPs = 10.10.10.0/24
AllowedIPs = 172.16.101.0/24
Endpoint = 150.140.195.196:13231
PersistentKeepalive = 25
