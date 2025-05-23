import cv2
import numpy as np
import json
import os

VIDEO_PATH = r"videos\c_mback.mp4"
FRAME_OUTPUT_DIR = "output/framesv5"
JSON_OUTPUT_PATH = "output/blobs/blobs4.json"

os.makedirs(FRAME_OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(JSON_OUTPUT_PATH), exist_ok=True)

def preprocess_frame(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply thresholding (tune this!)
    _, thresh = cv2.threshold(blurred, 75, 255, cv2.THRESH_BINARY)

    return thresh

def detect_blobs(thresh, frame, frame_id):
    # Connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh, connectivity=8)

    blobs = []
    for i in range(1, num_labels):  # skip background
        # x, y = int(centroids[i][0]), int(centroids[i][1])
        # area = stats[i, cv2.CC_STAT_AREA]

        x, y, w, h, area = stats[i]
        cx, cy = centroids[i]

        if area < 5000 or area > 15000:
            continue
    
        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Annotate area and centroid
        text = f"Area: {area}, ID: {id}"
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.4, (0, 255, 255), 1)
        
        cv2.imwrite(f"{FRAME_OUTPUT_DIR}/labelled_frame_{frame_id:04d}.png", frame)

        # Optional: Filter small and large blobs
        
            
        # Seat position logic using raw y value
        if y > 700:
            seat_position = "front"
        else:
            seat_position = "back"

        blobs.append({
            "object_id": blob_id,
            "x": int(x),
            "y": int(y),
            "area": int(area),
            "seat_position": seat_position
        })

    return blobs

def main():
    cap = cv2.VideoCapture(VIDEO_PATH)
    frame_id = 0
    output_data = []
    previous_positions = {}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed during read.")
            break

        if frame_id % 150 == 0:
            # Save original frame (optional for debugging)
            cv2.imwrite(f"{FRAME_OUTPUT_DIR}/frame_{frame_id:04d}.png", frame)

            thresh = preprocess_frame(frame)
            cv2.imwrite(f"{FRAME_OUTPUT_DIR}/thresh_{frame_id:04d}.png", thresh)
            blobs = detect_blobs(thresh, frame, frame_id)

            updated_blobs = []
            blob_count = 0 
            for blob in blobs:
                obj_id = blob["object_id"]
                blob_count += 1
                x, y = blob["x"], blob ["y"]

                # Save previous position if available
                if obj_id in previous_positions:
                    prev_x, prev_y = previous_positions[obj_id]
                    blob["prev_x"] = prev_x
                    blob["prev_y"] = prev_y
                else:
                    blob["prev_x"] = None
                    blob["prev_y"] = None
                
                # Update for next frame
                previous_positions[obj_id] = (x, y)
                updated_blobs.append(blob)

            frame_info = {
                "frame_id": frame_id,
                "blobs": blobs,
                "blob_count": blob_count
            }
            output_data.append(frame_info)
        frame_id += 1

    cap.release()

    # Save to JSON
    with open(JSON_OUTPUT_PATH, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Processed {frame_id} frames. Blob data saved to {JSON_OUTPUT_PATH}")

if __name__ == "__main__":
    main()
