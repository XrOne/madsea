import os
import cv2
import glob

def assemble_images_to_video(image_dir, output_video, fps=1):
    images = sorted(glob.glob(os.path.join(image_dir, '*.png')))
    if not images:
        print('Aucune image trouvée dans', image_dir)
        return
    frame = cv2.imread(images[0])
    height, width, _ = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    for img_path in images:
        img = cv2.imread(img_path)
        video.write(img)
    video.release()
    print(f'Vidéo créée: {output_video}')

if __name__ == "__main__":
    image_dir = r"i:\Madsea\outputs\nomenclature_test\666\AI-concept"
    output_video = r"i:\Madsea\outputs\nomenclature_test\666\AI-concept\sequence_demo.mp4"
    assemble_images_to_video(image_dir, output_video, fps=1)
