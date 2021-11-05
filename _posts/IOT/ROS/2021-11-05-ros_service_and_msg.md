---
layout: post
title: "ROS系统的Service和msg"
date: 2021-11-05 17:14:51 +0800
categories: 技术
tags: ROS python C++
---

今年有段时间有些开拓性的项目，设计到机器人相关的知识，当时忙着实现也没有记录，现在公司组织架构调整，项目也凉了。正好有时间记录一下。

不得不说ROS系统的设计还是蛮不错的，各个模块都是解耦的，也不限制语言，可以用python2、python3，也可以用c++。在ROS中模块间的通信调用主要通过Service和msg来进行。
Service与我们服务端的rpc方法远程调用类似，而msg与MQ类似。

# Service

Service需要srv来定义数据类型，以我之前写的获取录音的服务为例

在模块(xf_mic_asr_offline)下创建`srv/Get_Record_Pcm_srv.srv`

```
int8 time_out
---
char[] record_pcm_buf
```
> --- 前面是输入(Request)，后面是输出(Response)

然后需要在`CMakeLists.txt`文件中添加我们的srv文件

```cmake
add_service_files(
  FILES
  ...
  Get_Record_Pcm_srv.srv
)

```

服务函数

```C++
/*
获取录音音频
*/
bool Get_Record_Pcm(xf_mic_asr_offline::Get_Record_Pcm_srv::Request &req, xf_mic_asr_offline::Get_Record_Pcm_srv::Response &res)
{

	record_pcm_buf.clear();
	int ret1 = start_to_record_denoised_sound();
	ROS_INFO("start_to_record_denoised_sound %d\n", ret1);
	sleep(req.time_out);
	int ret2 = finish_to_record_denoised_sound();
	ROS_INFO("finish_to_record_denoised_sound %d\n", ret2);
	xf_mic_asr_offline::Pcm_Msg pcm_data;
	vector<char>::iterator it;
	for (it = record_pcm_buf.begin(); it != record_pcm_buf.end(); it++)
	{
		res.record_pcm_buf.push_back(*it);
	}
	record_pcm_buf.clear();
	return true;
}
```

然后需要使用`catkin_make`来编译一下

其他模块中调用

```python
import rospy
from xf_mic_asr_offline.srv import Get_Record_Pcm_srv


get_record_pcm_service = rospy.ServiceProxy('/xf_asr_offline_node/get_record_pcm_srv', Get_Record_Pcm_srv)
record_pcm_rep = get_record_pcm_service(5)
print(record_pcm_rep.record_pcm_buf)
```

我的例子是C++写的Service，python来调用的(Client)。python和C++都可以实现Service和Client的，具体参考官方文档：

* http://wiki.ros.org/ROS/Tutorials/WritingServiceClient%28c%2B%2B%29
* http://wiki.ros.org/ROS/Tutorials/WritingServiceClient%28python%29

关于srv的详细官方文档：

* http://wiki.ros.org/ROS/Tutorials/CreatingMsgAndSrv#Creating_a_srv


# msg

和msg相关的是Publisher和Subscriber。同样以我之前写的录音相关的消息为例

首先同样在模块(xf_mic_asr_offline)下创建`msg/Pcm_Msg.msg`

```
int32 length
char[] pcm_buf
```

`CMakeLists.txt`文件中添加我们的srv文件

```cmake
add_service_files(
  FILES
  ...
  Get_Record_Pcm_srv.srv
)

```

生产者

```c++

ros::Publisher pub_pcm;

...
    pub_pcm.publish(pcm_data);
...

int main(int argc, char *argv[])
{
	ros::init(argc, argv, "xf_asr_offline_node");
	ros::NodeHandle ndHandle("~");
	pub_pcm = ndHandle.advertise<xf_mic_asr_offline::Pcm_Msg>(pcm_topic, 1);
```


消费者

```python
from xf_mic_asr_offline.msg import Pcm_Msg


def pcm_deno_callback(msg):
    print(msg)


rospy.Subscriber('/mic/pcm/deno', Pcm_Msg, pcm_deno_callback)
```


Publisher和Subscriber官方文档(python和C++都可以实现)：

* http://wiki.ros.org/ROS/Tutorials/WritingPublisherSubscriber%28c%2B%2B%29
* http://wiki.ros.org/ROS/Tutorials/WritingPublisherSubscriber%28python%29

msg官方文档：

* http://wiki.ros.org/ROS/Tutorials/CreatingMsgAndSrv#Using_msg
