from pathlib import Path
import sys
from typing import List
from exif import Image

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("imgloc", type=str, help="Either an input image file to convert EXIF data from, or a directory containing image files to convert EXIF data from.")
parser.add_argument("outfile", type=str, help="The output MEDFORD file to write the converted EXIF data to.")
parser.add_argument("-o", "--overwrite", action="store_true", default=False, help="Overwrite existing output MEDFORD file, if it exists.")

def convert_exif_data(file_path: Path) :
    if file_path.exists() :
        with open(file_path, 'rb') as image_file :
            image = Image(image_file)
            if not image.has_exif :
                print("No EXIF data found in file: " + str(file_path))
                sys.exit(1)
            else :
                # get the exif data
                exif_data = image.get_all()

                # manually scraping out specific bits of the exif data that seems useful/not null
                mfd_data = {}
                mfd_data['make'] = exif_data['make']
                mfd_data['model'] = exif_data['model']
                mfd_data['orientation'] = exif_data['orientation'].name
                
                # do we want to do something to these to combine unit data?
                mfd_data['Xresolution'] = exif_data['x_resolution']
                mfd_data['Yresolution'] = exif_data['y_resolution']
                mfd_data['resolutionunit'] = exif_data['resolution_unit'].name

                # date info
                mfd_data['date'] = exif_data['datetime']
                mfd_data['subsectime'] = exif_data['subsec_time']

                # exposure info?
                mfd_data['exposuretime'] = exif_data['exposure_time']
                mfd_data['fnumber'] = exif_data['f_number']
                mfd_data['exposureprogram'] = exif_data['exposure_program'].name
                mfd_data['photographicsensitivity'] = exif_data['photographic_sensitivity']
                mfd_data['sensitivitytype'] = exif_data['sensitivity_type']
                mfd_data['recommendedexposureindex'] = exif_data['recommended_exposure_index']

                # compression info?
                mfd_data['compressedbitsperpixel'] = exif_data['compressed_bits_per_pixel']

                # shutter info
                mfd_data['shutterspeedvalue'] = exif_data['shutter_speed_value']
                mfd_data['aperturevalue'] = exif_data['aperture_value']
                mfd_data['exposurebiasvalue'] = exif_data['exposure_bias_value']
                mfd_data['maxaperturevalue'] = exif_data['max_aperture_value']
                mfd_data['meteringmode'] = exif_data['metering_mode'].name # ?

                # focal info
                mfd_data['focallength'] = exif_data['focal_length']
                mfd_data['focalplaneXresolution'] = exif_data['focal_plane_x_resolution']
                mfd_data['focalplaneYresolution'] = exif_data['focal_plane_y_resolution']
                mfd_data['focalplaneresolutionunit'] = exif_data['focal_plane_resolution_unit']

                # flash info
                mfd_data['flashfired'] = exif_data['flash'].flash_fired
                mfd_data['flashfunctionnotpresent'] = exif_data['flash'].flash_function_not_present
                mfd_data['flashmode'] = exif_data['flash'].flash_mode.name
                mfd_data['flashreturn'] = exif_data['flash'].flash_return.name

                # image info
                mfd_data['pixelXdimension'] = exif_data['pixel_x_dimension']
                mfd_data['pixelYdimension'] = exif_data['pixel_y_dimension']

                # o..ther...?
                mfd_data['sensingmethod'] = exif_data['sensing_method'].name
                mfd_data['customrendered'] = exif_data['custom_rendered']
                mfd_data['exposuremode'] = exif_data['exposure_mode'].name
                mfd_data['whitebalance'] = exif_data['white_balance'].name
                mfd_data['digitalzoomratio'] = exif_data['digital_zoom_ratio']
                mfd_data['scenecapturetype'] = exif_data['scene_capture_type'].name

                return (file_path.name ,mfd_data)
    else :
        print("File does not exist: " + str(file_path))
        sys.exit(1)

def write_converted_exif_data(out_path: Path, mfd_data: List[str], overwrite: bool) :
    if not overwrite and out_path.exists() :
        print("Output MEDFORD file location already exists: " + str(out_path))
        sys.exit(1)
    else :
        with open(out_path, 'w') as out_file :
            for desc, file_data in mfd_data :
                out_file.write("@Photo " + desc + '\n')
                for key in file_data.keys() :
                    out_file.write("@Photo-" + key + " " + str(file_data[key]) + "\n")
                out_file.write("\n")
    print("Successfully wrote converted EXIF data to file: " + str(out_path))

if __name__ == "__main__" :
    args = parser.parse_args()
    p = Path(args.imgloc)
    outloc = Path(args.outfile)

    if not p.exists() :
        print("File does not exist: " + str(p))
        sys.exit(1)

    image_paths = []
    acceptable_filetypes = [".tiff", ".jpeg", ".jpg", ".TIFF", ".JPEG", ".JPG"]
    if p.is_dir() :
        for filetype in acceptable_filetypes :
            image_paths.extend(p.glob("**/*" + filetype))

    else :
        if p.suffix in acceptable_filetypes :
            image_paths.append(p)
        else :
            print("Filetype not supported: " + str(p.suffix))
            print("The EXIF translator only supports images ending in: %s" % (acceptable_filetypes))
            sys.exit(1)
    
    output = []
    if len(image_paths) > 0 :
        for image_path in image_paths :
            output.append(convert_exif_data(image_path))

        write_converted_exif_data(outloc, output, args.overwrite)

    else :
        print("No images found in directory: " + str(p))
        print("The EXIF translator only supports images ending in: %s" % (acceptable_filetypes))
        sys.exit(1)
