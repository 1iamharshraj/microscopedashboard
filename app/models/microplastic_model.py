import torch
import torch.nn as nn
import numpy as np
from PIL import Image
import cv2
import json
import os
from datetime import datetime

class DummyMicroplasticModel(nn.Module):
    """Dummy PyTorch model for microplastic detection"""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 8 * 8, 128)
        self.fc2 = nn.Linear(128, 5)  # 5 classes: background, fiber, fragment, pellet, film
        
    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = self.pool(torch.relu(self.conv3(x)))
        x = x.view(-1, 64 * 8 * 8)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

class MicroplasticDetector:
    def __init__(self):
        self.device = torch.device("cpu")  # Use CPU for compatibility
        self.model = DummyMicroplasticModel()
        self.model.load_state_dict(self.model.state_dict())  # Dummy initialization
        self.model.eval()
        
        # Class names for microplastics
        self.class_names = ['background', 'fiber', 'fragment', 'pellet', 'film']
        
    def preprocess_image(self, image_path):
        """Preprocess image for model input"""
        try:
            # Load and resize image
            image = Image.open(image_path).convert('RGB')
            image = image.resize((224, 224))
            
            # Convert to tensor
            image_array = np.array(image)
            image_tensor = torch.from_numpy(image_array).permute(2, 0, 1).float()
            image_tensor = image_tensor.unsqueeze(0) / 255.0
            
            return image_tensor, image_array
        except Exception as e:
            raise Exception(f"Image preprocessing failed: {str(e)}")
    
    def postprocess_detections(self, predictions, original_image):
        """Convert model predictions to bounding boxes and labels"""
        # Generate dummy bounding boxes (in real implementation, this would come from object detection)
        height, width = original_image.shape[:2]
        
        # Simulate some detections
        detections = []
        np.random.seed(42)  # For consistent dummy results
        
        for i in range(np.random.randint(1, 4)):  # 1-3 detections
            x1 = np.random.randint(0, width//2)
            y1 = np.random.randint(0, height//2)
            x2 = x1 + np.random.randint(50, 150)
            y2 = y1 + np.random.randint(50, 150)
            
            # Ensure coordinates are within image bounds
            x2 = min(x2, width)
            y2 = min(y2, height)
            
            class_id = np.random.randint(1, 5)  # Skip background
            confidence = np.random.uniform(0.6, 0.95)
            
            detection = {
                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                'class_id': int(class_id),
                'class_name': self.class_names[class_id],
                'confidence': float(confidence)
            }
            detections.append(detection)
        
        return detections
    
    def predict(self, image_path):
        """Run inference on the image"""
        try:
            # Preprocess image
            image_tensor, original_image = self.preprocess_image(image_path)
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(image_tensor)
                predictions = torch.softmax(outputs, dim=1)
            
            # Postprocess to get detections
            detections = self.postprocess_detections(predictions, original_image)
            
            return {
                'success': True,
                'detections': detections,
                'image_shape': original_image.shape,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def draw_detections(self, image_path, detections, output_path):
        """Draw bounding boxes on the image"""
        try:
            image = cv2.imread(image_path)
            
            for detection in detections['detections']:
                x1, y1, x2, y2 = detection['bbox']
                class_name = detection['class_name']
                confidence = detection['confidence']
                
                # Draw bounding box
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw label
                label = f"{class_name}: {confidence:.2f}"
                cv2.putText(image, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            cv2.imwrite(output_path, image)
            return True
            
        except Exception as e:
            print(f"Error drawing detections: {e}")
            return False

# Global model instance
microplastic_model = MicroplasticDetector()
