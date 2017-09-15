from aliyunsdkecs.request.v20140526 import CreateInstanceRequest
from aliyunsdkecs.request.v20140526.DescribeImagesRequest import DescribeImagesRequest
from aliyunsdkecs.request.v20140526.DescribeInstanceTypesRequest import DescribeInstanceTypesRequest
from aliyunsdkcore import client
from app.common.Aliyunsdk import LoadSDK
import json
req = CreateInstanceRequest.CreateInstanceRequest()
req.set_ImageId("m-bp14knyxhkgpfrdzyuhw")
req.set_InstanceType("ecs.n1.small")
req.set_HostName("testbysong")
req.set_Password("Xgtest00!")
req.set_VSwitchId("vsw-23vbycvof")
req.set_InstanceChargeType("PostPaid")
res=LoadSDK(req,"cn-hangzhou")


request.set_ImageId('m-bp14knyxhkgpfrdzyuhw');
request.set_InstanceType('ecs.s2.large');
request.set_SecurityGroupId('sg-bp1fpm1mc6adc0dhfo9t');
request.set_InstanceName('F_project_test');
request.set_HostName('F_project_test');
request.set_Password('1b2iNzxxSY5bn20V');
request.set_VSwitchId('vsw-bp1jvqmzed4jsx20vo51s');
print json.dumps(res,indent=4)
# req = DescribeInstanceTypesRequest()
#
# print json.dumps(res,indent=4)
