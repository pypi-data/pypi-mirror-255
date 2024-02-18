import numpy as np
from pathlib import Path
from scipy import signal as sg
from scipy import interpolate
import pickle
import functions.output.HDF5_creation as hdf
import functions.yaml.yaml_rw as yml
import functions.photon.photon_gen_image as Image_Gen
import functions.photon.black_body_filter as BB
import functions.noise.noise as N
import functions.timeline.timeline as Tl
import functions.phase.phase_conversion as Ph
import functions.phase.calib_read as Cr
import functions.IQ.IQ_sim as IQ
import functions.photon.sim_image_photon as SI
import functions.photon.rot as Rot
import electronics.filter as Fi
import electronics.data_reading as Re

import image_process.image_generation as IG
import image_process.atmosphere.turbulence as Tf

class PhotonSimulator():
    r"""" Launch the simulation by reading the yaml file and return all the computed information

    Parameter:
    ----------

    Yaml_path: string
        Path to the YAML input file

    Attributes:
    -----------

    TBD

    
    """

    def __init__(self, yaml_path):


        # Reading all config in the yaml
        self.config = yml.read_yaml(yaml_path)
        path = self.config['path']

        if Path(path).exists():
                print('Simulation exist')   # The name given to the simulation is already taken
                self.result = Re.load_dict_from_hdf5(path)
                print('Result in .Result')
        else:
            print('Creating the simulation')
                
            sim_config = self.config['1-Photon_Generation']

            # Method = photon_gen['Method']['method']
            # Exposure_time = photon_gen['Exposition_time']
            # size = photon_gen['Method']['size']
            # detector_dim = [size,size]
            # nb_object = photon_gen['Method']['Nb_object']
            # tel_diam = photon_gen['Method']['Telescope_diameter']
            # distance = (photon_gen['Method']['Object_Distance']['min'],photon_gen['Method']['Object_Distance']['max'])
            # fov_arcsec = photon_gen['fov_arcsec']

            telescope = sim_config['telescope']
            fov_arcsec = telescope['detector']['fov']
            exposure_time = telescope['exposition_time']
            size = int(telescope['detector']['size'])
            detector_dim = [size,size]
            tel_diam = telescope['diameter']
            latitude = telescope['latitude'] * np.pi/180
            obscuration = telescope['obscuration']

            star = sim_config['star']
            nb_object = star['number']
            distance = (star['distance']['min'],star['distance']['max'])
            wavelength_array = np.linspace(star['wavelength_array']['min'],star['wavelength_array']['max'],star['wavelength_array']['nbr'])
            
            sky = sim_config['sky']
            sky_method = sky['method']
            alt = sky['guide']['alt'] * np.pi / 180 
            az = sky['guide']['az'] * np.pi / 180
            contamination = sky['contamination']
            rotation = sky['rotation']

            if sky['fov_method'] == 'fix':
                sky_fov = fov_arcsec
            elif sky['fov_method'] == 'time_dep':
                sky_fov = fov_arcsec * exposure_time   # A revoir !
            else:
                print('sky FOV is not defined')

                
            #   Creation of stars with their spectrum
            self.star_pos,self.star_spec = IG.image_sim(Image_size=int(size/fov_arcsec * sky_fov), object_number=nb_object, distance=distance, Path_file=path,Wavelength=wavelength_array,save = False)

            rot = np.zeros(len(self.star_pos),dtype = object)
            alt_ev = np.zeros(len(self.star_pos),dtype = object)

            #   Rotation effect
            if rotation == True:
                print('Earth rotation effect')
                # lat_tel = photon_gen['Rotation']['tel_latitude'] * np.pi / 180
                # alt = photon_gen['Rotation']['guide_star']['alt'] * np.pi / 180 
                # az = photon_gen['Rotation']['guide_star']['az'] * np.pi / 180
                coo_guide = [alt,az]
                for st in range(len(self.star_pos)):
                    rot[st],alt_ev[st] =Rot.rotation(lat_tel=latitude,coo_guide=coo_guide,coo_star=self.star_pos[st], time = exposure_time,size=size)

            else:
                for st in range(len(self.star_pos)):
                    rot[st] = [interpolate.interp1d([0,exposure_time],[self.star_pos[st][1],self.star_pos[st][1]]),interpolate.interp1d([0,exposure_time],[self.star_pos[st][2],self.star_pos[st][2]])]
                    alt_ev[st] = interpolate.interp1d([0,exposure_time],[np.pi/2,np.pi/2])
                

                    
            try: trans_Path = telescope['transmittance']
            except: trans_Path = False

            #   Creation of photons
            self.photon_list = SI.photon(wavelength_array,self.star_spec,exposure_time,tel_diam,trans_Path)   
                
                #   Point Source Function
            try: sim_config['PSF']
            except:
                print('No PSF -> Point')
                psf_grid = np.zeros(shape = (size,size,len(wavelength_array)))
                psf_grid[int(size/2),int(size/2),:] = 1
                point = np.linspace(0,size,size)
                psf = interpolate.RegularGridInterpolator((point,point,wavelength_array),psf_grid)
                self.psf_visu = psf_grid
            else:
                if sim_config['PSF']['method'] == 'turbulence':
                    turb = sim_config['PSF']
                    nb_pixels_img = size    
                    seeing = turb['seeing']
                    wind = turb['wind']
                    L0 = turb['L0']
                          
                    try: save_link = turb['Path'] 
                    except: save_link = 0
                    if np.shape(wind)==():
                        psf, self.psf_visu = Tf.PSF_creation(fov_arcsec, nb_pixels_img, wavelength_array, seeing, wind, tel_diam, obscuration, L0,exposure_time,save_link)
                    else:
                        coeff = turb['coeff']
                        psf, self.psf_visu = Tf.PSF_creation_mult(fov_arcsec, nb_pixels_img,  wavelength_array, seeing, wind, tel_diam, obscuration, L0,coeff,save_link)
                elif sim_config['PSF']['method'] == 'Download': 
                        file = open(turb['Path'],'rb')
                        psf_file = pickle.load(file)
                        psf = psf_file[0]
                        self.psf_visu = psf_file[1]
                        file.close()


                print('Computing position')
                # Computing position of photon on the PSF 
                self.photon_dict_on_PSF = SI.photon_pos_on_PSF(self.star_pos, self.photon_list, psf, size)

                # Computing position of photon according to the star position and the time
                lam0 = (max(wavelength_array)+min(wavelength_array))/2
                self.photon_dict = SI.photon_proj(self.photon_dict_on_PSF,self.star_pos,rot,alt_ev,size,fov_arcsec,lam0)

                #   Projection of the photon on the detector
                self.wavelength, self.time = SI.detector_scale(detector_dim=detector_dim, photon_dict=self.photon_dict)
            

        

            # Do we want to simulate the phase or IQ ?
            try:self.config['3-Phase']
            except:
                # We don't want to simulate the phase
                try: self.config['3-IQ']
                # We don't want to simulate nor the phase neither IQ
                except: pass
                # We want to simulate IQ
                else:
                    #   NOT UPDATED
                    # Creation of the Timeline
                    point_nb = self.config['2-Timeline']['point_nb']
                    print('Timeline creation')
                    self.photon_timeline = Tl.sorting(exposure_time,self.wavelength,point_nb,self.time) 
                    self.IQ_Compute(obj = '3-IQ')

            else:

                # Creation of the Timeline
                point_nb = self.config['2-Timeline']['point_nb']
                print('Timeline creation')
                self.photon_timeline = Tl.sorting(exposure_time,self.wavelength,point_nb,self.time) 
                self.phase_compute(detector_dim=detector_dim,obj = '3-Phase',timeline=self.photon_timeline, Filter = False)

            try:self.config['4-Electronic']
            except:
                pass
            else:
                wavelength, photon_time = np.zeros(detector_dim,dtype = float), np.zeros(detector_dim, dtype = float)
                photon_timeline = Tl.sorting(exposure_time,wavelength,point_nb,photon_time)
                self.phase_compute(detector_dim=detector_dim,obj = '3-Phase',timeline=photon_timeline, Filter = True)


            if self.config['5-Output']['save'] == 'Simulation':
                print('Saving in HDF5 at: ' + str(path))
                hdf.save_dict_to_hdf5(self.config, path,self,size)

            elif self.config['5-Output']['save'] == 'photon_list':
                print('Saving the photon list at:' +str(path))
                hdf.save_photon_list(path,self.config, self.fil_phase,self.filtered_noise)




    def phase_compute(self, detector_dim, obj, timeline, Filter = False):

            # Reading convertion coeff
            try: self.config[obj]['Conv_wv'] and self.config[obj]['Conv_phase']
            except: 
                try: self.config[obj]['Calib_File']
                except: 
                    Cr.write_csv('Calib.csv',dim = detector_dim, sep = '/')
                    pix,conv_wv,conv_phase = Cr.read_csv('Calib.csv')
                else: pix,conv_wv,conv_phase = Cr.read_csv(self.config[obj]['Calib_File'])

            else:
                pix = []
                conv_wv = []
                conv_phase = []
                for i in range(detector_dim[0]):
                    for j in range(detector_dim[1]):
                        pix.append(str(i)+str(j))
                        conv_wv.append(self.config[obj]['Conv_wv'])
                        conv_phase.append(self.config[obj]['Conv_phase'])
            resolution = self.config[obj]['Resolution']
            decay = self.config[obj]['Decay']
            loc = self.config[obj]['Noise']['loc']
            scale = self.config[obj]['Noise']['scale']
            #Conversion photon to phase
            if Filter == False:
                print('Computing phase')
                self.phase_conversion = Ph.phase_conv(timeline,pix = pix,conv_wv=conv_wv, conv_phase=conv_phase, resolution = resolution)
                
                #Adding exponential
                self.phase_exp = Ph.exp_adding(self.phase_conversion, decay)

                # Adding Noise
                if self.config[obj]['Noise']['type'] == 'Gaussian':
                    phase = np.copy(self.phase_exp)
                    
                    
                    self.phase =  N.gaussian(phase,location=loc,scale=scale)
                elif self.config[obj]['Noise']['type'] == 'Poisson':
                    phase = np.copy(self.phase_exp)
                    self.phase = N.poisson(phase)
                else:
                    pass
            
            elif Filter == True:
                print('Filtering the phase')
                try: self.config['4-Electronic']['Path']
                except: 
                    self.noise = Ph.phase_conv(timeline,pix = pix,conv_wv=conv_wv, conv_phase=conv_phase, resolution = resolution)
                    # Adding Noise
                    if self.config[obj]['Noise']['type'] == 'Gaussian':
                        phase = np.copy(self.noise)
                        self.noise =  N.gaussian(phase,location=loc,scale=scale)
                    elif self.config[obj]['Noise']['type'] == 'Poisson':
                        phase = np.copy(self.noise)
                        self.noise = N.poisson(phase)
                    else:
                        pass
                    # Filter creation

                    nperseg = self.config['4-Electronic']['nperseg']
                    template_time = self.config['4-Electronic']['template_time']
                    trigerinx = self.config['4-Electronic']['trigerinx']
                    point_nb = self.config['4-Electronic']['point_nb']
                    self.psd = Fi.psd(self.noise,nperseg)
                    self.template = Fi.template(self.noise, decay=decay, template_time=template_time, trigerinx=trigerinx,point_nb=point_nb)
                    self.filter = Fi.filter_creation(Noise = self.noise, template=self.template, psd=self.psd)
                    self.filtered_noise = Fi.filtering(self.noise,self.filter)
                    try: self.config['4-Electronic']['save_path']
                    except: pass
                    else:
                        file = open(self.config['4-Electronic']['save_path'], 'wb')
                        pickle.dump([self.filter,self.noise], file)
                        file.close
                else: 
                    file = open(self.config['4-Electronic']['Path'],'rb')
                    self.filter,self.filtered_noise= pickle.load(file)
                    file.close()
 
                self.fil_phase = Fi.filtering(self.phase,self.filter)


     
    
    def IQ_Compute(self,obj):

            try: self.config[obj]['Calib_file_csv']
            except:
                self.IQ_conversion = IQ.photon2IQ_th(self.Photon_Timeline)
            else:
                self.IQ_conversion = IQ.photon2IQ_csv(self.Photon_Timeline, Path = self.config[obj]['Calib_file_csv'])
            Decay = self.config[obj]['Decay']
            self.IQ_exp = IQ.exp_adding(self.IQ_conversion, Decay)
            # Adding Noise
            if self.config[obj]['Noise']['type'] == 'Gaussian':
                    sig = np.copy(self.IQ_exp)
                    loc = self.config[obj]['Noise']['loc']
                    scale = self.config[obj]['Noise']['scale']
                    self.IQ =  [N.gaussian(sig[0],location=loc,scale=scale),N.gaussian(sig[1],location=loc,scale=scale)]
            elif self.config[obj]['Noise']['type'] == 'Poisson':
                    sig = np.copy(self.IQ_exp)
                    self.IQ = [N.poisson(sig[0]),N.poisson(sig[1])]
            else:
                    pass




