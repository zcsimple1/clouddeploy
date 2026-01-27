# MQTT 配置文件
# OneNET 设备接入配置

# 产品信息
PRODUCT_ID="v6IkuqD6vh"

# Broker 地址
MQTT_HOST="mqtts.heclouds.com"
MQTT_PORT="1883"

# ============================================================================
# 配置组1: 设备 MO 配置
# ============================================================================
MO_CONFIG=(
    "$PRODUCT_ID"                           # 用户名
    "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"  # 密码
    "MO"                                   # Client ID
)

# ============================================================================
# 配置组2: 设备 MO1 配置
# ============================================================================
MO1_CONFIG=(
    "$PRODUCT_ID"                           # 用户名
    "version=2018-10-31&res=products%2Fv6IkuqD6vh%2Fdevices%2FMO&et=1772098636&method=sha1&sign=vzb4PV%2FK%2FvPLSdBd%2FVOVRHrSX44%3D"  # 密码
    "MO1"                                  # Client ID
)
