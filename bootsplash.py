import argparse
import cv2
from pathlib import Path

def extract_and_crop_frames(video_path: str, output_folder: str, target_fps: float, resolution: str = None):
    """
    Extracts frames from an MP4 video at a configurable FPS, optionally center-crops 
    them to a target resolution, and saves them as PNGs.
    """
    video_path = Path(video_path)
    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse target resolution if provided
    target_w, target_h = None, None
    if resolution:
        try:
            target_w, target_h = map(int, resolution.lower().split('x'))
        except ValueError:
            print("Error: Resolution format must be WIDTHxHEIGHT (e.g., 1280x400)")
            return

    # Open the video file
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return

    # Get native video properties
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    if video_fps == 0:
        print("Error: Could not determine video FPS.")
        cap.release()
        return

    # Calculate frame interval (extract every Nth frame)
    frame_interval = max(1, round(video_fps / target_fps))
    
    print(f"Video Native FPS: {video_fps:.2f}")
    print(f"Target Extraction FPS: {target_fps} (Saving every {frame_interval} frames)")
    if resolution:
        print(f"Target Resolution (Center-Cropped): {target_w}x{target_h}")
    print(f"Extracting frames to '{output_dir}'...")

    frame_idx = 0
    saved_count = 0

    while True:
        success, frame = cap.read()
        if not success:
            break  # End of video reached

        # Process frame only if it matches our interval
        if frame_idx % frame_interval == 0:
            # Handle Center Cropping
            if target_w and target_h:
                orig_h, orig_w, _ = frame.shape
                
                # Verify that the crop region fits inside the native video
                if target_w > orig_w or target_h > orig_h:
                    print(f"\nError: Target crop size {target_w}x{target_h} is larger than video size {orig_w}x{orig_h}")
                    cap.release()
                    return

                # Calculate start/end indices for center crop
                start_x = (orig_w - target_w) // 2
                start_y = (orig_h - target_h) // 2
                
                # Crop the matrix using NumPy slicing
                frame = frame[start_y:start_y+target_h, start_x:start_x+target_w]

            # Save the processed frame
            filename = output_dir / f"frame_{saved_count:06d}.png"
            cv2.imwrite(str(filename), frame)
            saved_count += 1

        frame_idx += 1

    cap.release()
    print(f"Finished! Successfully saved {saved_count} frames.")

if __name__ == "__main__":
    # Initialize argument parser
    parser = argparse.ArgumentParser(
        description="Extract and optional center-crop frames from an MP4 video at a configurable frame rate as PNGs."
    )
    
    # Add command-line arguments
    parser.add_argument(
        "-i", "--input", 
        required=True, 
        help="Path to the input MP4 video file."
    )
    parser.add_argument(
        "-o", "--output", 
        default="frames", 
        help="Directory where PNG frames will be saved (default: 'frames')."
    )
    parser.add_argument(
        "-f", "--fps", 
        type=float, 
        default=1.0, 
        help="Target frames per second to extract (default: 1.0)."
    )
    parser.add_argument(
        "-r", "--resolution",
        default=None,
        help="Target resolution to center-crop frames to, format WIDTHxHEIGHT (e.g., 1280x400)."
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the extraction and cropping pipeline
    extract_and_crop_frames(args.input, args.output, args.fps, args.resolution)

