import random
import argparse
from pathlib import Path
import numpy as np
import torch
import torchvision
from torchvision import transforms
from torch.backends import cudnn
from utils.train_util import load_model_pytorch, train
from nets.resnet_cifar import ResNet_CIFAR
from nets.vgg import VGG_CIFAR

#%%
'''
    Configuration
'''
parser = argparse.ArgumentParser(description='Training model')
parser.add_argument('--dataset', type=str, default='cifar10',
                    help='cifar10 or imagenet')
parser.add_argument('--dataroot', type=str, metavar='PATH',
                    help='Path to Dataset folder')
parser.add_argument('--model', type=str, default='resnet56',
                    help='model to use, only resnet56, resnet20')
parser.add_argument('--pretrained', type=int, default=0,
                    help='whether to use pretrained model')
parser.add_argument('--batch_size', type=int, default=128,
                    help='input batch size for statistics (default: 128)')
parser.add_argument('--test_batch_size', type=int, default=256,
                    help='input batch size for testing (default: 256)')
parser.add_argument('--gpus', default=None, 
                    help='List of GPUs used for training - e.g 0,1,3')
parser.add_argument('-j', '--workers', default=8, type=int, metavar='N',
                    help='Number of data loading workers (default: 8)')
parser.add_argument('--seed', type=int, default=0, 
                    help='random seed (default: 0)')
parser.add_argument('--epochs', type=int, default=300,
                    help='epochs to train (default: 300)')
parser.add_argument('--lr', type=float, default=0.1,
                    help='learning rate to train (default: 0.1)')
parser.add_argument('--save_acc', type=float, default=94.0,
                    help='save accuracy')
parser.add_argument('--label_smoothing', type=float, default='0.0',
                    help='label smoothing rate')
parser.add_argument('--warmup_step', type=int, default='0',
                    help='warm up epochs')
parser.add_argument('--warm_lr', type=float, default='10e-5',
                    help='warm up learning rate')


def setup_seed(seed):
     torch.manual_seed(seed)
     torch.cuda.manual_seed_all(seed)
     torch.cuda.manual_seed(seed)
     np.random.seed(seed)
     random.seed(seed)
     cudnn.deterministic = True


def Training():
    '''configuration'''
    args = parser.parse_args()
    args.dataset = 'cifar100'
    project_dir = Path(__file__).resolve().parent
    args.dataroot = project_dir / 'data'
    args.model = 'vgg13'
    args.pretrained = 0
    args.gpus = 0
    args.j = 4
    args.epochs = 30
    args.lr = 0.1
    args.save_acc = 0.0
    args.label_smoothing = 0.0 
    args.warmup_step = 0
    args.warm_lr = 10e-5
    print(args)
    
    setup_seed(args.seed)
    save_info = project_dir / 'ckpt' / args.model / 'cifar100' 
    
    if args.dataset == 'cifar10':
        '''load data and model'''
        mean=[125.31 / 255, 122.95 / 255, 113.87 / 255]
        std=[63.0 / 255, 62.09 / 255, 66.70 / 255]
        transform_train = transforms.Compose([
            transforms.RandomCrop(32, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(mean, std),
            ])
        transform_test = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean,std)
            ])
        trainset = torchvision.datasets.CIFAR10(root=args.dataroot, train=True, download=False, transform=transform_train)
        testset = torchvision.datasets.CIFAR10(root=args.dataroot, train=False, download=False, transform=transform_test)
        
        if args.model == 'resnet56':
            net = ResNet_CIFAR(depth=56, num_classes=10)
        elif args.model == 'resnet20':
            net = ResNet_CIFAR(depth=20, num_classes=10)
        elif args.model == 'vgg':
            net = VGG_CIFAR(num_classes=10)
        else:
            print('no model')    

    if args.dataset == 'cifar100':
        '''load data and model'''
        mean=[129.3 / 255, 124.1 / 255, 112.4 / 255]
        std=[68.2 / 255, 65.4 / 255, 70.4 / 255]
        transform_train = transforms.Compose([
            transforms.RandomCrop(32, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(mean, std),
            ])
        transform_test = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean,std)
            ])
        trainset = torchvision.datasets.CIFAR100(root=args.dataroot, train=True, download=False, transform=transform_train)
        testset = torchvision.datasets.CIFAR100(root=args.dataroot, train=False, download=False, transform=transform_test)
        
        if args.model == 'resnet56':
            net = ResNet_CIFAR(depth=56, num_classes=100)
        elif args.model == 'resnet20':
            net = ResNet_CIFAR(depth=20, num_classes=100)
        elif args.model == 'resnet32':
            net = ResNet_CIFAR(depth=32, num_classes=100)
        elif args.model == 'vgg16':
            net = VGG_CIFAR(cfg_index=16, num_classes=100)
        elif args.model == 'vgg11':
            net = VGG_CIFAR(cfg_index=11, num_classes=100)
        elif args.model == 'vgg13':
            net = VGG_CIFAR(cfg_index=13, num_classes=100)
        else:
            print('no model')    
    
    net = net.cuda()
    if args.pretrained == 1:
        model_path = project_dir / 'ckpt' / args.model / 'seed_0_acc_49.65.pth'
        load_model_pytorch(net, model_path, args.model)
        
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=args.batch_size, shuffle=False, num_workers=4)
    testloader = torch.utils.data.DataLoader(testset, batch_size=args.test_batch_size, shuffle=False, num_workers=4)
    
    '''training''' 
    train(net, epochs=args.epochs, lr=args.lr, train_loader=trainloader, 
          test_loader=testloader, save_info=save_info, save_acc=args.save_acc, seed=args.seed,
          label_smoothing=args.label_smoothing, warmup_step=args.warmup_step, warm_lr=args.warm_lr)

    print('finished')
    
    

if __name__=='__main__':
    Training()