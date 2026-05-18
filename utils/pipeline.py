import cv2
from utils.detector import detect
from utils.scene import interpret_scene, extract_relationships, generate_insight


def run_pipeline(input_path, output_path):
    detections, annotated_image = detect(input_path)

    labels = [d['label'] for d in detections]

    scene = interpret_scene(labels)
    relationships = extract_relationships(labels)
    insight = generate_insight(detections)

    if annotated_image is not None:
        cv2.imwrite(output_path, annotated_image)
        del annotated_image

    return {
        'objects': detections,
        'scene': scene,
        'relationships': relationships,
        'insight': insight,
    }
