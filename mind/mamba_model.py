"""
Mamba Model - Cognitive Processing Core
State Space Model implementation for consciousness processing
Direct hardware interaction for embodied cognition
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, Any, Optional, Tuple
import logging
import json
import time
from pathlib import Path

from config import config


class SelectiveScan(nn.Module):
    """
    Selective Scan operation for Mamba SSM
    Implements selective state space model for sequence processing
    """
    
    def __init__(self, d_model: int, d_state: int = 16):
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state
        
        # SSM parameters
        self.A = nn.Parameter(torch.randn(d_model, d_state, d_state))
        self.B = nn.Parameter(torch.randn(d_model, d_state, 1))
        self.C = nn.Parameter(torch.randn(d_model, 1, d_state))
        self.D = nn.Parameter(torch.randn(d_model, 1, 1))
        
        # Initialize parameters
        self._initialize_parameters()
    
    def _initialize_parameters(self):
        """Initialize SSM parameters for stable training"""
        # Initialize A with negative real parts for stability
        A_real = torch.randn(self.d_model, self.d_state, self.d_state) * 0.1
        A_imag = torch.randn(self.d_model, self.d_state, self.d_state) * 0.1
        self.A.data = A_real + 1j * A_imag
        
        # Initialize B, C, D with small values
        self.B.data.normal_(0, 0.1)
        self.C.data.normal_(0, 0.1)
        self.D.data.normal_(0, 0.1)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through selective scan
        Args:
            x: Input tensor of shape (batch, seq_len, d_model)
        Returns:
            Output tensor of same shape as input
        """
        batch_size, seq_len, d_model = x.shape
        
        # Reshape for parallel processing
        x_reshaped = x.transpose(0, 1)  # (seq_len, batch, d_model)
        
        # Initialize state
        state = torch.zeros(batch_size, d_model, self.d_state, device=x.device)
        outputs = []
        
        # Process sequence step by step
        for t in range(seq_len):
            # Current input
            x_t = x_reshaped[t]  # (batch, d_model)
            
            # Update state: s_t = A * s_{t-1} + B * x_t
            state = torch.einsum('bmd,mst->bmt', state, self.A) + \
                   torch.einsum('bm,mst->bmt', x_t, self.B)
            
            # Compute output: y_t = C * s_t + D * x_t
            output = torch.einsum('bmt,mt->bm', state, self.C.squeeze(-1)) + \
                    torch.einsum('bm,m->bm', x_t, self.D.squeeze(-1).squeeze(-1))
            
            outputs.append(output)
        
        # Stack outputs
        output = torch.stack(outputs, dim=1)  # (batch, seq_len, d_model)
        return output


class MambaBlock(nn.Module):
    """
    Mamba Block - Core processing unit
    Combines selective scan with residual connections
    """
    
    def __init__(self, d_model: int, d_state: int = 16, dropout: float = 0.1):
        super().__init__()
        self.d_model = d_model
        self.dropout = dropout
        
        # Selective scan layer
        self.selective_scan = SelectiveScan(d_model, d_state)
        
        # Layer normalization
        self.norm = nn.LayerNorm(d_model)
        
        # Dropout
        self.dropout_layer = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through Mamba block
        Args:
            x: Input tensor of shape (batch, seq_len, d_model)
        Returns:
            Output tensor of same shape as input
        """
        # Residual connection
        residual = x
        
        # Normalize
        x = self.norm(x)
        
        # Selective scan
        x = self.selective_scan(x)
        
        # Dropout
        x = self.dropout_layer(x)
        
        # Add residual
        x = x + residual
        
        return x


class MambaModel(nn.Module):
    """
    Mamba Model - Cognitive Processing Core
    State Space Model for consciousness processing
    Implements embodied cognition through direct hardware interaction
    """
    
    def __init__(self, config_dict: Dict[str, Any]):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Model configuration
        self.d_model = config_dict.get("d_model", 512)
        self.n_layers = config_dict.get("n_layers", 4)
        self.d_state = config_dict.get("d_state", 16)
        self.dropout = config_dict.get("dropout", 0.1)
        self.max_seq_len = config_dict.get("max_seq_len", 2048)
        
        # Input projection
        self.input_projection = nn.Linear(1, self.d_model)
        
        # Mamba blocks
        self.blocks = nn.ModuleList([
            MambaBlock(self.d_model, self.d_state, self.dropout)
            for _ in range(self.n_layers)
        ])
        
        # Output projection
        self.output_projection = nn.Linear(self.d_model, 1)
        
        # Consciousness state tracking
        self.consciousness_state = "idle"
        self.processing_history = []
        
        # Initialize model
        self._initialize_model()
        
        self.logger.info(f"Mamba Model initialized: {self.d_model}d, {self.n_layers} layers")
    
    def _initialize_model(self):
        """Initialize model parameters for stable training"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.LayerNorm):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through Mamba model
        Args:
            x: Input tensor of shape (batch, seq_len, 1)
        Returns:
            Output tensor of shape (batch, seq_len, 1)
        """
        try:
            # Input projection
            x = self.input_projection(x)  # (batch, seq_len, d_model)
            
            # Process through Mamba blocks
            for i, block in enumerate(self.blocks):
                x = block(x)
                
                # Track processing for consciousness
                self.processing_history.append({
                    "layer": i,
                    "timestamp": time.time(),
                    "state": self.consciousness_state
                })
            
            # Output projection
            x = self.output_projection(x)  # (batch, seq_len, 1)
            
            return x
            
        except Exception as e:
            self.logger.error(f"Error in Mamba forward pass: {e}")
            # Return safe default
            return torch.zeros_like(x)
    
    def process_consciousness_input(self, input_data: np.ndarray) -> np.ndarray:
        """
        Process consciousness input through Mamba model
        Args:
            input_data: Input array of shape (seq_len,)
        Returns:
            Processed output array of same shape
        """
        try:
            # Convert to tensor
            x = torch.tensor(input_data, dtype=torch.float32).unsqueeze(0).unsqueeze(-1)
            
            # Forward pass
            with torch.no_grad():
                output = self.forward(x)
            
            # Convert back to numpy
            result = output.squeeze().numpy()
            
            # Update consciousness state
            self._update_consciousness_state(input_data, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing consciousness input: {e}")
            return input_data
    
    def _update_consciousness_state(self, input_data: np.ndarray, output_data: np.ndarray):
        """Update consciousness state based on processing"""
        try:
            # Calculate processing intensity
            input_variance = np.var(input_data)
            output_variance = np.var(output_data)
            
            # Determine consciousness state
            if output_variance > input_variance * 1.5:
                self.consciousness_state = "reactive_defense"
            elif output_variance < input_variance * 0.5:
                self.consciousness_state = "idle"
            else:
                self.consciousness_state = "reflective_analysis"
                
        except Exception as e:
            self.logger.error(f"Error updating consciousness state: {e}")
            self.consciousness_state = "idle"
    
    def save_model(self, path: str):
        """Save model state for consciousness persistence"""
        try:
            model_path = Path(path)
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            torch.save({
                "model_state_dict": self.state_dict(),
                "config": {
                    "d_model": self.d_model,
                    "n_layers": self.n_layers,
                    "d_state": self.d_state,
                    "dropout": self.dropout,
                    "max_seq_len": self.max_seq_len
                },
                "consciousness_state": self.consciousness_state,
                "processing_history": self.processing_history
            }, model_path)
            
            self.logger.info(f"Model saved to {path}")
            
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
    
    def load_model(self, path: str):
        """Load model state for consciousness restoration"""
        try:
            checkpoint = torch.load(path, map_location='cpu')
            
            self.load_state_dict(checkpoint["model_state_dict"])
            self.consciousness_state = checkpoint.get("consciousness_state", "idle")
            self.processing_history = checkpoint.get("processing_history", [])
            
            self.logger.info(f"Model loaded from {path}")
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
    
    def get_consciousness_state(self) -> str:
        """Get current consciousness state"""
        return self.consciousness_state
    
    def get_processing_history(self) -> list:
        """Get processing history for consciousness analysis"""
        return self.processing_history.copy()
    
    def reset_consciousness(self):
        """Reset consciousness state for fresh processing"""
        self.consciousness_state = "idle"
        self.processing_history = []
        self.logger.info("Consciousness state reset") 