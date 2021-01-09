import torch
import numpy as np
import argparse
import os
import matplotlib.pyplot as plt
import cv2


from flownet2.models import FlowNet2  # the path is depended on where you create this module
from flownet2.utils_flownet2.frame_utils import read_gen  # the path is depended on where you create this module
from flownet2.utils_flownet2 import flow_utils, tools
import torchvision.transforms as transforms

def writeFlow(name, flow):
    np.save(name, flow)

def readFlow(name):
    flow = np.load(name, allow_pickle=True)
    return flow


def get_frame_flow(img1, img2, model, device, width, height):
    pim1 = cv2.imread(img1)
    pim2 = cv2.imread(img2)
    pim1 = cv2.resize(pim1, (width, height) )
    pim2 = cv2.resize(pim2, (width, height) )
    transform = transforms.Compose([
        transforms.ToTensor(),
    ])

    pim1 = transform(pim1).unsqueeze(dim=0).to(device)
    pim2 = transform(pim2).unsqueeze(dim=0).to(device)

    pred_flow_esti_tensor = torch.cat([pim1.view(-1, 3, 1, pim1.shape[-2], pim1.shape[-1]),
                                       pim2.view(-1, 3, 1, pim2.shape[-2], pim2.shape[-1])], 2)

    result = model(pred_flow_esti_tensor * 255.0).squeeze()
    data = result.data.cpu().numpy().transpose(1, 2, 0)


    return data



if __name__ == '__main__':
    # obtain the necessary args for construct the flownet framework
    parser = argparse.ArgumentParser()
    parser.add_argument('--fp16', action='store_true', help='Run model in pseudo-fp16 mode (fp16 storage fp32 math).')
    parser.add_argument("--rgb_max", type=float, default=255.)
    
    args = parser.parse_args()
    # print(args)

    # initial a Net
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    net = FlowNet2(args).to(device)
    # load the state_dict
    dict_ = torch.load("flownet2/FlowNet2_checkpoint.pth.tar")
    net.load_state_dict(dict_["state_dict"])


    # # test 
    # img1 = "/data0/lyx/VAD_datasets/avenue/training/frames/01/0001.jpg"
    # img2 = "/data0/lyx/VAD_datasets/avenue/training/frames/01/0002.jpg"

    # flow = get_frame_flow(img1, img2, net, device, 512, 384)
    # writeFlow('flow/flow1.npy',flow)
    # # print( readFlow('flow/flow1.npy') )

    # 计算所有图像的flow
    videos = "/data0/lyx/VAD_datasets/ped2/testing/frames"
    save_path = "./flow/ped2/test"
    video_list = sorted(os.listdir(videos))
    for video in video_list:
        frame_list = sorted(os.listdir(os.path.join(videos, video)))
        for i in range( 0, len(frame_list)-1 ):
            frame1 = os.path.join(videos, video, frame_list[i])
            frame2 = os.path.join(videos, video, frame_list[i+1])
            # print(frame2)
            flow = get_frame_flow( frame1, frame2, net, device, 512, 384 ) 
            # print(flow.shape)

            dir_ = os.path.join(save_path, video)
            if not os.path.exists(dir_):
                os.mkdir(dir_)
            writeFlow(dir_ + "/" + frame_list[i].split('.')[0] + ".npy", flow)


            # 这个地方遇到一个问题，每次计算了大概103张图的光流之后就会报错
            # 暂时没解决
            
             


    
