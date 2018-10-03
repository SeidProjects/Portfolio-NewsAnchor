from collections import deque
from threading import Thread
import Queue as queue
import time
import cv2
import numpy as np

class VideoClipWriter:
    def __init__(self, bufSize=64, timeout=1.0):
        self.bufSize = bufSize
        self.timeout = timeout

        self.frames = deque(maxlen=bufSize)
        self.framesToWrite = None
        self.writer = None
        self.thread = None
        self.isRecording = False
        self.startFrame = None
        self.clipName = None
        self.keyword = None

    def update(self, frame):
        self.frames.appendleft(frame)
        if (self.isRecording):
            self.framesToWrite.put(frame)

    def start(self, keywords, clipName, startFrame, outputPath, fourcc, fps):
        self.isRecording = True
        self.writer = cv2.VideoWriter(outputPath, fourcc, fps, (self.frames[0].shape[1], self.frames[0].shape[0]), True)
        self.framesToWrite = queue.Queue()
        self.clipName = clipName
        self.startFrame = startFrame
        self.keywords = keywords

        #for i in range(len(self.frames), 0, -1):
        #    self.framesToWrite.put(self.frames[i-1])

        self.thread = Thread(target=self.write, args = ())
        self.thread.daemon = True
        self.thread.start()
        
    def write(self):
        while True:
            if not self.isRecording:
                return

            if not self.framesToWrite.empty():
                frame = self.framesToWrite.get()
                self.writer.write(frame)
            else:
                time.sleep(self.timeout)

    def flush(self):
        while not self.framesToWrite.empty():
            frame = self.framesToWrite.get()
            self.writer.write(frame)

    def finish(self):
        self.isRecording = False
        self.thread.join()
        self.flush()
        self.writer.release()
