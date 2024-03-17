# Robot DSL 语法规范

[toc]

## 1.注释

Robot DSL 采用单行注释，以“#”开头

```
# 这是一条注释
```



## 2.变量

### 2.1 变量的声明与定义

变量无需声明，格式为：$变量名。

变量名可以由数字(0-9)，字母(a-z,A-Z) 以及下划线 (_) 构成，首字母必须为字母或下划线。

```
speak $name
```

### 2.2 变量的前缀

变量名可以有前缀，表示查询数据字典时的递进关系。

```
speak "您的余额为：" + $order.answer.logistics + "元"
```

### 2.3 特殊的变量

$answer: 用户最近输入

$user_id: 用户ID



## 3.常量

### 3.1 字符串

字符串用双引号标识，字符串之间、字符串和变量之间、变量和变量之间都可以通过 “+” 拼接。

```
speak "您的物流状态为：" + $order.answer.state + ",物流：" + $order.answer.logistics
```

### 3.2 数字

数字可以直接表示，暂时只支持整型。

```
listen 20
```



## 4.指令

### 4.1 speak

客服机器人向用户发送消息的指令。

用法：speak <表达式>

（表达式由字符串和变量表示）

```
speak "用户：" + $name + "，客服机器人为您服务！有什么可以帮到您的呢？"
```

### 4.2 listen

等待用户输入的指令。

用法：listen <等待时间>

```
listen 30
```

### 4.3 branch

根据用户输入进行分支判断，与keyword（通常为不带双引号的字符串）匹配后进入相应过程的指令。

branch与listen搭配使用，通常几个branch一起出现，表示多个分支。

用法：branch \<keyword> \<state>

```
branch 话费查询 Cost
branch 话费充值 Charge
branch 本月账单 Bill
branch 结束服务 Exit
branch #silence Silence
branch #other Default
```

特殊的keyword:

#silence: listen等待用户输入超时

#other: 用户输入与其他keyword不匹配，必须放在最后一个branch

### 4.4 goto

过程转移的指令。

用法：goto \<state>

```
goto Service
```

### 4.5 exit

退出对话的指令，后面不加任何参数。

```
exit
```



## 5.过程

过程用state标识，过程名由字母和下划线组成，通常首字母大写。



### 5.1 过程的定义

过程中可以定义多条指令，指令顺序执行，必须以end结尾。

```
state Service
    speak "请输入您需要的服务："
    listen 30
    branch 话费查询 Cost
    branch 话费充值 Charge
    branch 本月账单 Bill
    branch 结束服务 Exit
    branch #silence Silence
    branch #other Default
end
```

### 5.2 过程的声明

过程必须在脚本文件开头集体声明。

```
states
    Welcome
    Service
    Search
    Deposit
    Withdraw
    Silence
    Default
    Exit
end
```



## 6.脚本

### 6.1 脚本文件类型

脚本采用文本文件 (.txt) 编写。

### 6.2 脚本文件的组织

一个脚本由过程声明和过程定义组成，定义了一个客服机器人的应答逻辑。

过程声明必须放在脚本文件开头，声明的第一个过程为程序的入口过程。

过程定义可以不对于声明中的顺序。

例1.online_shop_robot.txt

```
states
    Welcome
    Service
    Refund
    Complain
    Search
    Consign
    Silence
    Default
    Exit
end

state Welcome
    speak "用户：" + $name + "，客服机器人为您服务！有什么可以帮到您的呢？"
    goto Service
end

state Service
    speak "请输入您需要的服务："
    listen 30
    branch 退换货 Refund
    branch 投诉 Complain
    branch 物流查询 Search
    branch 催发货 Consign
    branch 结束服务 Exit
    branch #silence Silence
    branch #other Default
end

state Refund
    speak "请输入订单号："
    listen 20
    speak "您已成功退换货。"
    goto Service
end

state Complain
    speak "您的意见是我们改进工作的动力"
    listen 20
    speak "我们后续会对您的建议进行处理，谢谢！"
    goto Service
end

state Search
    speak "请输入订单号："
    listen 30
    speak "您的物流状态为：" + $order.answer.state + ",物流：" + $order.answer.logistics
    goto Service
end

state Consign
    speak "请输入订单号："
    listen 30
    speak "已经催促店家发货啦，请耐心等待！"
    goto Service
end

state Silence
    speak "听不清，请您大声一点可以吗？"
    goto Service
end

state Default
    speak "对不起，我不理解您的意思。"
    goto Service
end

state Exit
    speak "本次服务结束，期待您的五星好评！"
    exit
end
```

例2. tele_robot.txt

```
states
    Welcome
    Service
    Cost
    Charge
    Bill
    Silence
    Default
    Exit
end

state Welcome
    speak "用户：" + $name + "，客服机器人为您服务！有什么可以帮到您的呢？"
    goto Service
end

state Service
    speak "请输入您需要的服务："
    listen 30
    branch 话费查询 Cost
    branch 话费充值 Charge
    branch 本月账单 Bill
    branch 结束服务 Exit
    branch #silence Silence
    branch #other Default
end

state Cost
    speak "您的话费余额为:" + $money + "元"
    goto Service
end

state Charge
    speak "请输入充值金额："
    listen 20
    speak "充值成功！"
    goto Service
end

state Bill
    speak "您本月已花费:" + $month_cost + "元"
    goto Service
end

state Silence
    speak "听不清，请您大声一点可以吗？"
    goto Service
end

state Default
    speak "对不起，我不理解您的意思。"
    goto Service
end

state Exit
    speak "本次服务结束，期待您的五星好评！"
    exit
end
```

例3. bank_robot.txt

```
states
    Welcome
    Service
    Search
    Deposit
    Withdraw
    Silence
    Default
    Exit
end

state Welcome
    speak "用户：" + $name + "，客服机器人为您服务！有什么可以帮到您的呢？"
    goto Service
end

state Service
    speak "请输入您需要的服务："
    listen 30
    branch 余额查询 Search
    branch 存款 Deposit
    branch 取款 Withdraw
    branch 结束服务 Exit
    branch #silence Silence
    branch #other Default
end

state Search
    speak "您的银行卡余额为：" + $money + "元"
    goto Service
end

state Deposit
    speak "请输入存款金额："
    listen 20
    speak "存款成功！"
    goto Service
end

state Withdraw
    speak "请输入取款金额："
    listen 20
    speak "取款成功！"
    goto Service
end

state Silence
    speak "听不清，请您大声一点可以吗？"
    goto Service
end

state Default
    speak "对不起，我不理解您的意思。"
    goto Service
end

state Exit
    speak "本次服务结束，期待您的五星好评！"
    exit
end
```

