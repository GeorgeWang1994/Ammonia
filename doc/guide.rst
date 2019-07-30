=======
 guide
=======


基础配置
==============


目前的主要的配置是在创建ammonia对象的时候


默认的参数如下：


.. code-block:: python

    DEFAULT_CONF = {
        "DEBUG": False,
        "TASK_URL": settings.get_task_url(),
        "BACKEND_URL": settings.get_backend_url(),
        "BACKEND_TYPE": "database",
        "TASK_CONNECTION_TIMEOUT": settings.TASK_CONNECTION_TIMEOUT,
        "BACKEND_CONNECTION_TIMEOUT": settings.BACKEND_CONNECTION_TIMEOUT,
    }

..


如果想要自己进行设置相应的参数，


.. code-block:: python

    from ammonia.app import Ammonia

    ammonia = Ammonia(conf={
        "TASK_URL": "",
        "TASK_URL": "amqp://guest:guest@localhost:5672//",
        "BACKEND_URL": "redis://ammonia",
        "BACKEND_TYPE": "database",
        "TASK_CONNECTION_TIMEOUT": 3,
        "BACKEND_CONNECTION_TIMEOUT": 3,
    })

..


本地运行
==============


首先安装Ammonia

pip install Ammonia

目前仅仅支持两个参数，分别是"运行worker的个数"、"项目名称"，使用方法如下：

ammonia -w 2 -p qwe

上面的命令表示起两个worker，项目名称为qwe


docker中运行
==============

后续补充


普通任务
==============

.. code-block:: python

    @ammonia.task()
    def get_abc3(a, b):
        return a + b

..


定时任务
==============


.. code-block:: python

    @ammonia.task(eta=datetime.datetime.now() + datetime.timedelta(seconds=10))
    def get_abc(a, b):
        return a + b


    @ammonia.task(wait=datetime.timedelta(seconds=5))
    def get_abc2(a, b):
        return a + b

..

