# bingdog

bingdog is a framework to simplify complexity of business code, which was written with python 3. It splits procedure into multiple tasks and make them run as a configured workflow. Look into the introduction for more details.

[toc]

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

#### Demo for continuous integration

##### Scenario background
Build a daily build system to validate if there is any unit test error or compilation error.

##### Implementation
Make a workflow definition file named “daily_build.json” for example, which is created under directory “/home/test_user”. The directory can be anywhere the program has right to visit.
```json
{
	“init_parameters”: {
		“class_name”: “bingdog.task|task.BlankTask”,
		“parameters”: {
			“app_dir”: “/usr/local/src/test_app”,
			“src_dir”: “/usr/local/src”
		},
		“next_task”: “mvn_build”
	},
	“clean_project”: {
		“class_name”: “bingdog.task|task.ShellExecutionTask”,
		“statement”: “rm -rf $app_dir”,
		“next_task”: “git_clone”
	},
	“git_clone”: {
		“class_name”: “bingdog.task|task.ShellExecutionTask”,
		“statement”: “sshpass -f /usr/local/etc/github.pwd git clone http://sample_user@github.com/sample_project.git”,
		“next_task”: “mvn_build”
	},
	“mvn_build”: {
		“class_name”: “bingdog.task|task.ShellExecutionTask”,
		“statement”: “cd $app_dir;mvn install”
	}
}
```

Make a yaml configuration file named “daily_build.yaml” for example, which is created under directory “/home/test_user”. The rule of file name and directory is just same with workflow definition file.
``` yaml
application:
    task:
        flow_file_path: /home/test_user/daily_build.json # The file had created at the first step.
    logger:
        level: debug # Level can be defined with debug, info and warning.
        format: "%(levelname)s:%(asctime)s:%(message)s"
        log_file_path: # Log will be output to console terminal if log file path is left blank.
```

Program a python file like this. For example, the file was named as “dailybuild.py” under directory “/home/test_user”. Make sure that python has execution right to it.
``` python
from bingdog.executor import TaskExecutor
from bingdog.appconfig import Configurator
import sys

sys.path.append("/usr/local/src") # This is not necessary. It depends on the site-package configuration of your application environment.
Configurator.initialize(Configurator, "/home/test_user/daily_build.yaml") # This file was created at step 2.
executor = TaskExecutor()
executor.execute("init_parameters") # The task ID of the first task.
```

Run in shell.
``` shell
python3 /home/test_user/dailybuild.py
```

The program is running as the definition of the workflow. If the build failed, an exception will be thrown by Task [ShellExecutionTask](). ShellExecutionTask also can be override to implement customized result processing logic. 

#### Demo for batched data processing

##### Scenario background

Build a program to download CSV files and load them into MySQL Database. It is required as 3 steps:
- Downloading CSV files from a specified url.
- Creating tables with prepared initialization scripts.
- Loading data into MySQL Database.

##### Implementation


Make a workflow definition file named “csv_fetch.json” for example, which is created under directory “/home/test_user”. The directory can be anywhere the program has right to visit.

```json
{
	“init_parameters”: {
		“class_name”: “bingdog.task|task.BlankTask”,
		“parameters”: {
			“app_dir”: “/usr/local/src/test_app”,
			“market_type”: “1”,
			“fetch_date”: “20200507”,
			“code”: “000001”,
          “temp_dir”: “/tmp/”
    	},
		“next_task”: “csv_download”
	},
	"csv_download": {
		"class_name": "bingdog.task|task.ShellExecutionTask",
		"statement": "curl -s \"http://quotes.money.163.com/service/chddata.html?code=$market_type$code&start=$fetch_date&end=$fetch_date&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP\" | iconv -f gbk -t utf-8 > $temp_dir/$code.csv",
		"next_task": "csv_fetch"
	},
	“mvn_build”: {
		“class_name”: “bingdog.task|task.ShellExecutionTask”,
		“statement”: “cd $app_dir;mvn install”
	}
}
```

