# -*- coding: utf-8 -*-
import IAgoraRtcEngine
import ctypes
import os
import numpy as np
import tensorflow as tf
from object_detection.utils import label_map_util

from PIL import Image
import cv2

class CallBackData:
    def __init__(self):
        self.localUid = -1
        self.remoteUid = -1
        self.rawDataCounter = 0
        self.joinChannelSuccess = False
        self.remoteUserWindowSet = False
        self.remoteUserEnableVideo = True
        self.localWindowSet = False

        MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'
        PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
        PATH_TO_LABELS = os.path.join('object_detection/data', 'mscoco_label_map.pbtxt')
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
        self.category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
        self.image = None
        self.isImageDetect = True
        self.detectReady = True

EventHandlerData = CallBackData()

class EventHandler:
    @staticmethod
    def onJoinChannelSuccess(channel, uid, elapsed):
        print ("JoinChannelSuccess: channel=%s, uid=%d, elapsed=%d"%(channel, uid, elapsed))
        EventHandlerData.localUid = uid
        EventHandlerData.joinChannelSuccess = True

    @staticmethod
    def onLeaveChannel(duration, txBytes, rxBytes, txKBitRate,
        rxKBitRate, rxAudioKBitRate, txAudioKBitRate, rxVideoKBitRate,
        txVideoKBitRate, lastmileDelay, userCount, cpuAppUsage,
        cpuTotalUsage):
        print ("leave channel")
        EventHandlerData.joinChannelSuccess = False
        EventHandlerData.localWindowSet = False
        EventHandlerData.remoteUserWindowSet = False
        EventHandlerData.localUid = -1
        EventHandlerData.remoteUid = -1


    @staticmethod
    def onClientRoleChanged(oldRole, newRole):
        pass

    @staticmethod
    def onConnectionStateChanged(state, reason):
        pass

    @staticmethod
    def onConnectionLost():
        print ("connection lost")

    @staticmethod
    def onRejoinChannelSuccess(channel, uid, elapsed):
        print ("rejoin channel success")

    @staticmethod
    def onUserJoined(uid, elapsed):
        print ("a remote user joined, uid=%d"%uid)
        EventHandlerData.remoteUid = uid

    @staticmethod
    def onUserOffline(uid, reason):
        print ("a remote user offline, uid=%d, reason=%d"%(uid, reason))
        EventHandlerData.remoteUid = -1
        EventHandlerData.remoteUserWindowSet = False

    @staticmethod
    def onFirstLocalAudioFrame(elapsed):
        pass

    @staticmethod
    def onMicrophoneEnabled(enabled):
        if enabled:
            print ("microphone enabled")

    @staticmethod
    def onUserEnableVideo(uid, enabled):
        print ("UserEnableVideo, uid=%d"%uid)

    @staticmethod
    def onFirstRemoteAudioFrame(uid, elapsed):
        print ("first remote audio frame, uid=%d" % uid)

    @staticmethod
    def onFirstRemoteVideoDecoded(uid, width, height, elapsed):
        print ("FirstRemoteVideoDecoded: uid=%d, width=%d, height=%d, elapsed=%d" % (uid, width, height, elapsed))

    @staticmethod
    def onNetworkQuality(uid, txQuality, rxQuality):
        pass

    @staticmethod
    def onAudioQuality(uid, quality, delay, lost):
        pass

    @staticmethod
    def onRtcStats(duration, txBytes, rxBytes, txKBitRate,
        rxKBitRate, rxAudioKBitRate, txAudioKBitRate, rxVideoKBitRate,
        txVideoKBitRate, lastmileDelay, userCount, cpuAppUsage,
        cpuTotalUsage):
        pass

    @staticmethod
    def onLocalVideoStats(sentBitrate, sentFrameRate):
        pass

    @staticmethod
    def onUserEnableLocalVideo(uid, enabled):
        pass

    @staticmethod
    def onRemoteVideoStats(uid, delay, width, height, receivedBitrate,
                           decoderOutputFrameRate, rendererOutputFrameRate, rxStreamType):
        pass

    @staticmethod
    def onRemoteAudioTransportStats(uid, delay, lost, rxKBitRate):
        pass

    @staticmethod
    def onRemoteVideoTransportStats(uid, delay, lost, rxKBitRate):
        pass

    @staticmethod
    def onApiCallExecuted(err, api, result):
        pass

    @staticmethod
    def onRemoteAudioStats(uid, quality,
			networkTransportDelay, jitterBufferDelay,
			audioLossRate):
        pass

    @staticmethod
    def onCameraReady():
        pass

    @staticmethod
    def onFirstLocalVideoFrame(width, height, elapsed):
        pass

    @staticmethod
    def onRemoteVideoStateChanged(uid, state):
        pass

    @staticmethod
    def onConnectionInterrupted():
        print ("connection lost")

    @staticmethod
    def onFirstRemoteVideoFrame(uid, width, height, elapsed):
        pass

class VideoFrameObserver:
    @staticmethod
    def onCaptureVideoFrame(width, height, yStride,
			uStride, vStride, yBuffer, uBuffer, vBuffer,
			rotation, renderTimeMs, avsync_type):
        pass

    @staticmethod
    def onRenderVideoFrame(uid, width, height, yStride,
                            uStride, vStride, yBuffer, uBuffer, vBuffer,
                            rotation, renderTimeMs, avsync_type):
        if EventHandlerData.isImageDetect:
            y_array = (ctypes.c_uint8 * (width * height)).from_address(yBuffer)
            u_array = (ctypes.c_uint8 * ((width // 2) * (height // 2))).from_address(uBuffer)
            v_array = (ctypes.c_uint8 * ((width // 2) * (height // 2))).from_address(vBuffer)

            Y = np.frombuffer(y_array, dtype=np.uint8).reshape(height, width)
            U = np.frombuffer(u_array, dtype=np.uint8).reshape((height // 2, width // 2)).repeat(2, axis=0).repeat(2, axis=1)
            V = np.frombuffer(v_array, dtype=np.uint8).reshape((height // 2, width // 2)).repeat(2, axis=0).repeat(2, axis=1)
            YUV = np.dstack((Y, U, V))[:height, :width, :]
            RGB = cv2.cvtColor(YUV, cv2.COLOR_YUV2RGB, 3)
            EventHandlerData.image = Image.fromarray(RGB)
            EventHandlerData.isImageDetect = False
