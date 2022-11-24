# Description
This repository is dedicaded to ease plugin integrations for site24x7. It contains a set of plugins that can be used to monitor your infrastructure. and in order to install it you need to write below command into your terminal.

```bash
pip3 install site24x7 --force-reinstall
ls -l /usr/local/lib/python3/dist-packages/site24x7_plugin_helper
```

### Usage
Below lines can be used to integrate your plugin.
```python
import json
from site24x7 import Site24x7_plugin_helper
client = site24x7_plugin_helper.connector.request_client.RequestClient(
    author="TechStyleOS",
    plugin_version="1"
)
content = client.get('https://www.techstylefashiongroup.com/').content
client.__setitem__("content", content[0:20]) # site24x7 only accepts 20 characters
client.set_metric_types()
print(json.dumps(client.dict))
```

### jenkins run command also example input
This bash command is for main.py file, it is dedicated to run the plugin on a jenkins cronjob. It is also an example of how to use.
```bash
if pip3 list | grep -F site24x7; then
    echo "site24x7 is installed"
else
    echo "site24x7 is not installed, installing it right now..."
    pip3 install site24x7
fi

SCRIPT_LOCATION=`python3 -c "import site24x7_plugin_helper;print(site24x7_plugin_helper.__file__.replace('__init__.py', 'main.py'))"`
query="select * from testtable"
this_plugin_name="my_testing_plugin"
python3 $SCRIPT_LOCATION \
    --plugin=$this_plugin_name \
    --query=$query \
    --database="mydb" \
    --server="myserver" \
    --username="myusername" \
    --password="mypassword" \
    # or you can give an environment for everything or some of them ABOVE
    # environment will be picked LAST
    --env="///src/site24x7_plugin_helper/.env"
```

# Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
# License
## [MIT](https://choosealicense.com/licenses/mit/)
# TOOLS AND TECHNOLOGIES
Below is just neccesary tools and technologies to run this project.
### how to fast and secure plugin placing on bash
```bash
PLUGIN_NAME="testplugin"
echo "installing $PLUGIN_NAME"
mkdir /opt/site24x7/monagent/plugins/$PLUGIN_NAME
mv .env /opt/site24x7/monagent/plugins/$PLUGIN_NAME/.env
mv $PLUGIN_NAME.py /opt/site24x7/monagent/plugins/$PLUGIN_NAME/$PLUGIN_NAME.py
```
### how to install site24x7 agent on linux 64bit 
```bash
DEVICE_KEY="XXX" # A long authentication key from site24x7.com
sudo wget https://staticdownloads.site24x7.com/server/Site24x7_Linux_64bit.install
sudo chmod 755 Site24x7_Linux_64bit.install
sudo ./Site24x7_Linux_64bit.install -i -key=$DEVICE_KEY
```
### how to see how many plugin this server has on site24x7.com
```js
await page.goto('https://site24x7.com/plugins/');
await page.evaulate(()=>{
    return document.querySelectorAll(".cursor.ng-scope").length;
}).then(result=>{
    console.log(result);
}).catch(error=>{
    console.log(error);
}).finally(()=>{
    browser.close();
}).then(()=>{
    console.log('done');
});
```
### what is expected query(EXEC) input and expected output?
```js
const rows = database.exec(query); 
console.log(rows);
// [(0, 'key', 'value'), (1, 'dev', 'renas'), ...rows]

const fs = require('fs');
console.log(fs.readFileSync('/tmp/testplugin.cache', 'utf8'))
// {
//     "plugin_version": "2",
//     "heartbeat_required": "true",
//     "CPU": 100,
//     "server": "localhost",
//     "database": "testdb",
//     "driverLocation": "/usr/local/lib/python3.6/dist-packages/pyodbc/drivers/pyodbc.so",
//     "query": "select * from testtable",
//     "thisPluginName": "testplugin",
//     "key": "value",
//     "dev": "renas"
// }
```

### site24x7 agent ignored plugins
```bash
cat /opt/site24x7/monagent/temp/ignored_plugins.txt
```