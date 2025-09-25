#!/usr/bin/env python3

# Script Name: coupon_map.py
# Version: 1.0 [Initial Release]

# >>>>> DESCRIPTION <<<<< #
# This Python script generates PDF documentation of PCB coupon maps for manufacturing processes.
# It loads configuration from a JSON file with support for site-specific customizations.
# The script interfaces with Genesis CAD/CAM software to access panel data and layer information.
# It performs validation checks on panels and layers, with fallback mechanisms for missing layers.
# The core functionality exports specified layers to PDF with configurable parameters for manufacturing documentation.

# Script Settings:
# - If get issue while print or generated pdf is blank then need update Genesis hooks as below:
#   1. ps2pdf
#   2. ps_tile

# Created by Rahul Suthar on: 16-SEP-2025 For AUT-1209

import os
import sys
import json
from Environment import *
from GenesisStep import GenesisStep
from CustomWidgets import MessageOk
from PyQt5.QtWidgets import QApplication

class CouponMapGenerator:
    def __init__(self, job=JOB, panel_step_name=PANEL_STEP_NAME, site_name=SITE_NAME):
        self.job = job
        self.panel_step_name = panel_step_name
        self.site_name = site_name
        self.panel_step = GenesisStep(job, panel_step_name)
        self.config = None
        
        # For Ensure QApplication is created for GUI components
        if QApplication.instance() is None:
            self.app = QApplication(sys.argv)
    
    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config_coupon_map.json')
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Load default settings
            settings = config['default']
            # Override with site-specific settings if provided
            if self.site_name and self.site_name in config['sites']:
                for key, value in config['sites'][self.site_name].items():
                    settings[key] = value
                    
            self.config = settings
            return settings
        except Exception as e:
            print(f"Error loading configuration: {e}")
            MessageOk(title="Error", text=f"Failed to load configuration file.\n\n{e}\n\nPlease contact Automation Team.", ok_button_text="Abort❌")
            return None
    
    def process_config_variables(self):
        if not self.config:
            return False
            
        # Handle print layer name substitutions
        if self.config["print_lay_name"] == "{TOP_LAYER_NAME}":
            self.config["print_lay_name"] = self.config["print_lay_name"].format(TOP_LAYER_NAME=TOP_LAYER_NAME)
        if self.config["print_lay_name"] == "{BOT_LAYER_NAME}":
            self.config["print_lay_name"] = self.config["print_lay_name"].format(BOT_LAYER_NAME=BOT_LAYER_NAME)

        # Handle output file path substitution
        self.config["print_location"] = self.config["print_location"].format(JOB_PATH=JOB_PATH, cpn_map_pdf_name=self.config["cpn_map_pdf_name"])
        
        return True

    def create_coupon_map_pdf(self):
        """Generate the coupon map PDF based on the configuration."""
        if not self.config:
            return False
        
        # Check if panel step exists
        if not self.panel_step.exists():
            MessageOk(title="Error", text=f"In the job '{self.job}'\n\nPanel step '{self.panel_step_name}' does not exist.\n\nPlease create the panel step first!", ok_button_text="Abort❌")
            return False

        # Check if specified layer exists
        if not self.panel_step.layerExists(self.config["print_lay_name"]):
            MessageOk(title="Error", text=f"In the job '{self.job}'\n\nLayer '{self.config['print_lay_name']}' does not exist in the Matrix.\n\nPrinted with Layer [{TOP_LAYER_NAME}] instead.",ok_button_text="Ok👍")
            self.config["print_lay_name"] = TOP_LAYER_NAME

        # Generate the PDF
        self.panel_step.openEditor(clear=True, zoom_home=True)
        self.panel_step.COM(f'print,title={self.config["print_title"]},layer_name={self.config["print_lay_name"]},mirrored_layers=,draw_profile=yes,drawing_per_layer=yes,label_layers={self.config["label_layers"]},dest=pdf_file,num_copies=1,dest_fname={self.config["print_location"]},paper_size={self.config["paper_size"]},scale_to=0,nx=1,ny=1,orient=none,paper_orient=portrait,paper_width=0,paper_height=0,paper_units=inch,auto_tray=no,top_margin=0.5,bottom_margin=0.5,left_margin=0.5,right_margin=0.5,x_spacing=0,y_spacing=0,color1=990000,color2=9900,color3=99,color4=990099,color5=999900,color6=9999,color7=0')
        self.panel_step.closeEditor(clear=True)
        return True
        
    def run(self):
        """Execute the full coupon map generation process."""
        if not self.load_config():
            return False
            
        if not self.process_config_variables():
            return False
            
        return self.create_coupon_map_pdf()

if __name__ == '__main__':
    # Execution
    generator = CouponMapGenerator()
    generator.run()