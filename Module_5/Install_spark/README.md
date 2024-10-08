# Spark Installation (window)
## Windows

Here we'll show you how to install Spark 3.3.2 for Windows.
We tested it on Windows 10 and 11 Home edition, but it should work
for other versions distros as well

In this tutorial, we'll use [MINGW](https://www.mingw-w64.org/)/[Gitbash](https://gitforwindows.org/) for command line

If you use WSL, follow the instructions from [linux.md](linux.md) 


### Installing Java

Spark needs Java 11. 
[Link]https://adoptopenjdk.net/index.html
Select “Windows x64 Compressed Archive” 

Unpack it to a folder with no space in the path. We use `C:/tools` - so the full path to JDK is `/c/tools/jdk-11.0.13`
!!! Replace with vour jdk version

Now let’s configure it and add it to `PATH`:

```bash
export JAVA_HOME="/c/tools/jdk-11.0.13"
export PATH="${JAVA_HOME}/bin:${PATH}"
```

Check that Java works correctly:

```bash
java --version
```

Output:

```
java 11.0.13 2021-10-19 LTS
Java(TM) SE Runtime Environment 18.9 (build 11.0.13+10-LTS-370)
Java HotSpot(TM) 64-Bit Server VM 18.9 (build 11.0.13+10-LTS-370, mixed mode)
```

### Hadoop

Next, we need to have Hadoop binaries. 

We'll need Hadoop 3.2 which we'll get from [here](https://github.com/cdarlint/winutils/tree/master/hadoop-3.2.0).

Create a folder (`/c/tools/hadoop-3.2.0`) and put the files there 

```bash
HADOOP_VERSION="3.2.0"
PREFIX="https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-${HADOOP_VERSION}/bin/"

FILES="hadoop.dll hadoop.exp hadoop.lib hadoop.pdb libwinutils.lib winutils.exe winutils.pdb"

for FILE in ${FILES}; do
  wget "${PREFIX}/${FILE}"
done
```

If you don't have wget, you can use curl:

```bash
HADOOP_VERSION="3.2.0"
PREFIX="https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-${HADOOP_VERSION}/bin/"

FILES="hadoop.dll hadoop.exp hadoop.lib hadoop.pdb libwinutils.lib winutils.exe winutils.pdb"

for FILE in ${FILES}; do
  curl -o "${FILE}" "${PREFIX}/${FILE}";
done
```

Add it to `PATH`:

```bash
export HADOOP_HOME="/c/tools/hadoop-3.2.0"
export PATH="${HADOOP_HOME}/bin:${PATH}"
```

### Spark

Now download Spark. Select version 3.3.2 

```bash
wget https://archive.apache.org/dist/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz
```


Unpack it in some location without spaces, e.g. `c:/tools/`: 

```bash
tar xzfv spark-3.3.2-bin-hadoop3.tgz
```

Let's also add it to `PATH`:

```bash
export SPARK_HOME="/c/tools/spark-3.3.2-bin-hadoop3"
export PATH="${SPARK_HOME}/bin:${PATH}"
```

### Testing it

Go to this directory

```bash
cd spark-3.3.2-bin-hadoop3
```

And run spark-shell:

```bash
./bin/spark-shell.cmd
```

At this point you may get a message from windows firewall — allow it.


There could be some warnings (like this):

```
WARNING: An illegal reflective access operation has occurred
WARNING: Illegal reflective access by org.apache.spark.unsafe.Platform (file:/C:/tools/spark-3.3.2-bin-hadoop3/jars/spark-unsafe_2.12-3.3.2.jar) to constructor java.nio.DirectByteBuffer(long,int)
WARNING: Please consider reporting this to the maintainers of org.apache.spark.unsafe.Platform
WARNING: Use --illegal-access=warn to enable warnings of further illegal reflective access operations
WARNING: All illegal access operations will be denied in a future release
```

You can safely ignore them.

Now let's run this:

```
val data = 1 to 10000
val distData = sc.parallelize(data)
distData.filter(_ < 10).collect()
```

### PySpark

It's the same for all platforms.

This document assumes you already have python.

To run PySpark, we first need to add it to `PYTHONPATH`:

```bash
export PYTHONPATH="${SPARK_HOME}/python/:$PYTHONPATH"
export PYTHONPATH="${SPARK_HOME}/python/lib/py4j-0.10.9-src.zip:$PYTHONPATH"
```

Make sure that the version under `${SPARK_HOME}/python/lib/` matches the filename of py4j or you will
encounter `ModuleNotFoundError: No module named 'py4j'` while executing `import pyspark`.

For example, if the file under `${SPARK_HOME}/python/lib/` is `py4j-0.10.9.3-src.zip`, then the
`export PYTHONPATH` statement above should be changed to

```bash
export PYTHONPATH="${SPARK_HOME}/python/lib/py4j-0.10.9.3-src.zip:$PYTHONPATH"
```

On Windows, you may have to do path conversion from unix-style to windowns-style:

```bash
SPARK_WIN=`cygpath -w ${SPARK_HOME}`

export PYTHONPATH="${SPARK_WIN}\\python\\"
export PYTHONPATH="${SPARK_WIN}\\python\\lib\\py4j-0.10.9-src.zip;$PYTHONPATH"
```

Now you can run Jupyter or IPython to test if things work. Go to some other directory, e.g. `~/tmp`.

Download a CSV file that we'll use for testing:

```bash
wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv
```

or [Link](https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/misc)

Now let's run `ipython` (or `jupyter notebook`) and execute:

```python
import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()

df = spark.read \
    .option("header", "true") \
    .csv('taxi+_zone_lookup.csv')

df.show()
```

Test that writing works as well:

```python
df.write.parquet('zones')
```