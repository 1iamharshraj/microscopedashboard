import torch
import torch.nn as nn
import numpy as np
from PIL import Image
import cv2
import json
import os
from datetime import datetime

class DummyPlanktonSegmentationModel(nn.Module):
    """Dummy PyTorch model for plankton segmentation"""
    def __init__(self):
        super().__init__()
        # Encoder
        self.enc1 = nn.Conv2d(3, 64, 3, padding=1)
        self.enc2 = nn.Conv2d(64, 128, 3, padding=1)
        self.enc3 = nn.Conv2d(128, 256, 3, padding=1)
        
        # Decoder
        self.dec1 = nn.Conv2d(256, 128, 3, padding=1)
        self.dec2 = nn.Conv2d(128, 64, 3, padding=1)
        self.dec3 = nn.Conv2d(64, 1, 3, padding=1)  # Single channel for mask
        
        self.pool = nn.MaxPool2d(2, 2)
        self.upsample = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        
    def forward(self, x):
        # Encoder
        e1 = torch.relu(self.enc1(x))
        e2 = self.pool(torch.relu(self.enc2(e1)))
        e3 = self.pool(torch.relu(self.enc3(e2)))
        
        # Decoder
        d1 = self.upsample(torch.relu(self.dec1(e3)))
        d2 = self.upsample(torch.relu(self.dec2(d1)))
        mask = torch.sigmoid(self.dec3(d2))
        
        return mask

class DummyPlanktonClassifier(nn.Module):
    """Dummy PyTorch model for plankton classification"""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(128 * 8 * 8, 256)
        self.fc2 = nn.Linear(256, 20)  # 20 plankton species
        
    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = self.pool(torch.relu(self.conv3(x)))
        x = x.view(-1, 128 * 8 * 8)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

class PlanktonAnalyzer:
    def __init__(self):
        self.device = torch.device("cpu")  # Use CPU for compatibility
        self.segmentation_model = DummyPlanktonSegmentationModel()
        self.classifier_model = DummyPlanktonClassifier()
        
        # Initialize models
        self.segmentation_model.load_state_dict(self.segmentation_model.state_dict())
        self.classifier_model.load_state_dict(self.classifier_model.state_dict())
        
        self.segmentation_model.eval()
        self.classifier_model.eval()
        
        # Plankton species names
        self.species_names = [
            'Diatom', 'Dinoflagellate', 'Copepod', 'Radiolarian', 'Foraminifera',
            'Coccolithophore', 'Ciliate', 'Flagellate', 'Nauplius', 'Amphipod',
            'Cladocera', 'Rotifer', 'Chaetognath', 'Appendicularian', 'Polychaete',
            'Crustacean_Larva', 'Fish_Larva', 'Gelatinous_Zooplankton', 'Bacteria', 'Virus'
        ]
    
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
    
    def postprocess_segmentation(self, mask_output, original_image):
        """Convert segmentation output to binary mask"""
        try:
            # Convert tensor to numpy
            mask = mask_output.squeeze().cpu().numpy()
            
            # Apply threshold to create binary mask
            binary_mask = (mask > 0.5).astype(np.uint8) * 255
            
            # Resize mask to original image size
            original_height, original_width = original_image.shape[:2]
            binary_mask = cv2.resize(binary_mask, (original_width, original_height))
            
            return binary_mask
        except Exception as e:
            raise Exception(f"Segmentation postprocessing failed: {str(e)}")
    
    def postprocess_classification(self, classification_output):
        """Convert classification output to species prediction"""
        try:
            # Apply softmax to get probabilities
            probabilities = torch.softmax(classification_output, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0, predicted_class].item()
            
            return {
                'species_id': int(predicted_class),
                'species_name': self.species_names[predicted_class],
                'confidence': float(confidence),
                'all_probabilities': probabilities[0].cpu().numpy().tolist()
            }
        except Exception as e:
            raise Exception(f"Classification postprocessing failed: {str(e)}")
    
    def create_overlay(self, original_image, mask):
        """Create overlay of mask on original image"""
        try:
            # Convert mask to 3-channel
            mask_colored = cv2.applyColorMap(mask, cv2.COLORMAP_JET)
            
            # Create overlay
            overlay = cv2.addWeighted(original_image, 0.7, mask_colored, 0.3, 0)
            
            return overlay
        except Exception as e:
            print(f"Error creating overlay: {e}")
            return original_image
    
    def predict(self, image_path):
        """Run inference on the image"""
        try:
            # Preprocess image
            image_tensor, original_image = self.preprocess_image(image_path)
            
            # Run segmentation
            with torch.no_grad():
                mask_output = self.segmentation_model(image_tensor)
                classification_output = self.classifier_model(image_tensor)
            
            # Postprocess results
            binary_mask = self.postprocess_segmentation(mask_output, original_image)
            classification_result = self.postprocess_classification(classification_output)
            
            return {
                'success': True,
                'segmentation_mask': binary_mask.tolist(),
                'classification': classification_result,
                'image_shape': original_image.shape,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def save_visualization(self, original_image, mask, classification_result, output_path):
        """Save visualization of segmentation and classification results"""
        try:
            # Create overlay
            overlay = self.create_overlay(original_image, mask)
            
            # Add text with classification result
            species_name = classification_result['species_name']
            confidence = classification_result['confidence']
            text = f"{species_name} ({confidence:.2f})"
            
            cv2.putText(overlay, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            cv2.imwrite(output_path, overlay)
            return True
            
        except Exception as e:
            print(f"Error saving visualization: {e}")
            return False

# Global model instance
plankton_model = PlanktonAnalyzer()
