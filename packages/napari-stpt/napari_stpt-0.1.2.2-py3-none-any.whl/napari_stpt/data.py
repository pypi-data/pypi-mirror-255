import random
import os
import xarray as xr
import colorsys
import vispy.color
import json
from .utilities import parse_channel_input
import gc
import numpy as np
import math
import SimpleITK as sitk
import pandas as pd

class Data:
    def __init__(self):
        self.ds1 = None
        self.ds2 = None
        self.ds4 = None
        self.ds8 = None
        self.ds16 = None
        self.ds32 = None
        self.old_method = False
        self.spacing = None
        self.bscale = None
        self.bzero = None
        self.align_x = None
        self.align_y = None
        self.corrected_align_x = None
        self.corrected_align_y = None
        self.value_range = None
        self.optical_slices = None
        self.number_of_sections = None
        self.shape = None
        self.slice_spacing = None
        self.corrected_align_x = None
        self.corrected_align_y = None

    def Load2D(self, viewer, image_folder, comboBoxPath, selected_channels, default_contrast_limits, thresholdN, channels_start, axio, old_method, overall_brightness, scroll, scroll_overall_brightness):

    #def Load2D(self, text):
        random.seed(42)


        # Remove previous bounding box
        if any(i.name == 'bounding box' for i in viewer.layers):
            viewer.layers.remove('bounding box')

        file_name = image_folder + str(comboBoxPath) + '/mos'
        default_contrast_limits = [0,30000]
        thresholdN.setText("1000")
        channels_start = 0
        if not os.path.exists(file_name):
            file_name = image_folder + str(comboBoxPath) + '/mos.zarr'
            default_contrast_limits = [0,30]
            thresholdN.setText("0.3")
            channels_start = 1
        print(file_name)

        self.ds1 = xr.open_zarr(file_name)
        self.ds2 = xr.open_zarr(file_name, group='l.2')
        self.ds4 = xr.open_zarr(file_name, group='l.4')
        self.ds8 = xr.open_zarr(file_name, group='l.8')
        self.ds16 = xr.open_zarr(file_name, group='l.16')
        self.ds32 = xr.open_zarr(file_name, group='l.32')

        # Get number of sections
        if axio:
            number_of_sections = len(list(self.ds1))
            self.optical_slices_available = 1
        else:
            if old_method:
                number_of_sections = len(set(self.ds1.attrs['cube_reg']['slice']))
            else:
                try:
                    number_of_sections = int(json.loads(self.ds1.attrs['multiscale'])['metadata']['number_of_sections'])
                except:
                    try:
                        number_of_sections = int(json.loads(self.ds1['S001'].attrs['raw_meta'])['sections'])
                    except:
                        number_of_sections = len(list(self.ds1))


            self.optical_slices_available = len(self.ds1.z)

        print(f"Number of sections: {number_of_sections}")
        print(f"optical slices available: {self.optical_slices_available}")


        channel_names = self.ds1.coords['channel'].values.tolist()
        print(f"channel_names: {channel_names}")



        scroll.setRange(0, (self.optical_slices_available*number_of_sections)-1)
        optical_slice = 0
        scroll.setValue(0)
        z = 0


        if old_method:
            #Old method
            bscale = self.ds1.attrs['bscale']
            bzero = self.ds1.attrs['bzero']

            slice_names = self.ds1.attrs['cube_reg']['slice']

            scroll.setRange(0, len(slice_names)-1)
            if z >= len(slice_names):
                z = len(slice_names)-1
                scroll.setValue(z)

            slice_name = slice_names[z]
        else:
            try:
                bscale = self.ds1['S001'].attrs['bscale']
                bzero = self.ds1['S001'].attrs['bzero']
            except:
                bscale = 1
                bzero = 0
            slice_name = f"S{(z+1):03d}"

        print("slice_name: " + slice_name)
        
        
        # Read the image spacing
        if self.old_method:
            self.spacing = (self.ds1['S001'].attrs['scale'])
        else:
            self.spacing = [1,1]
            try:
                self.spacing[0] = float(json.loads(self.ds1.attrs['multiscale'])['metadata']['scale'][0])
                self.spacing[1] = float(json.loads(self.ds1.attrs['multiscale'])['metadata']['scale'][1])
            except:
                try:
                    self.spacing[0] = float(json.loads(self.ds1['S001'].attrs['scale'])["x"])
                    self.spacing[1] = float(json.loads(self.ds1['S001'].attrs['scale'])["y"])
                except:
                    print("spacing not defined")

        print(f"spacing: {self.spacing}")

        # Parse the selected channels
        #input_string = selected_slices
        #selected_channels = parse_channel_input(input_string)
        print("Selected channels:", selected_channels)

        number_of_channels = len(selected_channels)
        print("Number of channels:", number_of_channels)




        print(selected_channels)
        for chn in range(50):
            if chn in selected_channels:
                #print("loading")


                try:
                    im1 = (self.ds1[slice_name].sel(type='mosaic', z=optical_slice).data[chn] * bscale + bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(type='mosaic', z=optical_slice).data[chn] * bscale + bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(type='mosaic', z=optical_slice).data[chn] * bscale + bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(type='mosaic', z=optical_slice).data[chn] * bscale + bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(type='mosaic', z=optical_slice).data[chn] * bscale + bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(type='mosaic', z=optical_slice).data[chn] * bscale + bzero).squeeze()
                except:
                    try:
                        im1 = (self.ds1[slice_name].sel(z=optical_slice).data[chn] * bscale + bzero).squeeze()
                        im2 = (self.ds2[slice_name].sel(z=optical_slice).data[chn] * bscale + bzero).squeeze()
                        im4 = (self.ds4[slice_name].sel(z=optical_slice).data[chn] * bscale + bzero).squeeze()
                        im8 = (self.ds8[slice_name].sel(z=optical_slice).data[chn] * bscale + bzero).squeeze()
                        im16 = (self.ds16[slice_name].sel(z=optical_slice).data[chn] * bscale + bzero).squeeze()
                        im32 = (self.ds32[slice_name].sel(z=optical_slice).data[chn] * bscale + bzero).squeeze()
                    except:
                        try:
                            im1 = (self.ds1[slice_name].data[chn] * bscale + bzero).squeeze()
                            im2 = (self.ds2[slice_name].data[chn] * bscale + bzero).squeeze()
                            im4 = (self.ds4[slice_name].data[chn] * bscale + bzero).squeeze()
                            im8 = (self.ds8[slice_name].data[chn] * bscale + bzero).squeeze()
                            im16 = (self.ds16[slice_name].data[chn] * bscale + bzero).squeeze()
                            im32 = (self.ds32[slice_name].data[chn] * bscale + bzero).squeeze()
                        except:
                            print("skipping this channel since it can't be read")
                            continue


                if chn==0:
                    color_map='bop purple'
                elif chn==1:
                    color_map='red'
                elif chn==2:
                    color_map='green'
                elif chn==3:
                    color_map='blue'
                elif chn==4:
                    color_map='yellow'
                elif chn==5:
                    color_map='magenta'
                elif chn==6:
                    color_map='cyan'
                elif chn==7:
                    color_map='bop orange'
                elif chn==8:
                    color_map='bop blue'
                elif chn==9:
                    color_map='bop purple'
                else:
                    # Generate a random hue value between 0 and 1 (representing the entire spectrum)
                    random_hue = random.uniform(0, 1)

                    # Convert the hue value to an RGB color
                    rgb_color = colorsys.hsv_to_rgb(random_hue, 1, 1)

                    color_map= vispy.color.Colormap([[0.0, 0.0, 0.0], [rgb_color[0], rgb_color[1], rgb_color[2]]])

                channel_name = str(channel_names[chn])

                if any(i.name == channel_name for i in viewer.layers):
                    viewer.layers.remove(channel_name)



                min_value = im32.min().compute()
                if min_value < 0:
                    min_value = 0
                max_value = im32.max().compute()

                self.value_range = [min_value, max_value]
                
                self.overall_brightness = number_of_channels * (1.01 - (float(scroll_overall_brightness.value()) / 1000))
                contrast_limits = [self.value_range[0],self.value_range[1]*self.overall_brightness]

                
                
                if "IMC" in channel_name:
                    contrast_limits = [0,300*overall_brightness]
                elif "AXIO" in channel_name:
                    contrast_limits = [0,30000*overall_brightness]
                elif "STPT" in channel_name:
                    contrast_limits = [0,30000*overall_brightness]
                else:
                    contrast_limits = [0,30000*overall_brightness]

                layerC1 = viewer.add_image([im1, im2, im4, im8, im16, im32], multiscale=True,
                                      name=str(channel_name), blending='additive', colormap=color_map, contrast_limits=contrast_limits, scale=self.spacing)



        return self.optical_slices_available, self.value_range, number_of_sections
                
       

    def Align(self, volume, resolution, output_resolution, start_slice_number, current_spacing):
        sample_name = "20220818_MPR_BalbC_4T1_Zsg_lung_C_D_132_100x20um"
        
        print("------------------------------------------------------------------------")
        print(f"spacing({self.spacing[0]}, {self.spacing[1]})")
        size_multiplier = (resolution*0.1*self.spacing[0])/output_resolution
        size = (volume.shape[0], int(size_multiplier*volume.shape[1]), int(size_multiplier*volume.shape[2]))
        aligned = np.zeros(size, dtype=np.float32)
        size2D = (int(size_multiplier*volume.shape[2]), int(size_multiplier*volume.shape[1]))

        z_size = volume.shape[0]
        
        for z in range(0, z_size):

            fixed = sitk.GetImageFromArray(volume[z, :, :])
            fixed.SetOrigin((0, 0))
            fixed.SetSpacing([resolution*0.1*current_spacing[1],resolution*0.1*current_spacing[0]])

            transform = sitk.Euler2DTransform()
            
            
            slice_name_stpt = f"S{(z+1):03d}"
            home_directory = os.path.expanduser('~')
            file_path = home_directory + f"/Storage/imaxt/imaxt_reg/{sample_name}/{sample_name}_INT_STPT_STPT_all_reg.parquet"
            
#             internal_df_stpt = pd.read_parquet(file_path, engine='pyarrow')
#             internal_filtered_df_stpt = internal_df_stpt[(internal_df_stpt['ranking'] == 1) & ((internal_df_stpt['FLAG'] == 1) | (internal_df_stpt['FLAG'] == 0))]
#             internal_row_stpt = internal_filtered_df_stpt[internal_filtered_df_stpt['S_S'] == slice_name_stpt]
#             M = np.array([[internal_row_stpt.iloc[0, 24], internal_row_stpt.iloc[0, 25], internal_row_stpt.iloc[0, 26]], [internal_row_stpt.iloc[0, 27], internal_row_stpt.iloc[0, 28], internal_row_stpt.iloc[0, 29]]])

#             print(M)
            
            align_pos = z + start_slice_number
            alignY = 0
            if not np.isnan(self.corrected_align_y[align_pos]):
                alignY = -self.corrected_align_y[align_pos]*0.1*current_spacing[1]

            alignX = 0
            if not np.isnan(self.corrected_align_x[align_pos]):
                alignX = -self.corrected_align_x[align_pos]*0.1*current_spacing[0]

            transform.SetTranslation([alignY, alignX])


            resampler = sitk.ResampleImageFilter()
            resampler.SetSize(size2D)
            resampler.SetOutputSpacing([output_resolution, output_resolution])
            resampler.SetOutputOrigin((0, 0))
            resampler.SetInterpolator(sitk.sitkLinear)
            resampler.SetDefaultPixelValue(0)
            resampler.SetTransform(transform)

            out = resampler.Execute(fixed)

            np_out = sitk.GetArrayFromImage(out)
            aligned[z, :, :] = np_out

        return aligned.astype(dtype=np.float32)

         
                
                
    def AlignAXIO(axio_volume, sample_name, slice_names, resolution, channel):

        sample_name = sample_name[:-5]

        new_volume = np.zeros(axio_volume.shape)

        # df = pd.read_parquet(f"/home/tristan/Shared/imaxt_reg/{sample_name}/{sample_name}_EXT_AXIO_STPT_all_reg.parquet", engine='pyarrow')
        df = pd.read_parquet(f"/storage/imaxt/imaxt_reg/{sample_name}/{sample_name}_EXT_AXIO_STPT_all_reg.parquet", engine='pyarrow')


        filtered_df = df[(df['ranking'] == 1) & ((df['FLAG'] == 1) | (df['FLAG'] == 0))]
        #filtered_df = df[(df['ranking'] == 1)]

        print(slice_names)

        axio_zoom = xr.open_zarr(f"/storage/processed.2022/axio/{sample_name}_Axio/mos", group='l.{0:d}'.format(resolution))

        for index, slice_name in enumerate(slice_names):

            row = filtered_df[filtered_df['D_S'] == slice_name]

            if not row.empty:

                axio_location = int(row.iloc[0, 4][1:]) - 1
                # print(row.iloc[0, 4])
                # print(axio_location)
                # print(row)
                # print(" ")

                axio_image = axio_zoom[slice_name].sel(channel=channel).data
                axio_image = axio_image.squeeze()

                #axio_image = axio_volume[index,:,:]

                #flip image
                if row.iloc[0, 8] == 0.0:
                    axio_image = axio_image[::-1,:]

                axio_image = np.asarray(axio_image)

                M = np.array([[row.iloc[0, 24], row.iloc[0, 25], row.iloc[0, 26]/resolution], [row.iloc[0, 27], row.iloc[0, 28], row.iloc[0, 29]/resolution]])
                # Expand the dimensions of M so that it can be multiplied by T.
                M = np.append(M, [[0, 0, 0]], axis=0)

                rows, cols = axio_image.shape
                affine_np_img = cv2.warpAffine(axio_image, M[:2,:], (cols, rows))
                if (axio_location < new_volume.shape[0]):
                    new_volume[axio_location,:,:] = affine_np_img


        return new_volume   
                

    def Load3D(self, viewer, image_folder, comboBoxPath, selected_channels, default_contrast_limits, thresholdN, channels_start, axio, old_method, overall_brightness, scroll, scroll_overall_brightness, pixel_size, m_slice_spacing, start_slice, end_slice, crop, crop_start_x, crop_end_x, crop_start_y, crop_end_y):
        random.seed(42)
        
        verbose = True

        

        # Clear memory
        gc.collect()


                  
        if verbose:
            print(f"folder location: " + image_folder)
            
        
        file_name = image_folder + str(comboBoxPath) + '/mos'
        default_contrast_limits = [0,30000]
        thresholdN.setText("1000")
        channels_start = 0
        if not os.path.exists(file_name):
            file_name = image_folder + str(comboBoxPath) + '/mos.zarr'
            default_contrast_limits = [0,30]
            thresholdN.setText("0.3")
            channels_start = 1
        print(file_name)

        # Try to read only the meta data using the consolidated flag as True
        # Currently not used
        try:
            self.ds1 = xr.open_zarr(file_name, consolidated=False)
            # print("not trying consolidated")
        except Exception:
            print("none-consolidated")
            self.ds1 = xr.open_zarr(file_name)
            
            
            
        channel_names = self.ds1.coords['channel'].values.tolist()
        print(f"channel_names: {channel_names}")

        
        
        # Read the image spacing
        if self.old_method:
            self.spacing = (self.ds1['S001'].attrs['scale'])
        else:
            self.spacing = [1,1]
            try:
                self.spacing[0] = float(json.loads(self.ds1.attrs['multiscale'])['metadata']['scale'][0])
                self.spacing[1] = float(json.loads(self.ds1.attrs['multiscale'])['metadata']['scale'][1])
            except:
                try:
                    self.spacing[0] = 10 * float(json.loads(self.ds1['S001'].attrs['scale'])["x"])
                    self.spacing[1] = 10 * float(json.loads(self.ds1['S001'].attrs['scale'])["y"])
                    # self.spacing[2] = 10 * float(json.loads(self.ds1['S001'].attrs['scale'])["z"])
                except:
                    print("spacing not defined")
                

            
            
                
        if verbose:
            print(f"spacing ({self.spacing[0]}, {self.spacing[1]})")

        # Read the parameters to convert the voxel values (bscale and bzero)
        if self.old_method:
            self.bscale = self.ds1.attrs['bscale']
            self.bzero = self.ds1.attrs['bzero']
        else:
            try:
                self.bscale = self.ds1['S001'].attrs['bscale']
                self.bzero = self.ds1['S001'].attrs['bzero']
            except:
                self.bscale = 1
                self.bzero = 0

        if verbose:
            print(f"bscale {self.bscale}, bzero {self.bzero}")


        # Get number of sections
        if axio:
            self.number_of_sections = len(list(self.ds1))

        
        self.number_of_sections = len(list(self.ds1))
        if verbose:
            print(f"Number of sections: {self.number_of_sections}")
            

        # Read the translation values
        if self.old_method:
            self.align_x = self.ds1.attrs['cube_reg']['abs_dx']
            self.align_y = self.ds1.attrs['cube_reg']['abs_dy']
        else:
            self.align_x = []
            self.align_y = []

            for z in range(0, self.number_of_sections):
                # slice_name = f"S{(z+1):03d}"
                # self.align_x.append(self.ds1[slice_name].attrs['offsets']['x'])
                # self.align_y.append(self.ds1[slice_name].attrs['offsets']['y'])
                self.align_x.append(0)
                self.align_y.append(0)

        if verbose:
            print(f"align_x {self.align_x}")
            print(f"align_y {self.align_y}")
        

        # User defined output pixel size
        output_resolution = float(pixel_size)

        if verbose:
            print(f"output pixel size {output_resolution}")


        # Calculate at which resolution the image should be read based on the image spacing and output pixel size
        resolution = 32
        index = 5
        if (output_resolution / 0.5) < 32:
            resolution = 16
            index = 4
        if (output_resolution / 0.5) < 16:
            resolution = 8
            index = 3
        if (output_resolution / 0.5) < 8:
            resolution = 4
            index = 2
        if (output_resolution / 0.5) < 4:
            resolution = 2
            index = 1
        if (output_resolution / 0.5) < 2:
            resolution = 1
            index = 0

        if verbose:
            print(f"loading at resolution {resolution} with index {index}")
        

        # Open the image file
        # if axio:
        #     ds = xr.open_zarr(file_name, group='l.{0:d}'.format(resolution))
        # else:
        #     if self.old_method:
        #         gr = self.ds1.attrs["multiscale"]['datasets'][index]['path']
        #         ds = xr.open_zarr(file_name, group=gr)
        #     else:
        #         gr = json.loads(self.ds1.attrs["multiscale"])['datasets'][index]['path']
        #         ds = xr.open_zarr(file_name, group=gr)


        try:
            gr = self.ds1.attrs["multiscale"]['datasets'][index]['path']
            ds = xr.open_zarr(file_name, group=gr)
        except:
            try:
                gr = json.loads(self.ds1.attrs["multiscale"])['datasets'][index]['path']
                ds = xr.open_zarr(file_name, group=gr)
            except:
                ds = xr.open_zarr(file_name, group='l.{0:d}'.format(resolution))

                
        # Get the number of optical slices that are available
        if axio:
            self.optical_slices_available = 1
        else:
            self.optical_slices_available = len(ds.z)

        if verbose:
            print(f"optical slices available: {self.optical_slices_available}")
        
        # Slice spacing given by the user, which should be extracted from the file name
        self.slice_spacing = float(m_slice_spacing)

        # Get the optical slice spacing
        if self.old_method or axio:
            # assume that the optical slices do not overlap
            optical_section_spacing = self.slice_spacing / self.optical_slices_available
        else:
            try:
                optical_section_spacing = float(json.loads(self.ds1.attrs['multiscale'])['metadata']['optical_section_spacing'])
            except:
                try:
                    optical_section_spacing = float(json.loads(self.ds1['S001'].attrs['raw_meta'])['zres'])
                except:
                    optical_section_spacing = 1


        if verbose:
            print(f"optical_slices zres: {optical_section_spacing}")


        # Calculate how many optical slices to use
        if self.optical_slices_available > 1:
            expected_nr_of_slices = round(self.slice_spacing / optical_section_spacing)
            if self.optical_slices_available > expected_nr_of_slices:
                self.optical_slices = expected_nr_of_slices
            else:
                self.optical_slices = self.optical_slices_available
        else:
            self.optical_slices = 1


        # Get slice names
        if self.old_method:
            self.slice_names = self.ds1.attrs['cube_reg']['slice']
        else:
            self.slice_names = []
            for z in range(0, self.number_of_sections):
                slice_name = f"S{(z+1):03d}"
                for i in range(0, self.optical_slices):
                    self.slice_names.append(slice_name)
        
        if verbose:
            print(f"slice names: {self.slice_names}")


        if verbose:
            print(f"number of optical slices used: {self.optical_slices}")

        # Make copies of the translations for all the optical slices used
        if self.old_method:
            self.corrected_align_x = self.align_x
            self.corrected_align_y = self.align_y
        else:
            self.corrected_align_x = []
            for index, value in enumerate(self.align_x):
                for i in range(0,self.optical_slices):
                    self.corrected_align_x.append(value)

            self.corrected_align_y = []
            for index, value in enumerate(self.align_y):
                for i in range(0,self.optical_slices):
                    self.corrected_align_y.append(value)


        if verbose:
            print(f"There are {len(self.corrected_align_x)} translations")

        # Set perspective view which aids the navigation
        viewer.window.qt_viewer.camera._3D_camera.fov = 45

        # Store the output resolution in which this volume was loaded
        self.current_output_resolution = float(pixel_size)

        # Define start slice
        if start_slice == "":
            start_slice_number = 0
            chop_bottom = 0
        else:
            start_slice_number = int(math.floor(float(start_slice)/float(self.optical_slices)))
            chop_bottom = int(start_slice) - (self.optical_slices * start_slice_number) 

        # Define end slice
        if end_slice == "":
            end_slice_number = self.number_of_sections-1
            chop_top = 0
        else:
            end_slice_number = int(math.floor(float(end_slice)/float(self.optical_slices)))
            chop_top = (self.optical_slices * (end_slice_number + 1) -1) - int(end_slice) 

        # Define number of slices
        number_of_slices = end_slice_number - start_slice_number + 1
        if verbose:
            print(f"number_of_slices {number_of_slices}")
            
            
        # Parse the selected channels
        # selected_channels = parse_channel_input(selected_slices)
        if verbose:
            print("Selected channels:", selected_channels)
            
        number_of_channels = len(selected_channels)
        if verbose:
            print("Number of channels:", number_of_channels)

        spacing_loaded = [float(self.slice_spacing)/float(self.optical_slices), output_resolution, output_resolution]

        for chn in range(50):
            if chn in selected_channels:
                print(f"loading channel {chn}")
                
                if axio:
                    try:
                        volume_1_temp = (ds.sel(type='mosaic').to_array(
                        ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                        volume_1_temp = volume_1_temp[:,chn,:,:]
                    except Exception as e:
                        if verbose:
                            print("An error occurred:", str(e))
                        volume_1_temp = (ds.to_array(
                        ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                        volume_1_temp = volume_1_temp[:,chn,:,:]
                else:
                    try:
                        volume_1_temp = (ds.sel(type='mosaic', z=0).to_array(
                        ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                        volume_1_temp = volume_1_temp[:,chn,:,:]
                    except Exception as e:
                        if verbose:
                            print("An error occurred:", str(e))
                        try:
                            volume_1_temp = (ds.sel(z=0).to_array(
                            ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                            volume_1_temp = volume_1_temp[:,chn,:,:]
                        except Exception as e:
                            if verbose:
                                print("An error occurred:", str(e))
                            print("skipping this channel since it can't be read")
                            continue

                

                if crop:
                    spacing_x = resolution*0.1*self.spacing[0]
                    spacing_y = resolution*0.1*self.spacing[1]

                    size_y = int(math.floor((crop_end_x - crop_start_x) / spacing_x))
                    size_z = int(math.floor((crop_end_y - crop_start_y) / spacing_y))
                    start_y = int(math.floor(crop_start_x / spacing_x))
                    start_z = int(math.floor(crop_start_y / spacing_y))
                else:
                    if axio:
                        size_y = int(math.floor(volume_1_temp.shape[2]))
                        size_z = int(math.floor(volume_1_temp.shape[3]))
                    else:
                        size_y = int(math.floor(volume_1_temp.shape[1]))
                        size_z = int(math.floor(volume_1_temp.shape[2]))
                    start_y = 0
                    start_z = 0

                volume_1 = np.zeros((self.optical_slices*number_of_slices, size_y, size_z), dtype=np.float32)

                if number_of_slices != volume_1_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z].shape[0]:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("One or more slices appear to be missing")
                    msg.setInformativeText("Find the missing slice(s) by using the Load slice function and " \
    "scrolling through the slices until an error message is displayed. " \
    "Then set a Slices range to avoid this slice.")
                    msg.setWindowTitle("Error")
                    msg.setStandardButtons(QMessageBox.Ok)
                    retval = msg.exec_()
                    return

                volume_1[0::self.optical_slices, :, :] = volume_1_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z]

                for optical_slice in range(1, self.optical_slices):
                    try:
                        volume_1_temp = (ds.sel(channel=channels_start, type='mosaic', z=optical_slice).to_array(
                        ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                    except:
                        volume_1_temp = (ds.sel(channel=channels_start, z=optical_slice).to_array(
                        ).data * self.bscale + self.bzero).astype(dtype=np.float32)

                    volume_1[optical_slice::self.optical_slices, :, :] = volume_1_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z]

                    
                    
                    
                # Normalize the brightness changes between optical sections
                # if self.cb_correct_brightness_optical_section.isChecked():
                #     print("correcting brightness of optical sections C1")
                #     self.Normalize_slices(volume_1, self.optical_slices)

                print("aligning")
                aligned_1 = self.Align(volume_1, resolution, output_resolution, start_slice_number*self.optical_slices, self.spacing)
                #aligned_1 = volume_1

                aligned_1 = aligned_1[chop_bottom:aligned_1.shape[0]-chop_top,:,:]
                self.shape = aligned_1.shape

                if verbose:
                    print(f"self.shape {self.shape}")

                if chn==0:
                    color_map='bop purple'
                elif chn==1:
                    color_map='red'
                elif chn==2:
                    color_map='green'
                elif chn==3:
                    color_map='blue'
                elif chn==4:
                    color_map='yellow'
                elif chn==5:
                    color_map='magenta'
                elif chn==6:
                    color_map='cyan'
                elif chn==7:
                    color_map='bop orange'
                elif chn==8:
                    color_map='bop blue'
                elif chn==9:
                    color_map='bop purple'
                else:
                    # Generate a random hue value between 0 and 1 (representing the entire spectrum)
                    random_hue = random.uniform(0, 1)

                    # Convert the hue value to an RGB color
                    rgb_color = colorsys.hsv_to_rgb(random_hue, 1, 1)

                    color_map= vispy.color.Colormap([[0.0, 0.0, 0.0], [rgb_color[0], rgb_color[1], rgb_color[2]]])

                channel_name = channel_names[chn]

                if any(i.name == channel_name for i in viewer.layers):
                    viewer.layers.remove(channel_name)
                    
                
                min_value = volume_1.min()
                if min_value < 0:
                    min_value = 0
                max_value = volume_1.max()
                
                self.value_range = [min_value, max_value]
                
                self.overall_brightness = number_of_channels * (1.01 - (float(scroll_overall_brightness.value()) / 1000))
                contrast_limits = [self.value_range[0],self.value_range[1]*self.overall_brightness]
                

                # viewer.add_image([aligned_1], name=channel_name, scale=(float(self.slice_spacing)/float(self.optical_slices) / output_resolution, 1, 1), 
                #                       blending='additive', colormap=color_map, contrast_limits=contrast_limits, scale=self.spacing)

                viewer.add_image([aligned_1], name=channel_name, scale=(float(self.slice_spacing)/float(self.optical_slices), output_resolution, output_resolution), 
                                      blending='additive', colormap=color_map, contrast_limits=contrast_limits)



        

        
        return self.optical_slices_available, self.value_range
    
    
    
    
