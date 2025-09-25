# Coupon_Map_Generator #

# >>>>> DESCRIPTION <<<<< #
This Python script generates PDF documentation of PCB coupon maps for manufacturing processes.
It loads configuration from a JSON file with support for site-specific customizations.
The script interfaces with Genesis CAD/CAM software to access panel data and layer information.
It performs validation checks on panels and layers, with fallback mechanisms for missing layers.
The core functionality exports specified layers to PDF with configurable parameters for manufacturing documentation.

# Script Settings:
-> If get issue while print or generated pdf is blank then need update Genesis hooks as below:
   1. ps2pdf
   2. ps_tile