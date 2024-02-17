import numpy as np
import pandas as pd
import os
import warnings
# from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
# from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score

class rhessys_calibrater:
    
    def __init__(self, template, para_dic=None):
        # Work_dir: path of the rhessys model
        if para_dic is None:
            self.para_dic = {'gw1':(0.001,0.2),
                             'gw2':(0.001,0.2),
                             'gw3':(0.001,0.2),
                             's1':(0.001,20),
                             's2':(0.1,300.0),
                             's3':(0.1,20),
                             'sv1':(0.001,20),
                             'sv2':(0.1,300.0),
                             'svalt1':(0.5,2),
                             'svalt2':(0.5,2),
                            # 'snowEs ':(0.5,2),
                            # 'snowTs ':(0.5,2)
                               }
        else:
            self.para_dic = para_dic
        
        template = pd.read_csv(template)
        self.workdir = template['Value'][template['augName']=='workDir'].values[0]
        self.outputCsvName = template['Value'][template['augName']=='outputCsvName'].values[0]
        self.round = template['Value'][template['augName']=='round'].values[0]
        self.numParamSet = int(template['Value'][template['augName']=='numParamSet'].values[0])
        self.rhessysExecutable = template['Value'][template['augName']=='rhessysExecutable'].values[0]
        self.startDate = template['Value'][template['augName']=='startDate'].values[0]
        self.endDate = template['Value'][template['augName']=='endDate'].values[0]
        self.worldfile = template['Value'][template['augName']=='worldfile'].values[0]
        self.flowtable = template['Value'][template['augName']=='flowtable'].values[0]
        self.tecfile = template['Value'][template['augName']=='tecfile'].values[0]
        self.outputPrefix = template['Value'][template['augName']=='outputPrefix'].values[0]
        self.options = template['Value'][template['augName']=='options'].values[0]

        ## Param setting for HPC, slurm system
        self.userHPC = template['Value'][template['augName']=='userHPC'].values[0]
        self.allocationHPC = template['Value'][template['augName']=='allocationHPC'].values[0]
        self.memSize = template['Value'][template['augName']=='memSize'].values[0]
        self.timeHPC = template['Value'][template['augName']=='timeHPC'].values[0]
        self.randomSeed = int(template['Value'][template['augName']=='randomSeed'].values[0])
        
        if os.path.exists(self.workdir):
            print(f'RHESSys calibrater is setup at {self.workdir}\n')
        else:
            raise Exception(f'The RHESSys folder {self.workdir} does not exist.\n')
            
        
            
        if not os.path.exists(os.path.join(self.workdir, 'output_calibration')):
            os.mkdir(os.path.join(self.workdir, 'output_calibration'))
            print('"output_calibration" is created (to store RHESSys calibration output)\n')
        else:
            print("output_calibration folder already exists.")
            
        if not os.path.exists(os.path.join(self.workdir, 'jobfiles_calibration')):
            os.mkdir(os.path.join(self.workdir, 'jobfiles_calibration'))
            print('"jobfiles_calibration" is created (to store temporary job files)\n')
        else:
            print("jobfiles folder already exists.\n")
            
        self.output_folder = 'output_calibration'
        self.jobfiles_folder = 'jobfiles_calibration'
        self.lines = []
    
    def UniformSample(self):
        ##########
        ## Sample from uniform distribution for each parameter, mainly used for the
        ##     first round of RHESSys calibration
        ## Inputs:
        ##     1. para_dic: dictionary of parameters, in format of {par_name: [min, max]}
        ##     2. out_path: output file name, saved to RHESSys model folder
        ##     3. num_set: number of sets of parameters, default=1000
        ##########
        # Optional: Set a random seed to make results reproducable
        np.random.seed(self.randomSeed)
        
        # 1. Draw samples for each parameter and save to a DataFrame
        pd.DataFrame({name:np.random.uniform(self.para_dic[name][0],self.para_dic[name][1],self.numParamSet).round(5) for name in self.para_dic.keys()}).to_csv(
                   os.path.join(self.workdir,f'{self.outputCsvName}_round{self.round}.csv'), index_label='index')
        print(f'Generating {self.numParamSet} parameter sets, saved at\n',os.path.join(self.workdir,f'{self.outputCsvName}_round{self.round}.csv\n'))
        
        # 2. Save the csv file storing parameter sets for future use
        #  df.to_csv(out_filename, index_label='index')
    
    def Para_cmd(self, out_txt=None):
        ##########
        ## Optional:
        ##    1. out_txt: path to write out parameter command line as txt
        ## Return:
        ##     a list of lines for parameters
        ##########

        # Step 1: Read parameter file
        paras = pd.read_csv(os.path.join(self.workdir,f'{self.outputCsvName}_round{self.round}.csv'))

        # Step 2: Create job script file for each line in the parameter file
        for idx in range(len(paras)):
        # for idx in range(1):
            cmd_line = ''

            para_line = paras.loc[idx]

            para_name = []
            # for i in range(len(para_line)):
            #     if para_line.index[i] == 'index':
            #         continue

            #     if para_line.index[i][:-1] not in para_name:
            #         cmd_line += '-{} {} '.format(para_line.index[i][:-1], para_line[i])
            #         para_name.append(para_line.index[i][:-1])
            #     else:
            #         cmd_line += str(para_line[i]) + ' '

            for i in range(len(para_line)):
                if para_line.index[i] == 'index':
                    continue

                if para_line.index[i][:-1] not in para_name:
                    cmd_line += '-{} {} '.format(para_line.index[i][:-1], para_line.iloc[i])
                    para_name.append(para_line.index[i][:-1])
                else:
                    cmd_line += str(para_line.iloc[i]) + ' '

            self.lines.append(cmd_line[:-1])
        
        # Steo 3: Optional. Write out a txt file for command lines of parameters
        if out_txt is not None:
            with open(os.path.join(self.workdir, out_txt), 'w') as f:
                f.writelines(i+'\n' for i in self.lines)

    
    def JobScripts(self, submit=False):
        ############
        ## Function to create the job file for RHESSys submission
        ##     ** Recommend to define work_dir as the model directory **
        ##     ** and define other variables in "relative" path ** 
        ##     Arguments:
        ##     1. para_cmd_line: the command lines (strings) for parameters only
        ##     2. job_files: folder path to store all job files
        ##     3. work_dir: work directory for the RHESSys project
        ##     4. rhessys_executable: full path of the rhessys executable
        ##     5. st_date, ed_date: start and end date of simulation, format as 'YEAR MONTH DAY HOUR'
        ##     6. worldfile: path of worldfile, recommend to save under work_dir
        ##     7. flowtable: path of TWO flow tables, sub and surf flow
        ##     8. tecfile: tecfile path
        ##     9. options: options/flags for RHESSys (e.g., -g for growth mode, -b for basin output)
        ##     10. output_dir: folder for saving output files
        ##     11. output_prefix: prefix of output files
        ##
        ############
        
       #  cur_dir = os.getcwd()

        if len(self.lines) == 0:
            self.Para_cmd()

            if len(self.lines) == 0:
                raise Exception('No parameters were generated for calibration. Create the object and run "UniformSample" and "Para_cmd" before this.')
        
        if len(self.lines) < self.numParamSet:
            raise Exception('Number of command lines {} not match the setup {} parameter sets, double check'.format(len(self.lines), self.numParamSet))
        
        count = 0
        for idx, line in enumerate(self.lines):
            # Set the idx starts at 1, not 0
            idx = idx + 1
            job_path = f'{self.workdir}/jobfiles/job_{idx}.job'
            with open(job_path,'w') as f:
                f.writelines('#!/bin/bash\n')
                f.writelines('#SBATCH --partition=standard\n')
                f.writelines('#SBATCH --ntasks=1\n')
                f.writelines(f'#SBATCH --mem={self.memSize}\n')
                f.writelines(f'#SBATCH -t {self.timeHPC}\n')   # Change if simulation takes more than 10 hours
                f.writelines('#SBATCH --output=/dev/null\n')
                f.writelines('#SBATCH --error=/dev/null\n')
                f.writelines(f'#SBATCH --job-name=rs{idx}\n')
                f.writelines(f'#SBATCH -A {self.allocationHPC}\n')
                # f.writelines(f'#SBATCH --mail-user={computing_id}@virginia.edu\n')
                # f.writelines(f'#SBATCH --mail-type=END\n')

                f.writelines('module purge\n')
                f.writelines('module load singularity\n')

                f.writelines(f'cd {self.workdir}\n')


                f.writelines(f'{self.rhessysExecutable} -st {self.startDate} -ed {self.endDate} {self.options} '+
                            f'-t {self.tecfile} -w {self.worldfile} -whdr {self.worldfile}.hdr ' +
                            f'-r {self.flowtable} -pre {self.output_folder}/{self.outputPrefix}{idx} ')

                f.writelines(line)
            count += 1

            if submit:
                os.system(f"sbatch {job_path}")
                print(f'Simulation {idx} is submitted.', end='\r')
        
        print(f'{count} jobfiles are successfully generated and saved to {self.workdir}/jobfiles_calibration.\n')

class rhessys_cluster:
    
    def __init__(self, 
                template
                ):
        self.template_path = template
        template = pd.read_csv(template)
        self.template = template
        self.workdir = template['Value'][template['augName']=='workDir'].values[0]
        self.outputCsvName = template['Value'][template['augName']=='outputCsvName'].values[0]
        self.round = template['Value'][template['augName']=='round'].values[0]
        self.numParamSet = int(template['Value'][template['augName']=='numParamSet'].values[0])
        self.rhessysExecutable = template['Value'][template['augName']=='rhessysExecutable'].values[0]
        self.startDate = template['Value'][template['augName']=='startDate'].values[0]
        self.endDate = template['Value'][template['augName']=='endDate'].values[0]
        self.worldfile = template['Value'][template['augName']=='worldfile'].values[0]
        self.flowtable = template['Value'][template['augName']=='flowtable'].values[0]
        self.tecfile = template['Value'][template['augName']=='tecfile'].values[0]
        self.outputPrefix = template['Value'][template['augName']=='outputPrefix'].values[0]
        self.options = template['Value'][template['augName']=='options'].values[0]

        ## Param setting for HPC, slurm system
        self.userHPC = template['Value'][template['augName']=='userHPC'].values[0]
        self.allocationHPC = template['Value'][template['augName']=='allocationHPC'].values[0]
        self.memSize = template['Value'][template['augName']=='memSize'].values[0]
        self.timeHPC = template['Value'][template['augName']=='timeHPC'].values[0]
        self.randomSeed = int(template['Value'][template['augName']=='randomSeed'].values[0])

        self.output_folder = 'output_calibration'
        self.jobfiles_folder = 'jobfiles_calibration'
        
        target_file = os.path.join(self.workdir,f'{self.outputCsvName}_round{self.round}.csv')
        print(target_file)

        try:
            self.analyzing_param = pd.read_csv(target_file)
        except:
            raise Exception(f"Can't find parameters from {target_file}\nPlease check the setting in your template file.")
        
        self.new_param = None
        self.new_lines = []

        print("Found {} sets of parameters".format(len(self.analyzing_param)))

        output_len = len(list(set([i.split('_')[0] for i in os.listdir(os.path.join(self.workdir, self.output_folder))])))

        if output_len != len(self.analyzing_param):
            warnings.warn('Found {} parameter sets in csv file, but not match {} simulations in output_calibration folder'.format(len(self.analyzing_param), output_len))
        else:
            print('Parameter analyzing is ready for:')
        
        self.param_names = [i for i in self.analyzing_param.columns if i != 'index']
        print(', '.join(self.param_names)+'.',len(self.param_names), 'in total.')
    
    def objective_analysis(self, 
                           observation_file,   # Have to be in csv format
                           date_field,
                           Q_field,
                           period,
                           obj_funs=['NSE','rmse','r2'],
                           cols = ['laiTREE', 'gw.storage']):

        # 1. Read observation data, with datetime as index
        observ = pd.read_csv(observation_file)
        observ.index = pd.to_datetime(observ[date_field])

        # 3. Create columns for each objective functions
        for name in obj_funs: self.analyzing_param[name] = np.nan 
        for name in cols: self.analyzing_param[name] = np.nan 

        for idx in range(1, len(self.analyzing_param) + 1):
            try:
                pred = pd.read_csv(f'{self.output_folder}/{self.outputPrefix}{idx}_basin.daily', sep=' ')  # use basin daily file to calibrate
            except:
                print(f'Simulation {idx} failed.')
                continue
            
            if len(pred) == 0:
                print(f'Simulation {idx} was corrupted. Skipped...')
            else:
                print(f'Analyzing {idx}', end="\r")
                pred.index = pd.to_datetime(pred['year'].astype(str)+'-'+pred['month'].astype(str)+'-'+pred['day'].astype(str),format='%Y-%m-%d')
                
                # pred = pred[slicer]  # Removing missing dates
                # Handle if simulation is shorter than the observation period --> choose shorter period
                if pred.index[-1] < pd.to_datetime(period[1]):
                    Q_pred = pred['streamflow'][period[0]:pred.index[-1]]
                    Q_obs = observ[Q_field][period[0]:pred.index[-1]]
                    print(f'Warning: Simulation {idx} ends earlier than the defined ending date')
                    print('Analyzing to {}-{}-{} only'.format(pred.index[-1].year,pred.index[-1].month,pred.index[-1].day))

                    end_period = pred.index[-1]
                else:
                    Q_pred = pred['streamflow'][period[0]:period[1]]
                    Q_obs = observ[Q_field][period[0]:period[1]]
                    end_period = period[1]
                    
                for fun in obj_funs:
                    self.analyzing_param[fun][idx-1] = getattr(rhessys_cluster, fun)(Q_obs, Q_pred)
                for col in cols:
                    # print(f'  Calculating col {col}', end="\r", flush=True)
                    self.analyzing_param[col][idx-1] = np.mean(pred[col][period[0]:end_period])
        
        self.analyzing_param.to_csv(f'{self.workdir}/{self.outputCsvName}_round{self.round}_stat.csv', index=False)
        print('Statistics are saved to',f'{self.workdir}/{self.outputCsvName}_round{self.round}_stat.csv','\nOr can be seen by your_cluster_name.analyzing_param')
        
        # return self.analyzing_param
    
    def KclusterSampling(self, 
                obj_fun,
                threshold, 
                method='greater',
                stat_path=None,
                kmeans_kwargs = {'init': 'random', 
                                 'n_init':10, 
                                 'max_iter':300, 
                                 'random_state':888}):
        
        
        self.analyzing_param=[]
        print(len(self.analyzing_param))
        if len(self.analyzing_param) == 0:
            analyzing_param = pd.read_csv(stat_path)
            print(analyzing_param.head())
        else: analyzing_param = self.analyzing_param
        
        # print(analyzing_param.head())

        if method == 'greater':
            temp = analyzing_param[analyzing_param[obj_fun] >= threshold][self.param_names]
        else:
            temp = analyzing_param[analyzing_param[obj_fun] <= threshold][self.param_names]

        if len(temp) < 0.1*len(analyzing_param):
            print("Threshold is too strict to perform K clustering with only {} points".format(len(temp)))
            if method == 'greater':
                sorting = False
            else:
                sorting = True
            
            temp = analyzing_param.sort_values(by=obj_fun, ascending=sorting).iloc[:int(0.1*len(analyzing_param)),:][self.param_names]
            print("Increasing sample to 10% of the simulations {}/{}".format(int(0.1*len(analyzing_param)),len(analyzing_param)))
        
        # Perform K clustering analysis
        silhouette_coef = []

        for k in range(2,8):
            kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
            kmeans.fit(temp)
            silhouette_coef.append(silhouette_score(temp, kmeans.labels_))
        
        opt_nodes = np.argmax(silhouette_coef)+2
        if opt_nodes <= 3:
            opt_nodes = 4
            print(f'Only {opt_nodes} clusters found, increase to 4')
        else:
            print(f"Found {opt_nodes} clusters ...")
        
        kmeans = KMeans(n_clusters=opt_nodes, **kmeans_kwargs)

        df_list = []

        temp['kmean_group'] = kmeans.fit(temp).labels_
        cluster_mean = temp.groupby('kmean_group').mean()
        cluster_std = temp.groupby('kmean_group').std()


        if opt_nodes  == 4:
            sample_size = 150
            print(f'Creating {sample_size} for each node.')
        else:
            sample_size = int(1000/opt_nodes)
            print(f'Creating {sample_size} for each node.')

        for i in range(len(cluster_mean)):
            df=pd.DataFrame()
            # print(i)
            for col in self.param_names:
                df[col] = np.random.normal(loc=cluster_mean[col][i], 
                                           scale=cluster_std[col][i], 
                                           size=sample_size)
                
                df[col][df[col]<0] = 0.00001     # Change to 0.00001 if cluster is smaller than 0 --> no physical meaning
            
            df_list.append(df)
        new_param = pd.concat(df_list).reset_index(drop=True)
        new_param['index'] = new_param.index + 1

        new_param.to_csv(f'{self.output_folder}/{self.outputCsvName}_kcluster_{self.round+1}.csv', index=False)
        print('Kmeans cluster parameters saved to',f'{self.output_folder}/{self.outputCsvName}_kcluster_{self.round+1}.csv')
        self.new_param = new_param

        # Update template
        print('Template file is updated, "round" increased to', self.round+1)
        self.template['Value'][self.template['augName']=='round'] = self.round + 1
        self.template.to_csv(self.template_path, index=False)
        # return new_param
    
    def Jobfiles_Kcluster(self, submit=False):
        ##########
        ## Submit jobs to UVA Rivanna. Requires:
        ##     1. path_para_sample: path of the csv file with parameter sets
        ##     2. allocation: allocation name on Rivanna
        ## Return:
        ##     a list of lines for parameters
        ##########
        
        if len(self.new_param) < 1:
            raise Exception('No new parameters generated, run ".KclusterSampling()" first.')

        # Step 2: Create job script file for each line in the parameter file
        for idx in range(len(self.new_param)):
        # for idx in range(1):
            cmd_line = ''

            para_line = self.new_param.loc[idx]

            para_name = []
            for i in range(len(para_line)):
                if para_line.index[i] == 'index':
                    continue

                if para_line.index[i][:-1] not in para_name:
                    cmd_line += '-{} {} '.format(para_line.index[i][:-1], para_line[i])
                    para_name.append(para_line.index[i][:-1])
                else:
                    cmd_line += str(para_line[i]) + ' '

            self.new_lines.append(cmd_line[:-1])
            
            for idx, line in enumerate(self.new_lines):
            # Set the idx starts at 1, not 0
                idx = idx + 1
                job_path = f'{self.workdir}/jobfiles/job_{idx}.job'
                with open(job_path,'w') as f:
                    f.writelines('#!/bin/bash\n')
                    f.writelines('#SBATCH --partition=standard\n')
                    f.writelines('#SBATCH --ntasks=1\n')
                    f.writelines(f'#SBATCH --mem={self.memSize}\n')
                    f.writelines(f'#SBATCH -t {self.timeHPC}\n')   # Change if simulation takes more than 10 hours
                    f.writelines('#SBATCH --output=/dev/null\n')
                    f.writelines('#SBATCH --error=/dev/null\n')
                    f.writelines(f'#SBATCH --job-name=rs{idx}\n')
                    f.writelines(f'#SBATCH -A {self.allocationHPC}\n')
                    # f.writelines(f'#SBATCH --mail-user={computing_id}@virginia.edu\n')
                    # f.writelines(f'#SBATCH --mail-type=END\n')

                    f.writelines('module purge\n')
                    f.writelines('module load singularity\n')

                    f.writelines(f'cd {self.workdir}\n')


                    f.writelines(f'{self.rhessysExecutable} -st {self.startDate} -ed {self.endDate} {self.options} '+
                            f'-t {self.tecfile} -w {self.worldfile} -whdr {self.worldfile}.hdr ' +
                            f'-r {self.flowtable} -pre {self.output_folder}/{self.outputPrefix}{idx} ')

                    f.writelines(line)
            
                if submit: os.system(f"sbatch {job_path}")
                    # print(f'Simulation {idx} is submitted.', end='\r')

    def NSE(obs, pred):
        return 1 - np.sum((obs - pred)**2) / np.sum((obs - np.mean(obs))**2)
    
    def rmse(obs, pred):
        return np.mean(np.sqrt((obs - pred)**2))

    def r2(obs, pred):
        return np.corrcoef(obs, pred)[0,1]**2
        

