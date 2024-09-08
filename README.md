# serv00-login
serv00.com自动签到，自动延期

# 如何使用
1-fork这个代码库

2-需要添加Action中添加Secrets，名字为SERV_LIST，内容包含登录的账号、密码和web管理地址举例如下：
[
 {"username": "serv00的账号", "password": "serv00的密码", "panel": "panel6.serv00.com"},
 {"username": "ct8的账号", "password": "ct8的密码", "panel": "panel.ct8.pl"}
]

注：
①添加Action Secrets的路径如下：Settings -> Security -> Secrets and variables -> Actions -> New repository secrets
②SERV_LIST支持多个账号

3-（可选）如果需要将结果推送到 微信（serv酱）/Telegram/pushplus需要添加额外的Secrets，具体对应关系列举如下：

| 推送类型 | secret名 | 说明 |  
| :---: | :---: | :---: |  
| 微信（serv酱） | SCKEY | serv酱的key |  
| Telegram | TG_BOT_TOKEN | tg机器人token |  
| Telegram | TG_CHAT_ID | 你的tg chat id |  
| pushplus | PUSHPLUS_TOKEN | pushplus的key |
