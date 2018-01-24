import os.path
import scipy.io
import pandas as pd
import numpy as np
import re
import glob

def get_animal_prefix(fileroot):
    # Assumes a "task" file in the animal directory
    anim_prefix = os.path.split(os.path.normpath(fileroot))[1].lower();
    # deals with Windows naming bug:
    if anim_prefix == 'con_':
        anim_prefix = 'con'
    filename = "{}*.mat".format(anim_prefix)
    if not glob.glob(os.path.join(fileroot,filename)) :
        anim_prefix = anim_prefix.title()
        filename = "{}*.mat".format(anim_prefix)
        if not glob.glob(os.path.join(fileroot,filename)) :
            return ""

    return anim_prefix


def load_task(fileroot, day=None, verbose=1):
    anim_prefix = get_animal_prefix(fileroot);

    if day is None :
        all_tasks= pd.DataFrame()
        file_list = []
        day_list = []
        for file in os.listdir(fileroot):
            m = re.match("{}task([0-9]+)\.mat".format(anim_prefix), file, re.IGNORECASE)
            if m:
                dk = int(m.group(1))
                all_tasks = all_tasks.append(load_task(fileroot, day=dk, verbose=verbose), ignore_index=True, verify_integrity=True)

        return all_tasks

    else :
        useful_fields = ['type','exposure','environment','description',
                         'sleepnum','dailyexposure','exposureday', 'experimentday',
                         'tracksexperienced', 'dailytracksexperienced', 'linearcoord']

        potential_fields = useful_fields + ['runbefore', 'runafter']

        filename = "{}task{:02d}.mat".format(anim_prefix, day)

        if verbose:
            print("Loading " + filename)
        mat = scipy.io.loadmat(os.path.join(fileroot,filename),
                               struct_as_record=False, squeeze_me=True)

        task = []
        data = mat['task']
        # Detect whether we need to parse a cell array by day (not for some animals on day 1)
        # Either we have an ndarray of mixed ndarray/scipy-structs or an ndarray (days) of ndarrays
        #   where the content will be in the day-th ndarray.
        if isinstance(data, np.ndarray):
            if all(isinstance(d, np.ndarray) for d in data):
                data = data[day-1]

        for epidx, da in enumerate(data):
            task.append({})
            task[epidx]['Epoch'] = epidx
            task[epidx]['Day'] = day-1

            if isinstance(da, np.ndarray):
                if (da.size == 0) :
                    continue;
            # First check to see if unexpected fields exist
            if (verbose > 1) :
                unexpected_fields = list(set(da._fieldnames) - set(potential_fields))
                if unexpected_fields :
                    print("Unexpected fields: ", unexpected_fields)

            # Next, load useful fields into dictionary
            for field in useful_fields :
                if (hasattr(da,field)):
                    task[epidx][field] = getattr(da,field);

        return pd.DataFrame(task, columns=['Day','Epoch']+useful_fields)

def load_pos(fileroot, day=None, verbose=1, day_list=None):
    anim_prefix = get_animal_prefix(fileroot);

    if day is None :
        all_pos= pd.DataFrame()
        if day_list is None:
            day_list = []
            for file in os.listdir(fileroot):
                # NOTE THAT WE'LL ONLY LOAD DAYS FOR WHICH THERE IS A TASK!!
                m = re.match("{}task([0-9]+)\.mat".format(anim_prefix), file, re.IGNORECASE)
                if m:
                    day_list.append(int(m.group(1)))
        for dk in day_list:
            all_pos = all_pos.append(load_pos(fileroot, day=dk, verbose=verbose), ignore_index=True, verify_integrity=True)

        return all_pos

    else :
        filename = "{}pos{:02d}.mat".format(anim_prefix, day)
        if verbose:
            print("Loading " + filename)
        mat = scipy.io.loadmat(os.path.join(fileroot,filename),
                               struct_as_record=False, squeeze_me=True)

        pos = []
        data = mat['pos']
        # Detect whether we need to parse a cell array by day (not for some animals on day 1)
        # Either we have an ndarray of mixed ndarray/scipy-structs or an ndarray (days) of ndarrays
        #   where the content will be in the day-th ndarray.
        if isinstance(data, np.ndarray):
            if all(isinstance(d, np.ndarray) for d in data):
                data = data[day-1]

        data_fields = ['time', 'x', 'y', 'dir', 'vel']
        default_data_fields = 'time x y dir vel'
        default_attrs = ['arg', 'descript', 'fields', 'cmperpixel']

        for epidx, da in enumerate(data):
            pos.append({})
            pos[epidx]['Epoch'] = epidx
            pos[epidx]['Day'] = day-1

            if isinstance(da, np.ndarray):
                if (da.size == 0) :
                    continue;
                else:
                    print("Unexpected ndarray in struct.")
            else :
                # Next, load useful fields into dictionary
                for attr in default_attrs :
                    if (hasattr(da,attr)):
                        pos[epidx][attr] = getattr(da,attr);

                # First check to see if unexpected fields exist
                if not (getattr(da,'fields') >= default_data_fields) :
                    print("Unexpected data fields ", getattr(da,'fields'))
                else :
                    datamat = getattr(da,'data')
                    for idx, field in enumerate(data_fields) :
                        if (datamat.ndim == 1) :
                            pos[epidx][field] = datamat[idx]
                        else :
                            pos[epidx][field] = datamat[:,idx]

        return pd.DataFrame(pos, columns=['Day','Epoch']+data_fields+default_attrs)


def load_spikes(fileroot, day=None, verbose=1) :
    anim_prefix = get_animal_prefix(fileroot);

    if day is None :
        all_spikes = pd.DataFrame()
        file_list = []
        day_list = []
        for file in os.listdir(fileroot):
            # NOTE THAT WE'LL ONLY LOAD DAYS FOR WHICH THERE IS A TASK!!
            m = re.match("{}task([0-9]+)\.mat".format(anim_prefix), file, re.IGNORECASE)
            if m:
                dk = int(m.group(1))
                all_spikes = all_spikes.append(load_spikes(fileroot, dk, verbose=verbose), ignore_index=True, verify_integrity=True)

        #task = task.sort_values(by=['Day','Epoch'])

        all_spikes = all_spikes.sort_values(by=['Day','Epoch','Tetrode','Cell'])
        cols = all_spikes.columns.tolist()
        newcols = ['Day','Epoch','Tetrode','Cell']
        newcols = newcols + list(set(cols) - set(newcols))

        return all_spikes[newcols]

    else :
        filename = "{}spikes{:02d}.mat".format(anim_prefix, day)
        if verbose:
            print("Loading " + filename)
        mat = scipy.io.loadmat(os.path.join(fileroot,filename),
                               struct_as_record=False, squeeze_me=True)

        spikedata = []
        # Spike files contain data for all epochs, tetrodes, and cells in a day
        # Some epochs have fields: ['data', 'descript', 'fields', 'depth', 'spikewidth', 'timerange']
        # but some epochs are missing 'spikewidth'
        data = mat['spikes']
        if (day > 1):
            data = data[day-1]
        for epidx, da in enumerate(data):
            #print(type(da))
            for tetidx, te in enumerate(da):
                if isinstance(te, np.ndarray) :
                    for cellidx, cell in enumerate(te):
                        spikedata.append({})
                        spikedata[-1]['Day'] = day - 1
                        spikedata[-1]['Epoch'] = epidx
                        neuron_idx = (day-1, epidx, tetidx, cellidx)
                        spikedata[-1]['Tetrode'] = tetidx
                        spikedata[-1]['Cell'] = cellidx
                        if (isinstance(cell, np.ndarray)) :
                            continue # No data for this tetrode/cell combo
                        spikedata[-1].update({f: getattr(cell,f) for f in cell._fieldnames})
                        if cell.data.size == 0 :
                            spikedata[-1]['spiketimes'] = cell.data # this is an empty array
                        else :
                            if (cell.data.ndim == 1) :
                                spikedata[-1]['spiketimes'] = cell.data[0]
                            else :
                                spikedata[-1]['spiketimes'] = cell.data[:,0]

                else: # Single cell on tetrode
                    spikedata.append({})
                    spikedata[-1]['Day'] = day - 1
                    spikedata[-1]['Epoch'] = epidx
                    neuron_idx = (day-1, epidx, tetidx, 0)
                    spikedata[-1]['Tetrode'] = tetidx
                    spikedata[-1]['Cell'] = 0
                    spikedata[-1].update({f: getattr(te,f) for f in te._fieldnames})
                    if te.data.size == 0 :
                        spikedata[-1]['spiketimes'] = te.data # this is an empty array
                    else :
                        if (te.data.ndim == 1) :
                            spikedata[-1]['spiketimes'] = te.data[0]
                        else :
                            spikedata[-1]['spiketimes'] = te.data[:,0]

        return spikedata


def load_cellinfo(fileroot, verbose=1) :
    anim_prefix = get_animal_prefix(fileroot);

    filename = "{}cellinfo.mat".format(anim_prefix)
    if verbose:
        print("Loading " + filename)

    mat = scipy.io.loadmat(os.path.join(fileroot,filename),
                           struct_as_record=False, squeeze_me=True)
    data = mat['cellinfo']
    cellinfo = {}
    idx_columns = ['Day', 'Epoch', 'Tetrode','Cell']
    for dayidx, da in enumerate(data) :
        for epidx, ep in enumerate(da):
            for tetidx, te in enumerate(ep):
                if isinstance(te, np.ndarray) :
                    for cellidx, cell in enumerate(te):
                        neuron_idx = (dayidx, epidx, tetidx, cellidx)
                        df = dict(zip(idx_columns,list(neuron_idx)))
                        if (isinstance(cell, np.ndarray)) :
                            cellinfo[str(neuron_idx)] = df
                            continue # No data for this tetrode/cell combo
                        ci = {f: getattr(cell,f) for f in cell._fieldnames}
                        df.update(ci)
                        cellinfo[str(neuron_idx)] = df
                else: # Single cell on tetrode
                    neuron_idx = (dayidx, epidx, tetidx, 0)
                    ci = {f: getattr(te,f) for f in te._fieldnames}
                    df = dict(zip(idx_columns,list(neuron_idx)))
                    df.update(ci)
                    cellinfo[str(neuron_idx)] = df
    cellinfodf = pd.DataFrame.from_dict(cellinfo,orient='index')
    return cellinfodf, data

def load_data(fileroot, day=None, epoch=None, tetrode=None, datatype='eeg', version='old', verbose=1):
    anim_prefix = get_animal_prefix(fileroot);

    if (datatype=='eeg') :
        filename = "{}eeg{:02d}-{}-{:02d}.mat".format(anim_prefix, day, epoch, tetrode)
        if verbose:
            print("Loading " + filename)
        mat = scipy.io.loadmat(os.path.join(fileroot,'EEG',filename),
                               struct_as_record=False, squeeze_me=True)
        data = mat[datatype]
        if (version=='new'):
            if (day > 1):
                data = data[day-1]
            if (epoch > 1):
                data = data[epoch-1]
            if (tetrode > 1):
                data = data[tetrode-1]
        return data
    elif (datatype=='tetinfo') :
        filename = "{}{}.mat".format(anim_prefix, datatype)
        if verbose:
            print("Loading " + filename)
        mat = scipy.io.loadmat(os.path.join(fileroot,filename),
                               struct_as_record=False, squeeze_me=True)
        data = mat[datatype]
        tetinfo = {}
        idx_columns = ['Day', 'Epoch', 'Tetrode']
        for dayidx, da in enumerate(data) :
            for epidx, ep in enumerate(da):
                for tetidx, te in enumerate(ep):
                  #if isinstance(te, np.ndarray) :
                      tetrode_idx = (dayidx, epidx, tetidx)
                      df = dict(zip(idx_columns,list(tetrode_idx)))
                      if (isinstance(te, np.ndarray)) :
                          tetinfo[str(tetrode_idx)] = df
                          continue # No data for this tetrode/cell combo
                      ti = {f: getattr(te,f) for f in te._fieldnames}
                      df.update(ti)
                      tetinfo[str(tetrode_idx)] = df
        tetinfodf = pd.DataFrame.from_dict(tetinfo,orient='index')
        return tetinfodf, data
    elif (datatype=='cellinfo') :
        return load_cellinfo(fileroot, verbose=verbose)

    elif (datatype=='task') :
        if day is None:
            return load_task(fileroot, verbose=verbose)
        else :
            return load_single_task_file(fileroot, day=day, verbose=verbose)

    elif (datatype=='spikes') :
        return load_spikes(fileroot, day=day, verbose=verbose)

    elif (datatype=='pos') :
        return load_pos(fileroot, day=day, verbose=verbose)

    elif (datatype=='rawpos') :
        x=0
    else :
        raise ValueError('datatype is not handled')




