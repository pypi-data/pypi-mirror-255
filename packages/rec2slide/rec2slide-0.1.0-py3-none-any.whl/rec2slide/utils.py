from cv2 import VideoCapture, CAP_PROP_FPS
from model import Video, Frame
from PIL import Image

class Utils:
    @staticmethod
    def read_video(path: str, interval: int) -> Video:
        cap = VideoCapture(path)
        fps = cap.get(CAP_PROP_FPS)
        frames = []
        ret, frame = cap.read()
        while ret:
            frame_id = int(cap.get(1))
            if frame_id % interval == 0:
                frames.append(Frame(data=frame, pos_id=frame_id))
            ret, frame = cap.read()
        return Video(
                    frames=frames, 
                    fps=fps, 
                    total_frames=len(frames), 
                    duration=len(frames)/fps
                )
        
    @staticmethod
    def frames2pdf(result: Video, output_path: str) -> None:
        pil_imgs = [Image.fromarray(frame.data) for frame in result]
        pil_imgs[0].save(
            output_path,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=pil_imgs[1:],
        )

    @staticmethod
    def frames2jpg(result: Video, output_path: str) -> None:
        for i, frame in enumerate(result):
            Image.fromarray(frame.data).save(f"{output_path}/frame_{i}.jpg")
    
    @staticmethod
    def frames2png(result: Video, output_path: str) -> None:
        for i, frame in enumerate(result):
            Image.fromarray(frame.data).save(f"{output_path}/frame_{i}.png")
