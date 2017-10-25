# TheIndoorWIFI_location
## **商场中精确定位用户所在店铺**

比赛网址：阿里云天池大赛


## 解决方案:

＃待完成


## 数据说明:

1、商场内店铺的信息数据，这个对训练和评测都是统一的。

2、真实用户在这些商场内的一段时间的到店交易数据，训练和评测将采用不同的时间段。

**Table 1、店铺和商场信息表**

|Field|Type|Description|Note|
|:---|:---:|:---:|:---:|
|shop_id|String|店铺ID|已脱敏|
|category_id|String|店铺类型ID|共40种左右类型，已脱敏|
|longitude|Double|店铺位置－经度|已脱敏，但相对距离依然可信|
|latitude|Double|店铺位置－纬度|已脱敏，但相对距离依然可信|
|price|Bigint|人均消费指数|从人均消费额脱敏而来，越高表示本店的人均消费额越高|
|mall_id|String|店铺所在商场ID|已脱敏|


**Table 2、用户在店铺内交易表**

|Field|Type|Description|Note|
|:---:|:---:|:---:|:---:|
|user_id|String|用户ID|已脱敏|
|shop_id|String|用户所在店铺ID|已脱敏.这里是用户当前所在的店铺，可以做训练的正样本。（此商场的所有其他店铺可以作为训练的负样本）|
|time_stamp|String|行为时间戳|粒度为10分钟级别。例如：2017-08-06 21:20|
|longitude|Double|行为发生时位置-经度|已脱敏，但相对距离依然可信|
|latitude|Double|行为发生时位置-纬度|已脱敏，但相对距离依然可信|
|wifi_infos|String|行为发生时Wifi环境，包括bssid（wifi唯一识别码），signal（强度），flag（是否连接）|例子：b_6396480\|-67\|false;b_41124514\|-86\|false;b_28723327\|-90\|false;解释：以分号隔开的WIFI列表。对每个WIFI数据包含三项：b_6396480是脱敏后的bssid，-67是signal强度，数值越大表示信号越强，false表示当前用户没有连接此WIFI（true表示连接）。|

**Table 3、评测集**

|Field|Type|Description|Note|
|:---:|:---:|:---:|:---:|
|row_id|String|测试数据ID||
|user_id|String|用户ID|已脱敏，并和训练数据保持一致|
|mall_id|String|商场ID|已脱敏，并和训练数据保持一致|
|time_stamp|String|行为时间戳|粒度为10分钟级别。例如：2017-08-06 21:20|
|longitude|Double|行为发生时位置-经度|已脱敏，但相对距离依然可信|
|latitude|Double|行为发生时位置-纬度|已脱敏，但相对距离依然可信|
|wifi_infos|String|行为发生时Wifi环境，包括bssid（wifi唯一识别码），signal（强度），flag（是否连接）|格式和训练数据中wifi_infos格式相同|
