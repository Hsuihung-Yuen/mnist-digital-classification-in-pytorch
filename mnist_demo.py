import torch
# 组建DataLoader
from torchvision import transforms
# 图像
from torchvision import datasets
from torch.utils.data import DataLoader
# 激活函数和优化器
import torch.nn.functional as F
import torch.optim as optim

# Dataset&Dataloader必备
batch_size = 64
# pillow（PIL）读的原图像格式为W*H*C，原值较大
# 转为格式为C*W*H值为0-1的Tensor
transform = transforms.Compose([
    # 变为格式为C*W*H的Tensor
    transforms.ToTensor(),
    # 第一个是均值，第二个是标准差，变值为0-1
    transforms.Normalize((0.1307, ), (0.3081, ))
])

train_dataset = datasets.MNIST(root='./dataset/mnist/',
                               train=True,
                               download=True,
                               transform=transform)

train_loader = DataLoader(train_dataset, shuffle=True, batch_size=batch_size)

test_dataset = datasets.MNIST(root='./dataset/mnist/',
                              train=False,
                              download=True,
                              transform=transform)
test_loader = DataLoader(test_dataset, shuffle=False, batch_size=batch_size)


class Net(torch.nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # 线性层1，input784维 output512维
        self.l1 = torch.nn.Linear(784, 512)
        # 线性层2，input512维 output256维
        self.l2 = torch.nn.Linear(512, 256)
        # 线性层3，input256维 output128维
        self.l3 = torch.nn.Linear(256, 128)
        # 线性层4，input128维 output64维
        self.l4 = torch.nn.Linear(128, 64)
        # 线性层5，input64维 output10维
        self.l5 = torch.nn.Linear(64, 10)

    def forward(self, x):
        # 改变张量形状view\reshape
        # view 只能用于内存中连续存储的Tensor，transpose\permute之后的不能用
        # 变为二阶张量（矩阵），-1用于计算填充batch_size
        x = x.view(-1, 784)
        # relu 激活函数
        x = F.relu(self.l1(x))
        x = F.relu(self.l2(x))
        x = F.relu(self.l3(x))
        x = F.relu(self.l4(x))
        # 第五层不再进行relu激活
        return self.l5(x)

# cnn version
# class Net(torch.nn.Module):
#     def __init__(self):
#         super(Net, self).__init__()
#         self.conv1 = torch.nn.Conv2d(1, 10, kernel_size=5)
#         self.conv2 = torch.nn.Conv2d(10, 20, kernel_size=5)
#         self.pooling = torch.nn.MaxPool2d(2)
#         self.fc = torch.nn.Linear(320, 10)
#
#     def forward(self, x):
#         #flatten data from (n, 1, 28, 28) to (n, 784)
#         batch_size = x.size(0)
#         x = self.pooling(F.relu(self.conv1(x)))
#         x = self.pooling(F.relu(self.conv2(x)))
#         x = x.view(batch_size, -1)
#         x = self.fc(x)
#         return x


model = Net()

# 交叉熵损失
criterion = torch.nn.CrossEntropyLoss()
# 随机梯度下降，momentum表冲量，在更新时一定程度上保留原方向
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.5)


def train(epoch):
    running_loss = 0.0
    # 提取数据
    for batch_idx, data in enumerate(train_loader, 0):
        inputs, target = data
        # 优化器清零
        optimizer.zero_grad()
        # 前馈+反馈+更新
        outputs = model(inputs)
        loss = criterion(outputs, target)
        loss.backward()
        optimizer.step()
        # 累计loss
        running_loss += loss.item()

        if batch_idx % 300 == 299:
            print('[%d, %5d] loss: %.3f' % (epoch + 1, batch_idx + 1, running_loss / 300))
            running_loss = 0.0


def test():
    correct = 0
    total = 0
    # 避免计算梯度
    with torch.no_grad():
        for data in test_loader:
            images, labels = data
            outputs = model(images)
            # 取每一行（dim=1表第一个维度）最大值（max）的下标(predicted)及最大值(_)
            _, predicted = torch.max(outputs.data, dim=1)
            # 加上这一个批量的总数（batch_size），label的形式为[N,1]
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    print('Accuracy on test set: %d %%' % (100 * correct / total))


for epoch in range(10):
    train(epoch)
    test()
