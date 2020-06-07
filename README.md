# bingdog

bingdog is a framework to simplify complexity of business code, which was written with python 3. It splits procedure into multiple tasks and make them run as a configured workflow. Look into the introduction for more details.

## Quick Start

### Installation

Using pip is the best way to install the framework as a module. Make sure you are using pip for python 3. Please check [dependencies]() before installation.
``` python
pip install bingdog
```

### How to Use

The framework can used in multiple scenarios, like continuous integration, batched data processing, business development and so on. Here are 3 samples for each scenario continuous integration and batched data processing and business development.

There are 4 steps to build a procedure with the framework:
- Making a [workflow definition file]() as json format.
- Making a yaml [configuration file]().
- Writting a [startup python program]() to launch processing.
- Writting customized tasks which is not necessary for all scenarios.

#### Hello World

Making a workflow definition file named "demo.json", which is created under dicretory "/home/test_user". There is no limitations to the file name. The directory can be anywhere the program has right to access.

``` json
{
	"demo":{
		"class_name":"bingdog.task|task.ShellExecutionTask",
		"statement": "echo \"Hello world\""
	}
}
```

Making a yaml configuration file named "demo.yaml", which is also created under directory "/home/test_user". The directory can be anywhere the program has right to access and the file name has no limitations for naming.

``` yaml
application:
    task:
        flow_file_path: /home/test_user/demo.json # The file had created at the first step.
    logger:
        level: debug # Level can be defined with debug, info and warning.
        format: "%(levelname)s:%(asctime)s:%(message)s"
        log_file_path: # Log will be output to console terminal if log file path is left blank.
```

Build a python file to startup named "demo.py", which is also created under directory "/home/test_user". The directory can be anywhere the program has right to access and the file name has no limitations for naming.

``` python
from bingdog.executor import TaskExecutor
from bingdog.appconfig import Configurator
import sys

sys.path.append("/home/test_user") # This is not necessary. It depends on the site-package configuration of your application environment.
Configurator.initialize(Configurator, "/home/test_user/demo.yaml") # This file was created at step 2.
executor = TaskExecutor()
executor.execute("demo") # The task ID of the first task.
```

Run in console terminal.

``` shell
python3 /home/test_user/demo.py
```

#### Senior Demo for batched data processing

##### Scenario background

Build a program to download CSV files and load them into MySQL Database. It is required as 3 steps:
- Downloading CSV files from a specified url.
- Creating tables with prepared initialization scripts.
- Loading data into MySQL Database.

##### Implementation

Here is the workflow definition file below. The others are all same with the previouse sample. You also can download [source code](http://sherocktong.github.io/sample.zip) for all details.

```json
{
	"init_parameters": {
		"class_name": "bingdog.task|task.BlankTask",
		"parameters": {
			"app_dir": "/usr/local/src/sample_batched_data_processing",
			"market_type": "1",
			"start_date": "20200507",
            "end_date": "20200604",
			"code": "000001",
            "temp_dir": "/tmp/",
            "db_name": "bingdog_demo"
    	},
		"next_task": "script_file_init"
	},
    "script_file_init": {
		"class_name": "bingdog.task|task.FileCopyTask",
		"source_file": "$app_dir/record_ddl.sql",
		"dist_file": "$temp_dir/script_$code.sql",
		"write_mode": "w",
		"encoding": "utf-8",
		"next_task": "csv_download"
	},
	"csv_download": {
		"class_name": "bingdog.task|task.ShellExecutionTask",
		"statement": "curl -s \"http://quotes.money.163.com/service/chddata.html?code=$market_type$code&start=$fetch_date&end=$fetch_date&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP\" | iconv -f gbk -t utf-8 > $temp_dir/$code.csv",
		"next_task": "csv_fetch"
	},
	"csv_fetch": {
		"class_name": "bingdog.task|task.BlankTask",
		"dist_file": "$temp_dir/script_$code.sql",
		"source_file": "$temp_dir/$code.csv",
		"sheet_index": "0",
		"sub_task_list": {
			"unit_task": "record_mapping",
			"unit_param_key": "record",
			"handler": "bingdog.taskhandler|taskhandler.CsvReaderTaskHandler"
		},
        "next_task": "script_execution"
	},
    "record_mapping": {
		"data_object": "record",
		"class_name": "bingdog.task|task.FieldMappingTask",
		"content": "record_dict",
		"mapping": {
            "fetch_date": "0",
			"close_price": "3",
			"highest_price": "4",
			"lowest_price": "5",
			"opening_price": "6",
			"last_close_price": "7",
			"change_value": "8",
			"change_percent": "9",
			"turnover_ratio": "10",
			"turnover_amount": "11",
			"turnover_qty": "12",
			"total_cap": "13",
			"cap": "14"
		},
		"next_task": "script_generation"
	},
    "script_generation": {
		"text": "insert into $db_name.daily_record_$fetch_year(code, record_date, change_value, change_percentage, close_price, opening_price, highest_price, lowest_price, last_close_price, turnover_ratio, turnover_amount, turnover_qty, tcap, mcap) values('$code', '$fetch_date', $change_value, $change_percent, $close_price, $opening_price, $highest_price, $lowest_price, $last_close_price, $turnover_ratio, $turnover_amount, $turnover_qty, $total_cap, $cap);\n",
		"bean": "record_dict",
		"class_name": "bingdog.task|task.ContentReplacementTask",
		"content": "record_sql",
		"next_task": "script_write"
	},
    "script_write": {
		"class_name": "bingdog.task|task.FileWriterTask",
		"write_mode": "a",
		"dist_file": "$temp_dir/script_$code.sql",
		"content": "record_sql"
	},
    "script_execution": {
        "class_name": "bingdog.task|task.ShellExecutionTask",
        "statement": "sudo mysql -e \"source $temp_dir/script_$code.sql\""
    }
}
```

## Introduction

bingdog is run by tasks like the diagram below. Each task represent a processing step. The parameters are passed between tasks.

![Task Processing Flow]()

## Task

Tasks are described as a json node in workflow definition file. The json node was combined by Task ID and Json Content.

``` json
"init_parameters": {
	"class_name": "bingdog.task|task.BlankTask",
	"parameters": {
		"app_dir": "/usr/local/src/sample_batched_data_processing",
		"market_type": "1",
		"start_date": "20200507",
		"end_date": "20200604",
		"code": "000001",
		"temp_dir": "/tmp/",
		"db_name": "bingdog_demo"
	},
	"next_task": "script_file_init"
}
```

### Task ID

"init_parameters" is a Task ID. It has to be distinct in a workflow definition file. The ID is prefered to be named with meaningful name. The json content includes properties to define what this task is made of and what the next task is.

#### Basic Properties

|Name|Description|Sample|
|-----|-----|-----|
|class_name|Task Class. The before "\|" is package name. The after "\|" is class name. It can be translated into python as "from ${package name} import ${class name}"|bingdog.task\|task.BlankTask|
|parameters|Add parameters into tasks||
|next_task|The task ID of next task||
|bean|For replacement to parameters||

### Task Class List

#### bingdog.task.BlankTask

Tasks of class BlankTask do nothing. They only are effective to basic properties.

#### ShellExecutionTask

Tasks of class ShellExecutionTask are to execute external system command, such as shell and batch command.

``` json
"csv_download": {
	"class_name": "bingdog.task|task.ShellExecutionTask",
	"statement": "curl -s \"http://quotes.money.163.com/service/chddata.html?code=$market_type$code&start=$fetch_date&end=$fetch_date&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP\" | iconv -f gbk -t utf-8 > $temp_dir/$code.csv"
}
```

|Name|Description|Sample|Optional|
|-----|-----|-----|-----|
|statement|External System Command||False|
|content|Key of Task Parameters to store return value||True|
|container|Key of Task Parameter Container to store return value|True|

#### FileCopyTask

Tasks of class FileCopyTask are to copy files and replace all the place holders in source file.

```json
"script_file_init": {
	"class_name": "bingdog.task|task.FileCopyTask",
	"source_file": "$app_dir/record_ddl.sql",
	"dist_file": "$temp_dir/script_$code.sql",
	"write_mode": "w",
	"encoding": "utf-8"
}
```

|Name|Description|Sample|Optional|
|-----|-----|-----|-----|
|source_file|Source file path||False|
|bean|Key for task parameters for text replacing||True|
|dist_file|Target file path||False|
|write_mode|Writting mode: Append, Overwrite with new one.Default: a|w/a/w+/a+|True|
|encoding|Charset for writting file.Default: utf8|utf8/gbk|True|

#### FileReaderTask

Tasks of class FileReaderTask are to read files into a parameter or container.

```json
"reader": {
	"class_name": "bingdog.task|task.FileReaderTask",
	"source_file": "/home/test_user/sample.txt",
	"container": "task"
}
```

|Name|Description|Sample|Optional|
|-----|-----|-----|-----|
|source_file|Source file path||False|
|content|Parameter key to store source file content||False|
|container|Container key to store source file content||False|

#### FileWriterTask

Tasks of class FileWriterTask are to write files from a parameter or container.

``` json
"writer": {
	"class_name": "bingdog.task|task.FileWriterTask",
	"dist_file": "/home/test_user/sample.txt",
	"content": "task",
	"bean": "item_properties"
}

|Name|Description|Sample|Optional|
|-----|-----|-----|-----|
|dist_file|Target file path||False|
|content|Parameter key to store content to write into target files||False|
|container|Container key to store content to write into target files||False|

#### ContentReplacementTask

Tasks of class ContentReplacementTask are to replace text and set it to a parameter or container.

``` json
"replace": {
	"class_name": "bingdog.task|task.ContentReplacementTask",
	"text": "insert into $db_name.daily_record_$fetch_year(code, record_date, change_value, change_percentage, close_price, opening_price, highest_price, lowest_price, last_close_price, turnover_ratio, turnover_amount, turnover_qty, tcap, mcap) values('$code', '$fetch_date', $change_value, $change_percent, $close_price, $opening_price, $highest_price, $lowest_price, $last_close_price, $turnover_ratio, $turnover_amount, $turnover_qty, $total_cap, $cap);\n",
	"content":"record",
	"bean": "item_properties"
}
```

|Name|Description|Sample|Optional|
|-----|-----|-----|-----|
|text|Text to be replaced||False|
|content|Parameter key to store replacement result||True|
|container|Container key to store replacement result||True|


#### JsonTransferTask

Tasks of class JsonTransferTask are to transfer text into json and load it into a parameter or container.

``` json
"to_json": {
	"class_name": "bingdog.task|task.JsonTransferTask",
	"text": "{\"Hello\": \"World\"}",
	"content": "result"
}
```

|Name|Description|Sample|Optional|
|-----|-----|-----|-----|
|text|Text to be replaced and translated into json||False|
|content|Parameter key to store json result||True|
|container|Container key to store json result||True|

#### ParameterRemoveTask

Tasks of class ParameterRemoveTask are to remove a parameter from task parameter dictionary.

```json
"remove": {
	"class_name": "bingdog.task|task.ParameterRemoveTask",
	"content": "parameter_to_be_removed"
}
```

|Name|Description|Sample|Optional|
|-----|-----|-----|-----|
|text|Text to be replaced and translated into json||False|
|content|Parameter key to store json result||True|
|container|Container key to store json result||True|

#### FieldMappingTask

Tasks of class FieldMappingTask are for mapping fields from one parameter to another.

```json
"record_mapping": {
	"data_object": "stock_record",
	"class_name": "bingdog.task|task.FieldMappingTask",
	"content": "stock_record_dict",
	"mapping": {
		"close_price": "3",
		"highest_price": "4",
		"lowest_price": "5",
		"opening_price": "6",
		"last_close_price": "7",
		"change_value": "8",
		"change_percent": "9",
		"turnover_ratio": "10",
		"turnover_amount": "11",
		"turnover_qty": "12",
		"total_cap": "13",
		"cap": "14"
	}
}
```
|Name|Description|Sample|Optional|
|-----|-----|-----|-----|
|data_object|Parameter key to store data object to be mapped||True|
|content|Parameter key to store data object after mapped||True|
|mapping|Field mapping configuration||True| 

#### ContainerUnpackTask

Tasks of class ContainerUnpackTask are to get parameter from container.

```json
"fetch": {
	"class_name": "bingdog.task|task.ContainerUnpackTask",
	"container": "value",
	"content": "value"
}
```

|Name|Description|Sample|Optional|
|-----|-----|-----|-----|
|container|Container key to store the value to be fetched||True|
|content|Parameter key to store the fetched value||True|

## TaskHandler

Task handlers are used to manage sub tasks for parent tasks. One parent task is only mapped to one task handler. 


``` python
"csv_fetch": {
	"class_name": "bingdog.task|task.BlankTask",
	"dist_file": "$temp_dir/script_$code.sql",
	"source_file": "$temp_dir/$code.csv",
	"sheet_index": "0",
	"sub_task_list": {
		"unit_task": "record_mapping",
		"unit_param_key": "record",
		"handler": "bingdog.taskhandler|taskhandler.CsvReaderTaskHandler"
	}
}
```

|Name|Description|Sample|Optional|
|-----|-----|-----|-----|
|container|Container key to 

Task Handlers of class 

### 