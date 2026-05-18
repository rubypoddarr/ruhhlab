def interpret_scene(labels):
    label_set = set(labels)

    if 'car' in label_set and 'person' in label_set:
        return "Urban traffic environment with human activity and vehicles interacting in shared space."
    if 'person' in label_set and 'cell phone' in label_set:
        return "Digital interaction scene — a person engaged with a mobile device."
    if 'person' in label_set and 'laptop' in label_set:
        return "Workspace environment with a person using computing equipment."
    if 'person' in label_set and 'bicycle' in label_set:
        return "Active lifestyle scene — cycling activity in an open environment."
    if 'person' in label_set and 'motorcycle' in label_set:
        return "Transportation scene with human-vehicle interaction."
    if 'dog' in label_set or 'cat' in label_set:
        if 'person' in label_set:
            return "Domestic scene with animal and human companionship."
        return "Animal presence detected — natural or domestic environment."
    if 'chair' in label_set and 'dining table' in label_set:
        return "Indoor dining or meeting space with furniture arrangement."
    if 'tv' in label_set or 'laptop' in label_set or 'keyboard' in label_set:
        return "Technology-rich indoor environment with electronic devices."
    if 'bottle' in label_set or 'cup' in label_set or 'bowl' in label_set:
        return "Kitchen or dining context with food and beverage items."
    if 'bus' in label_set or 'truck' in label_set:
        return "Heavy vehicle traffic environment with large transport units."
    if len(labels) > 5:
        return "Complex, crowded environment with multiple distinct objects and high visual activity."
    if len(labels) == 0:
        return "No significant objects detected in this scene."
    if 'person' in label_set:
        return f"Human-centric scene with {len(labels)} detected element(s)."
    return f"Mixed environment with {len(labels)} detected object(s)."


def extract_relationships(labels):
    label_set = set(labels)
    relationships = []

    if 'person' in label_set and 'car' in label_set:
        relationships.append("Person interacting with traffic environment")
    if 'person' in label_set and 'cell phone' in label_set:
        relationships.append("Person using a mobile device")
    if 'person' in label_set and 'laptop' in label_set:
        relationships.append("Person operating a computing device")
    if 'person' in label_set and ('dog' in label_set or 'cat' in label_set):
        relationships.append("Human-animal interaction detected")
    if 'person' in label_set and 'bicycle' in label_set:
        relationships.append("Person with bicycle — possible active transport")
    if 'car' in label_set and 'truck' in label_set:
        relationships.append("Mixed vehicle environment")
    if not relationships and 'person' in label_set:
        for label in labels:
            if label != 'person':
                relationships.append(f"Person in proximity to {label}")
                break

    return relationships


def generate_insight(detections):
    if not detections:
        return "No objects detected above confidence threshold."
    avg_conf = sum(d['confidence'] for d in detections) / len(detections)
    count = len(detections)
    if avg_conf >= 0.75:
        quality = "High confidence"
    elif avg_conf >= 0.55:
        quality = "Moderate confidence"
    else:
        quality = "Low confidence"
    return f"{quality} detection with {count} object(s) identified. Average confidence: {avg_conf:.2f}."
