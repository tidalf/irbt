# Endpoint documentation

Mobile apps does the following:

```python
# assoc robot with app (perhaps needed for push notifications)
data = {
    'password':password
}
assoc = requests.post(
    service_url + '/v1/user/associations/robots/%s?app_id=%s'
    % (robotId, appId), auth=auth, json=data)
print (assoc.content.decode('utf-8'))
```
